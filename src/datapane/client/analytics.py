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
    with suppress(Exception):
        posthog.capture(config.session_id, event, properties)


def identify(session_id: str, properties: Optional[dict] = None):
    properties = properties or {}
    properties.update(os=platform.system(), python_version=platform.python_version(), dp_version=datapane.__version__)
    with suppress(Exception):
        posthog.identify(session_id, properties)


def capture_init(config: c.Config):
    # Generates an identify event on init
    if not config.analytics:
        return
    identify(config.session_id)


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
