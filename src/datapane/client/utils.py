import argparse
import string
import sys
import typing as t
from distutils.util import strtobool
from typing import Iterator, Tuple

import click

from datapane.common import DPError, JDict


################################################################################
# Built-in exceptions
class IncompatibleVersionError(DPError):
    ...


class UnsupportedResourceError(DPError):
    ...


class ReportTooLargeError(DPError):
    ...


class InvalidTokenError(DPError):
    ...


class UnsupportedFeatureError(DPError):
    ...


class InvalidReportError(DPError):
    ...


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
        return get_ipython().__class__.__name__ == "ZMQInteractiveShell"  # noqa: F821
    except Exception:
        return False


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


################################################################################
# Misc
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

    def split_param(xs: Tuple[str]) -> Iterator[t.Tuple[str, str]]:
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
    """Called in library mode to pull any parameters into dp.Config"""
    parser = argparse.ArgumentParser(description="Datapane additional args", conflict_handler="resolve", add_help=False)
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
