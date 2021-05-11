"""This module provides a simple interface to capture analytics data"""
import platform
from contextlib import suppress
from functools import wraps
from typing import Optional

import posthog

import datapane

from . import config as c

POSTHOG_API_KEY = "wgDS94MS51wVhjXKouBmKwb_I3s8rK0ojtLJL4qVH7w"
POSTHOG_HOST = "https://numbers.datapane.com/"

posthog.api_key = POSTHOG_API_KEY
posthog.host = POSTHOG_HOST


def capture(event: str, properties: Optional[dict] = None):
    # Used for capturing generic events with properties
    config = c.get_config()
    if not config.analytics:
        return None
    t_user_id = config.session_id
    with suppress(Exception):
        posthog.capture(t_user_id, event, properties)


def _identify(distinct_id: str, properties: Optional[dict] = None):
    properties = properties or {}
    properties.update(os=platform.system(), python_version=platform.python_version(), dp_version=datapane.__version__)
    with suppress(Exception):
        posthog.identify(distinct_id, properties)


def capture_init():
    # Generates an identify event on init

    config = c.get_config()
    if not config.analytics:
        return

    distinct_id = config.session_id
    _identify(distinct_id)


def capture_event(name: str):
    # Decorator used for capturing events without any properties
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            capture(name)
            f(*args, **kwargs)

        return wrapper

    return decorator
