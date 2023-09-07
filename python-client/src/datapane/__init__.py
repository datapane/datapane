# Copyright 2020 StackHut Limited (trading as Datapane)
# SPDX-License-Identifier: Apache-2.0
import sys
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

__version__ = "0.17.0"


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

from .blocks import (
    HTML,
    Attachment,
    BigNumber,
    Block,
    Code,
    DataTable,
    Embed,
    Empty,
    Formula,
    Group,
    Media,
    Page,
    Plot,
    Select,
    SelectType,
    Table,
    Text,
    Toggle,
    VAlign,
    wrap_block,
)
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
from .view import App, Blocks, Report, View

# Other useful re-exports
# ruff: noqa: I001
from . import builtins  # isort:skip  otherwise circular import issue

X = wrap_block

__all__ = [
    "App",
    "Report",
    "DPClientError",
    "builtins",
    "enable_logging",
    "print_debug_info",
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
    "VAlign",
    "Blocks",
    "upload_report",
    "save_report",
    "build_report",
    "stringify_report",
    "X",
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
