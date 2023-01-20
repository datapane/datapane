# Copyright 2020 StackHut Limited (trading as Datapane)
# SPDX-License-Identifier: Apache-2.0
import sys
from pathlib import Path

try:
    from ._version import __rev__
except ImportError:
    # NOTE - could use subprocess to get from git?
    __rev__ = "local"

__version__ = "0.15.6"


# Public API re-exports
from .client import (  # isort:skip  otherwise circular import issue
    IN_PYTEST,
    DPClientError,
    DPMode,
    enable_logging,
    get_dp_mode,
    set_dp_mode,
)  # isort:skip  otherwise circular import issue

from .app.server import serve
from .blocks import (
    HTML,
    Attachment,
    BigNumber,
    Choice,
    Code,
    Controls,
    DataTable,
    Date,
    DateTime,
    Divider,
    Embed,
    Empty,
    File,
    Formula,
    Function,
    Group,
    Media,
    MultiChoice,
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
    wrap_block,
)
from .cloud_api import App, AppFormatting, AppWidth
from .cloud_api import File as CloudFile
from .cloud_api import FontChoice, TextAlignment, hello_world, login, logout, ping, signup
from .processors import build, save_report, stringify_report, upload
from .view import View

# Other useful re-exports
from . import builtins  # isort:skip  otherwise circular import issue

X = wrap_block

__all__ = [
    "App",
    "AppFormatting",
    "AppWidth",
    "DPClientError",
    "CloudFile",
    "FontChoice",
    "TextAlignment",
    "builtins",
    "hello_world",
    "login",
    "logout",
    "ping",
    "signup",
    "enable_logging",
    "load_params_from_command_line",
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
    "Divider",
    "Embed",
    "Group",
    "Text",
    "Toggle",
    "Controls",
    "Function",
    "View",
    "upload",
    "save_report",
    "serve",
    "build",
    "stringify_report",
    "X",
    "Range",
    "Switch",
    "TextBox",
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


def load_params_from_command_line() -> None:
    """Call this from your own scripts to read any CLI parameters into the global Params object"""
    # from .client.utils import parse_command_line
    #
    # config = parse_command_line()
    # Params.replace(config)
    pass
