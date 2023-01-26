"""This module provides a simple interface to capture analytics data"""
import atexit
import platform
import queue
import threading
from contextlib import suppress
from functools import wraps
from pathlib import Path
from time import sleep, time
from typing import Any, Callable, Dict, Optional, TypeVar, cast

import posthog

from datapane import _IN_DPSERVER, _IN_PYTEST, _USING_CONDA, ON_DATAPANE, __version__, log
from datapane.client.environment import environment

from . import config as c

posthog.sync_mode = True
posthog.api_key = "phc_wxtD2Qxd3RMlmCCSYDC0rW1We22yh06cMcffnfSJTZy"
posthog.host = "https://events.datapane.com/"
_NO_ANALYTICS_FILE: Path = c.APP_DIR / "no_analytics"
MAX_QUEUE_SIZE = 250
QUEUE_TIMEOUT = 10


class Consumer(threading.Thread):
    """Maintains and consumes queue for posthog requests"""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw, name="Analytics event consumer", daemon=True)
        self.queue = queue.Queue(MAX_QUEUE_SIZE)

    def run(self):
        """
        Run the next function at the start of the queue whenever the queue is non-empty.
        Note `self.queue.get()` is blocking while the queue is empty
        """
        while True:
            (f, args) = self.queue.get()
            with suppress(Exception):
                f(*args)
            self.queue.task_done()

    def send(self, f: Callable[..., None], args: Any):
        """Add analytics function and arguments to the thread queue"""
        self.queue.put((f, args))

    def join_queue(self):
        """
        Poll `queue.unfinished_tasks` until a max time is reached,
        rather than calling `queue.join`, as `queue.Queue.join` has no `timeout` parameter
        """
        end_time = time() + QUEUE_TIMEOUT
        while self.queue.unfinished_tasks and time() < end_time:
            sleep(1)


def is_analytics_disabled() -> bool:
    """Determine the initial state for analytics if not already set"""
    # disable if globally disabled or in certain envs
    if _NO_ANALYTICS_FILE.exists() or ON_DATAPANE or _IN_PYTEST or _IN_DPSERVER:
        log.debug("Analytics disabled")
        return True
    return False


def user_properties() -> Dict:
    """User properties to be added on `identify`, and amended on `capture`"""
    return dict(
        os=platform.system(),
        python_version=platform.python_version(),
        dp_version=__version__,
        environment_type=environment.name,
        in_jupyter=environment.is_notebook_environment,
        using_conda=_USING_CONDA,
    )


_NO_ANALYTICS: bool = is_analytics_disabled()

_consumer = None


def start_queue():
    global _consumer
    _consumer = Consumer()
    _consumer.start()


if not _NO_ANALYTICS:
    start_queue()


def capture(event: str, config: Optional[c.Config] = None, **properties) -> None:
    # Used for capturing generic events with properties
    if _NO_ANALYTICS:
        return None
    config = config or c.get_config()

    properties.update(
        {
            "source": "cli",
            "dp_version": __version__,
            "environment_type": environment.name,
            "in_jupyter": environment.is_notebook_environment,
            "using_conda": _USING_CONDA,
            # Note "$" isn't a valid char in `dict(k=v)` keys
            "$set": user_properties(),
        }
    )

    _consumer.send(posthog.capture, args=[config.session_id, event, properties])


# def identify(config: c.Config, **properties) -> None:
#     properties.update(user_properties())
#     _consumer.send(posthog.identify, args=[config.session_id, properties])


# def capture_init(config: c.Config) -> None:
#     # Generates an identify event on init
#     if _NO_ANALYTICS:
#         return None
#     identify(config.session_id)

# From the mypy docs ...https://mypy.readthedocs.io/en/stable/generics.html#declaring-decorators
F = TypeVar("F", bound=Callable[..., Any])


def capture_event(name: str) -> Callable[[F], F]:
    """Decorator to capture 'name' as analytics event when the function is called"""

    def _decorator(func: F) -> F:
        @wraps(func)
        def _wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            finally:
                capture(name)

        return cast(F, _wrapper)

    return _decorator


@atexit.register
def finish_queue():
    """Block main thread until analytics queue is clear"""
    global _consumer
    if _consumer is not None:
        _consumer.join_queue()
    _consumer = None
