# Copyright 2020 StackHut Limited (trading as Datapane)
# SPDX-License-Identifier: Apache-2.0
import os
import sys
from pathlib import Path

try:
    from ._version import __rev__
except ImportError:
    # NOTE - could use subprocess to get from git?
    __rev__ = "local"

__version__ = "0.15.1"

_TEST_ENV = bool(os.environ.get("DP_TEST_ENV", ""))
_IN_PYTEST = "pytest" in sys.modules
_IN_DPSERVER = "dp" in sys.modules
# we're running on datapane platform
ON_DATAPANE: bool = "DATAPANE_ON_DATAPANE" in os.environ
_USING_CONDA = os.path.exists(os.path.join(sys.prefix, "conda-meta", "history"))


# Other useful re-exports
from .common.utils import _setup_dp_logging, enable_logging, log  # isort:skip  otherwise circular import issue

# Public API re-exports
from .client.api import (
    HTML,
    App,
    Attachment,
    BigNumber,
    Code,
    DataTable,
    Divider,
    Embed,
    Empty,
    Environment,
    File,
    FontChoice,
    Formula,
    Group,
    Media,
    Page,
    PageLayout,
    Params,
    Plot,
    Report,
    ReportFormatting,
    ReportWidth,
    Result,
    Run,
    Schedule,
    Select,
    SelectType,
    Table,
    Text,
    TextAlignment,
    Toggle,
    builtins,
    by_datapane,
    hello_world,
    login,
    logout,
    ping,
    template,
)
from .client.config import init
from .common.dp_types import DPMode, get_dp_mode, set_dp_mode

__all__ = [
    "HTML",
    "App",
    "Attachment",
    "BigNumber",
    "Code",
    "DataTable",
    "Divider",
    "Embed",
    "Empty",
    "Environment",
    "File",
    "FontChoice",
    "Formula",
    "Group",
    "Media",
    "Page",
    "PageLayout",
    "Params",
    "Plot",
    "Report",
    "ReportFormatting",
    "ReportWidth",
    "Result",
    "Run",
    "Schedule",
    "Select",
    "SelectType",
    "Table",
    "Text",
    "TextAlignment",
    "Toggle",
    "builtins",
    "by_datapane",
    "hello_world",
    "login",
    "logout",
    "ping",
    "template",
    "_setup_dp_logging",
    "enable_logging",
    "log",
]


script_name = sys.argv[0]
script_exe = Path(script_name).stem
if script_exe == "datapane" or script_name == "-m":  # or "pytest" in script_name:
    # argv[0] will be "-m" as client module as submodule of this module
    set_dp_mode(DPMode.SCRIPT)
elif by_datapane or script_exe == "dp-runner":
    set_dp_mode(DPMode.FRAMEWORK)
else:
    set_dp_mode(DPMode.LIBRARY)

# TODO - do we want to init only in jupyter / interactive / etc.
# only init fully in library-mode, as framework and app init explicitly
if get_dp_mode() == DPMode.LIBRARY:
    init()
    # parse any commandline params
    from .client.utils import parse_command_line

    config = parse_command_line()
    Params.replace(config)
