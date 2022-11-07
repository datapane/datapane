import os
import string
import sys
import typing as t

import click

from datapane.common import DPError


################################################################################
# Built-in exceptions
class IncompatibleVersionError(DPError):
    pass


class UnsupportedResourceError(DPError):
    pass


class ReportTooLargeError(DPError):
    pass


class InvalidTokenError(DPError):
    pass


class UnsupportedFeatureError(DPError):
    pass


class InvalidReportError(DPError):
    pass


class MissingCloudPackagesError(DPError):
    def __init__(self, *a, **kw):
        # quick hack until we setup a conda meta-package for cloud
        self.args = (
            "Cloud packages not found, please run `pip install datapane[cloud]` or `conda install -c conda-forge nbconvert flit-core`",
        )


################################################################################
# Output
def success_msg(msg: str):
    click.secho(msg, fg="green")


def failure_msg(msg: str, do_exit: bool = False):
    click.secho(msg, fg="red")
    if do_exit:
        ctx: click.Context = click.get_current_context(silent=True)
        if ctx:
            ctx.exit(2)
        else:
            exit(2)


def is_jupyter() -> bool:
    """Checks if inside ipython shell inside browser"""
    try:
        return get_ipython().__class__.__name__ == "ZMQInteractiveShell"  # type: ignore [name-defined]  # noqa: F821
    except Exception:
        return False


def get_environment_type() -> str:
    """Try and get the name of the IDE the script is running in"""
    if "PYCHARM_HOSTED" in os.environ:
        return "pycharm"
    if "google.colab" in sys.modules:
        return "colab"
    elif "VSCODE_PID" in os.environ:
        return "vscode"
    elif is_jupyter():
        return "jupyter"

    return "unknown"


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
    msg = MarkdownFormatter(is_jupyter()).format(text, **params)
    if is_jupyter():
        from IPython.display import Markdown, display

        display(Markdown(msg))
    else:
        print(msg)
