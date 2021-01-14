"""# API docs for Datapane Client

These docs describe the Python API for building Datapane Reports, along with additional information on the Datapane Teams API.

Usage docs for Datapane can be found at https://docs.datapane.com

These objects are all available under the `datapane` module, via `import datapane as dp` (they are re-exported from `datapane.client.api`).

### Datapane Reports API

The core reporting APIs are available on both the public and teams plans, these are found in `datapane.client.api.report`, including,

  - `datapane.client.api.report.core.Report`
  - Layout Blocks
    - `datapane.client.api.report.blocks.Page`
    - `datapane.client.api.report.blocks.Group`
    - `datapane.client.api.report.blocks.Select`
  - Data Blocks
    - `datapane.client.api.report.blocks.Plot`
    - `datapane.client.api.report.blocks.Table`
    - `datapane.client.api.report.blocks.DataTable`
    - `datapane.client.api.report.blocks.File`
    - `datapane.client.api.report.blocks.BigNumber`
    - `datapane.client.api.report.blocks.Text`
    - `datapane.client.api.report.blocks.Code`
    - `datapane.client.api.report.blocks.HTML`

### Datapane Teams

Additional API docs for teams and enterprise features are found in `datapane.client.api.teams` that provide automation and sharing of data analytics workflows

  - `datapane.client.api.teams.Blob`
  - `datapane.client.api.teams.Variable`
  - `datapane.client.api.teams.Script`
  - `datapane.client.api.teams.Schedule`


.. note::  These docs describe the latest version of the datapane API available on [pypi](https://pypi.org/project/datapane/)
    <a href="https://pypi.org/project/datapane/">
        <img src="https://img.shields.io/pypi/v/datapane?color=blue" alt="Latest release" />
    </a>

"""

# flake8: noqa F401
# Internal API re-exports
import warnings

from .common import HTTPError, Resource
from .dp_object import DPObjectRef
from .teams import Blob, Run, Schedule, Script, Variable
from .report.blocks import (
    BigNumber,
    Code,
    Group,
    DataTable,
    Embed,
    File,
    HTML,
    Page,
    Plot,
    Select,
    SelectType,
    Text,
    Table,
)
from .report.core import Report, ReportType, Visibility
from .runtime import Params, Result, by_datapane, on_datapane, _reset_runtime, _report
from .user import login, logout, ping
from ..utils import IncompatibleVersionError
from ..config import init

from . import templates


################################################################################
# deprecations
# TODO - remove deprecation
class Markdown(Text):
    def __init__(self, *a, **kw):
        warnings.warn("Deprecated, to be removed in next release, use dp.Text instead.")
        super().__init__(*a, **kw)


class Blocks(Group):
    def __init__(self, *a, **kw):
        warnings.warn("Deprecated, to be removed in next release, use dp.Group instead.")
        super().__init__(*a, **kw)
