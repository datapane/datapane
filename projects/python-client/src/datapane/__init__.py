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

__version__ = "0.15.4"

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
    AppFormatting,
    AppWidth,
    Attachment,
    BigNumber,
    Code,
    DataTable,
    Divider,
    Embed,
    Empty,
    File,
    FontChoice,
    Formula,
    Group,
    Media,
    Page,
    PageLayout,
    Plot,
    Processor,
    Report,
    ReportFormatting,
    ReportWidth,
    Select,
    SelectType,
    Table,
    Text,
    TextAlignment,
    Toggle,
    build,
    builtins,
    cells_to_blocks,
    hello_world,
    login,
    logout,
    ping,
    save_report,
    serve,
    template,
    upload,
)
from .client.config import init
from .common.dp_types import DPMode, get_dp_mode, set_dp_mode

__all__ = [
    "App",
    "AppFormatting",
    "AppWidth",
    "HTML",
    "Attachment",
    "BigNumber",
    "Code",
    "DataTable",
    "Divider",
    "Embed",
    "Empty",
    "File",
    "FontChoice",
    "Formula",
    "Group",
    "Media",
    "Page",
    "PageLayout",
    "Plot",
    "Processor",
    "Report",
    "ReportFormatting",
    "ReportWidth",
    "Select",
    "SelectType",
    "Table",
    "Text",
    "TextAlignment",
    "Toggle",
    "builtins",
    "hello_world",
    "login",
    "logout",
    "ping",
    "template",
    "_setup_dp_logging",
    "enable_logging",
    "log",
    "upload",
    "save_report",
    "serve",
    "build",
    "cells_to_blocks",
]


script_name = sys.argv[0]
script_exe = Path(script_name).stem
if script_exe == "datapane" or script_name == "-m":  # or "pytest" in script_name:
    # argv[0] will be "-m" as client module as submodule of this module
    set_dp_mode(DPMode.SCRIPT)
else:
    set_dp_mode(DPMode.LIBRARY)

# TODO - do we want to init only in jupyter / interactive / etc.
# only init fully in library-mode, as framework and app init explicitly
if get_dp_mode() == DPMode.LIBRARY and not _IN_PYTEST:
    init()
