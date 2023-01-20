"""# API docs for Datapane Client

These docs describe the Python API for building Datapane documents.

Usage docs for Datapane can be found at https://docs.datapane.com

These objects are all available under the `datapane` module, via `import datapane as dp` (they are re-exported from `datapane.client.api`).

### Datapane Reports API

The core document APIs, these are found in `datapane.client.api.report`, including,

  - `datapane.client.api.report.core.App`
  - Layout Blocks
    - `datapane.client.api.report.blocks.Page`
    - `datapane.client.api.report.blocks.Group`
    - `datapane.client.api.report.blocks.Select`
  - Data Blocks
    - `datapane.client.api.report.blocks.Plot`
    - `datapane.client.api.report.blocks.Table`
    - `datapane.client.api.report.blocks.DataTable`
    - `datapane.client.api.report.blocks.Media`
    - `datapane.client.api.report.blocks.Formula`
    - `datapane.client.api.report.blocks.BigNumber`
    - `datapane.client.api.report.blocks.Text`
    - `datapane.client.api.report.blocks.Code`
    - `datapane.client.api.report.blocks.HTML`

### Datapane Enterprise (beta)

Additional API docs are found in `datapane.client.api.teams` that provide building, deployment, and sharing of data analytics apps and workflows

  - `datapane.client.api.teams.File`
  - `datapane.client.api.teams.Environment`
  - `datapane.client.api.teams.LegacyApp`
  - `datapane.client.api.teams.Schedule`


..note::  These docs describe the latest version of the datapane API available on [pypi](https://pypi.org/project/datapane/)
    <a href="https://pypi.org/project/datapane/">
        <img src="https://img.shields.io/pypi/v/datapane?color=blue" alt="Latest release" />
    </a>

"""

# Internal API re-exports
import warnings

from ..exceptions import IncompatibleVersionError
from .common import HTTPError, Resource
from .dp_object import DPObjectRef
from .ipython_utils import cells_to_blocks
from .report.blocks import (
    HTML,
    Attachment,
    BigNumber,
    Code,
    DataTable,
    Divider,
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
)
from .report.core import (
    App,
    AppFormatting,
    AppWidth,
    FontChoice,
    PageLayout,
    Report,
    ReportFormatting,
    ReportWidth,
    TextAlignment,
)
from .report.processors import Processor, build, save_report, serve, upload
from .runtime import Params, Result, _report, _reset_runtime, by_datapane
from .teams import Environment, File, LegacyApp, Run, Schedule
from .user import hello_world, login, logout, ping, signup, template

from ..config import init  # isort:skip  otherwise circular import issue
from . import builtins  # isort:skip

__all__ = [
    "warnings",
    "init",
    "App",
    "AppFormatting",
    "AppWidth",
    "IncompatibleVersionError",
    "builtins",
    "HTTPError",
    "Resource",
    "DPObjectRef",
    "HTML",
    "Attachment",
    "BigNumber",
    "Code",
    "DataTable",
    "Divider",
    "Embed",
    "Empty",
    "Formula",
    "Group",
    "LegacyApp",
    "Media",
    "Page",
    "Plot",
    "Report",
    "Select",
    "SelectType",
    "Table",
    "Text",
    "Toggle",
    "FontChoice",
    "PageLayout",
    "Processor",
    "ReportFormatting",
    "ReportWidth",
    "TextAlignment",
    "Params",
    "Result",
    "_report",
    "_reset_runtime",
    "by_datapane",
    "App",
    "Environment",
    "File",
    "Run",
    "Schedule",
    "hello_world",
    "login",
    "logout",
    "ping",
    "signup",
    "template",
    "upload",
    "save_report",
    "serve",
    "build",
    "cells_to_blocks",
]
