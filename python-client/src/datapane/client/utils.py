from __future__ import annotations

import argparse
import enum
import logging
import logging.config
import os
import string
import sys
import typing as t
from distutils.util import strtobool
from typing import Iterator, Tuple

import click

from datapane.common import JDict

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
    from .analytics import user_properties

    fields = user_properties()

    # Known dependencies
    import numpy as np
    import pandas as pd
    import pyarrow as pa

    fields["pandas_version"] = pd.__version__
    fields["numpy_version"] = np.__version__
    fields["pyarrow_version"] = pa.__version__

    print("Datapane Debugging Info")
    print("(please copy/paste into a GitHub Issue at https://github.com/datapane/datapane/issues)")
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


################################################################################
# cmd line parsing
def process_cmd_param_vals(params: Tuple[str, ...]) -> JDict:
    """Convert a list of k=v to a typed JSON dict"""

    def convert_param_val(x: str) -> t.Union[int, float, str, bool]:
        # TODO - this can be optimised / cleaned-up
        try:
            return int(x)
        except ValueError:
            try:
                return float(x)
            except ValueError:
                try:
                    return bool(strtobool(x))
                except ValueError:
                    return x

    def split_param(xs: Tuple[str, ...]) -> Iterator[t.Tuple[str, str]]:
        err_msg = "'{}', should be name=value"
        for x in xs:
            try:
                k, v = x.split("=", maxsplit=1)
            except ValueError:
                raise click.BadParameter(err_msg.format(x))
            if not k or not v:
                raise click.BadParameter(err_msg.format(x))
            yield (k, v)

    return {k: convert_param_val(v) for (k, v) in split_param(params)}


def parse_command_line() -> t.Dict[str, t.Any]:
    """Called in library mode to read any datapane CLI parameters"""
    parser = argparse.ArgumentParser(
        description="Datapane additional args",
        conflict_handler="resolve",
        add_help=False,
    )
    parser.add_argument(
        "--parameter",
        "-p",
        action="append",
        help="key=value parameters to pass into dp.Params",
        default=[],
    )

    (dp_args, remaining_args) = parser.parse_known_args()
    # reset sys.argv without the dp params for parsing by the user
    exe_name = sys.argv.pop(0)
    sys.argv.clear()
    sys.argv.append(exe_name)
    sys.argv.extend(remaining_args)

    return process_cmd_param_vals(dp_args.parameter)


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
