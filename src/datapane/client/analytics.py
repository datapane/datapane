"""This module provides a simple interface to capture analytics data"""
import platform
from contextlib import suppress
from functools import wraps
from pathlib import Path

import posthog

from datapane import _IN_DPSERVER, _IN_PYTEST, _USING_CONDA, ON_DATAPANE, __version__, log
from datapane.client.utils import is_jupyter

from . import config as c

posthog.api_key = "phc_wxtD2Qxd3RMlmCCSYDC0rW1We22yh06cMcffnfSJTZy"
posthog.host = "https://events.datapane.com/"
_NO_ANALYTICS_FILE: Path = c.APP_DIR / "no_analytics"


def is_analytics_disabled() -> bool:
    """Determine the initial state for analytics if not already set"""
    # disable if globally disabled or in certain envs
    if _NO_ANALYTICS_FILE.exists() or ON_DATAPANE or _IN_PYTEST or _IN_DPSERVER:
        log.debug("Analytics disabled")
        return True
    return False


_NO_ANALYTICS: bool = is_analytics_disabled()


def capture(event: str, **properties) -> None:
    # Used for capturing generic events with properties
    if _NO_ANALYTICS:
        return None
    config = c.get_config()

    # run identify on first action, (NOTE - don't change the order here)
    if not config.completed_action:
        config.completed_action = True
        identify(config.session_id)
        config.save()

    properties.update(source="cli", dp_version=__version__, in_jupyter=is_jupyter(), using_conda=_USING_CONDA)

    with suppress(Exception):
        posthog.capture(config.session_id, event, properties)


def identify(session_id: str, **properties) -> None:
    properties.update(
        os=platform.system(),
        python_version=platform.python_version(),
        dp_version=__version__,
        in_jupyter=is_jupyter(),
        using_conda=_USING_CONDA,
    )
    with suppress(Exception):
        posthog.identify(session_id, properties)
    # Also generate a CLI identify event to help disambiguation
    capture("CLI Identify")


# def capture_init(config: c.Config) -> None:
#     # Generates an identify event on init
#     if _NO_ANALYTICS:
#         return None
#     identify(config.session_id)


def capture_event(name: str):
    # Decorator used for capturing events without any properties
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            finally:
                capture(name)

        return wrapper

    return decorator
