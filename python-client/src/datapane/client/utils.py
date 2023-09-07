from __future__ import annotations

import enum
import logging
import logging.config
import os
import string
import sys
import typing as t

##############
# Client constants
TEST_ENV = bool(os.environ.get("DP_TEST_ENV", ""))
IN_PYTEST = "pytest" in sys.modules  # and TEST_ENV
# we're running on datapane platform
ON_DATAPANE: bool = "DATAPANE_ON_DATAPANE" in os.environ


################################################################################
# Logging
# export the application logger at WARNING level by default
log: logging.Logger = logging.getLogger("datapane")
if log.level == logging.NOTSET:
    log.setLevel(logging.WARNING)


_have_setup_logging: bool = False


def _setup_dp_logging(verbosity: int = 0, logs_stream: t.TextIO = None) -> None:
    global _have_setup_logging

    log_level = "WARNING"
    if verbosity == 1:
        log_level = "INFO"
    elif verbosity > 1:
        log_level = "DEBUG"

    # don't configure global logging config when running as a library
    if get_dp_mode() == DPMode.LIBRARY:
        log.warning("Configuring datapane logging in library mode")
        # return None

    # TODO - only allow setting once?
    if _have_setup_logging:
        log.warning(f"Reconfiguring datapane logger when running as {get_dp_mode().name}")
        # raise AssertionError("Attempting to reconfigure datapane logger")
        return None

    # initial setup via dict-config
    _have_setup_logging = True
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "colored": {
                "()": "colorlog.ColoredFormatter",
                "format": "[%(blue)s%(asctime)s%(reset)s] [%(log_color)s%(levelname)-5s%(reset)s] %(message)s",
                "datefmt": "%H:%M:%S",
                "reset": True,
                "log_colors": {
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                },
                "style": "%",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "colored",
                "stream": logs_stream or sys.stderr,
            }
        },
        "loggers": {"datapane": {"level": log_level, "propagate": True}},
        # only show INFO for anything else
        "root": {"handlers": ["console"], "level": "INFO"},
    }
    logging.config.dictConfig(log_config)


def enable_logging():
    """Enable logging for debug purposes"""
    _setup_dp_logging(verbosity=2)


def print_debug_info():
    """Print useful debugging information"""
    fields = dict()

    # Known dependencies
    import numpy as np
    import pandas as pd
    import pyarrow as pa

    fields["pandas_version"] = pd.__version__
    fields["numpy_version"] = np.__version__
    fields["pyarrow_version"] = pa.__version__

    print("Datapane Debugging Info")
    for (k, v) in fields.items():
        print(f"{k}: {v}")


################################################################################
# Output
def open_in_browser(url: str):
    """Open the given URL in the user's browser"""
    from datapane.ipython.environment import get_environment

    environment = get_environment()

    # TODO - this is a bit of a hack, but works for now. JupyterLab (Codespaces) doesn't support webbrowser.open.
    if environment.is_notebook_environment and not environment.can_open_links_from_python:
        ip = environment.get_ipython()
        ip.run_cell_magic("javascript", "", f'window.open("{url}", "_blank")')
    else:
        import webbrowser

        webbrowser.open(url, new=1)


class MarkdownFormatter(string.Formatter):
    """Support {:l} and {:cmd} format fields"""

    in_jupyter: bool

    def __init__(self, in_jupyter: bool):
        self.in_jupyter = in_jupyter
        super().__init__()

    def format_field(self, value: t.Any, format_spec: str) -> t.Any:
        if format_spec.endswith("l"):
            if self.in_jupyter:
                value = f"<a href='{value}' target='_blank'>here</a>"
            else:
                value = f"at {value}"
            format_spec = format_spec[:-1]
        elif format_spec.endswith("cmd"):
            value = f"!{value}" if self.in_jupyter else value
            format_spec = format_spec[:-3]
        return super().format_field(value, format_spec)


def display_msg(text: str, **params: str):
    from datapane.ipython.environment import get_environment

    environment = get_environment()

    msg = MarkdownFormatter(environment.is_notebook_environment).format(text, **params)
    if environment.is_notebook_environment:
        from IPython.display import Markdown, display

        display(Markdown(msg))
    else:
        print(msg)


############################################################
class DPMode(enum.Enum):
    """DP can operate in multiple modes as specified by this Enum"""

    SCRIPT = enum.auto()  # run from the cmd-line
    LIBRARY = enum.auto()  # imported into a process
    FRAMEWORK = enum.auto()  # running dp-runner


# default in Library mode
__dp_mode: DPMode = DPMode.LIBRARY


def get_dp_mode() -> DPMode:
    global __dp_mode
    return __dp_mode


def set_dp_mode(dp_mode: DPMode) -> None:
    global __dp_mode
    __dp_mode = dp_mode
