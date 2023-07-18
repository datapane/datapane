# Copyright 2020 StackHut Limited (trading as Datapane)
# SPDX-License-Identifier: Apache-2.0
import sys
import typing as t
from pathlib import Path

try:
    from . import _version
except ImportError:
    # NOTE - could use subprocess to get from git?
    __rev__ = "local"
    __is_dev_build__ = True
else:
    __rev__ = _version.__rev__
    __is_dev_build__ = getattr(_version, "__is_dev_build__", False)
    del _version

__version__ = "0.16.5"


# Public API re-exports
from .client import (  # isort:skip  otherwise circular import issue
    IN_PYTEST,
    DPClientError,
    DPMode,
    enable_logging,
    print_debug_info,
    get_dp_mode,
    set_dp_mode,
)  # isort:skip  otherwise circular import issue

from .app.server import serve_app
from .blocks import (
    HTML,
    Attachment,
    BigNumber,
    Block,
    Choice,
    Code,
    Compute,
    Controls,
    DataTable,
    Date,
    DateTime,
    Dynamic,
    Embed,
    Empty,
    File,
    Form,
    Formula,
    Group,
    Media,
    MultiChoice,
    NumberBox,
    Page,
    Plot,
    Range,
    Select,
    SelectType,
    Swap,
    Switch,
    Table,
    Tags,
    TargetMode,
    Text,
    TextBox,
    Time,
    Toggle,
    Trigger,
    VAlign,
    wrap_block,
)
from .cloud_api import CloudReport
from .cloud_api import File as CloudFile
from .cloud_api import hello_world, login, logout, ping, signup
from .processors import (
    FontChoice,
    Formatting,
    TextAlignment,
    Width,
    build_report,
    save_report,
    stringify_report,
    upload_report,
)
from .view import App, Blocks, View

# Other useful re-exports
from . import builtins  # isort:skip  otherwise circular import issue

X = wrap_block

__all__ = [
    "App",
    "DPClientError",
    "CloudFile",
    "CloudReport",
    "builtins",
    "hello_world",
    "login",
    "logout",
    "ping",
    "signup",
    "enable_logging",
    "print_debug_info",
    "load_params_from_command_line",
    "Block",
    "Attachment",
    "BigNumber",
    "Empty",
    "DataTable",
    "Media",
    "Plot",
    "Table",
    "Select",
    "SelectType",
    "Formula",
    "HTML",
    "Code",
    "Embed",
    "Group",
    "Text",
    "Toggle",
    "Controls",
    "VAlign",
    "Compute",
    "Form",
    "Dynamic",
    "Blocks",
    "upload_report",
    "save_report",
    "serve_app",
    "build_report",
    "stringify_report",
    "X",
    "Range",
    "Switch",
    "TextBox",
    "NumberBox",
    "Choice",
    "MultiChoice",
    "Tags",
    "Date",
    "DateTime",
    "Time",
    "File",
    "Swap",
    "Trigger",
    "TargetMode",
    "Page",
    "View",
    "Width",
    "FontChoice",
    "Formatting",
    "TextAlignment",
]


script_name = sys.argv[0]
script_exe = Path(script_name).stem
by_datapane = False  # hardcode for now as not using legacy runner
if script_exe == "datapane" or script_name == "-m":  # or "pytest" in script_name:
    # argv[0] will be "-m" as client module as submodule of this module
    set_dp_mode(DPMode.SCRIPT)
elif by_datapane or script_exe == "dp-runner":
    set_dp_mode(DPMode.FRAMEWORK)
else:
    set_dp_mode(DPMode.LIBRARY)

# TODO - do we want to init only in jupyter / interactive / etc.
# only init fully in library-mode, as framework and app init explicitly
if get_dp_mode() == DPMode.LIBRARY and not IN_PYTEST:
    from .client.config import init

    init()


def load_params_from_command_line() -> t.Dict:
    """Call this from your own scripts to read any CLI parameters into the global Params object"""
    from .client.utils import log, parse_command_line

    config = parse_command_line()
    log.debug(config)
    # Params.replace(config)
    return config
