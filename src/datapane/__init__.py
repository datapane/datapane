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

__version__ = "0.8.3"

TEST_ENV: bool = "DP_TEST_ENV" in os.environ

# Other useful re-exports
from .common.utils import log, _setup_dp_logging

# Public API re-exports
from .client.api import (
    Blocks,
    Blob,
    File,
    Markdown,
    Params,
    Plot,
    Report,
    Result,
    Run,
    Script,
    Schedule,
    Table,
    Variable,
    by_datapane,
    login,
    logout,
    on_datapane,
    ping,
)
from .client.config import init
from .common.dp_types import DPMode, set_dp_mode, get_dp_mode

script_name = sys.argv[0]
script_exe = Path(script_name).stem
if script_exe == "datapane" or script_name == "-m":  # or "pytest" in script_name:
    # argv[0] will be "-m" as client module as submodule of this module
    set_dp_mode(DPMode.APP)
elif by_datapane or script_exe == "dp-runner":
    set_dp_mode(DPMode.FRAMEWORK)
else:
    set_dp_mode(DPMode.LIBRARY)


# TODO - do we want to init only in jupyter / interactive / etc.
# only init fully in library-mode, as framework and app init explicitly
if get_dp_mode() == DPMode.LIBRARY:
    init()
    # parse any command0line params
    from .client.utils import parse_command_line

    parse_command_line()
