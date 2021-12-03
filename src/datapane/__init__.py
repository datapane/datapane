# Copyright 2020 StackHut Limited (trading as Datapane)
# SPDX-License-Identifier: Apache-2.0
# flake8: noqa F401
import os
import sys
from pathlib import Path

try:
    from ._version import __rev__
except ImportError:
    # NOTE - could use subprocess to get from git?
    __rev__ = "local"

__version__ = "0.13.0"

_TEST_ENV = bool(os.environ.get("DP_TEST_ENV", ""))
_IN_PYTEST = "pytest" in sys.modules
_IN_DPSERVER = "dp" in sys.modules
# we're running on datapane platform
ON_DATAPANE: bool = "DATAPANE_ON_DATAPANE" in os.environ
_USING_CONDA = os.path.exists(os.path.join(sys.prefix, "conda-meta", "history"))


# Other useful re-exports
from .common.utils import enable_logging, log, _setup_dp_logging

# Public API re-exports
from .client.api import (
    Attachment,
    Media,
    BigNumber,
    Code,
    DataTable,
    Divider,
    Embed,
    Empty,
    File,
    Group,
    FontChoice,
    Formula,
    HTML,
    Media,
    Text,
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
    App,
    Select,
    SelectType,
    Table,
    Text,
    TextAlignment,
    Toggle,
    Environment,
    Visibility,
    by_datapane,
    signup,
    login,
    logout,
    ping,
    hello_world,
    builtins,
)
from .client.config import init
from .common.dp_types import DPMode, set_dp_mode, get_dp_mode

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
    from .client.api.runtime import Params

    config = parse_command_line()
    Params.replace(config)
