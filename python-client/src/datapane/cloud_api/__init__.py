"""# API docs for Datapane Client

These docs describe the Python API for building Datapane documents.

Usage docs for Datapane can be found at https://docs.datapane.com

These objects are all available under the `datapane` module, via `import datapane as dp` (they are re-exported from `datapane.client.api`).

### Datapane Reports API

The core document APIs, these are found in `datapane.client.api.report`, including,

  - `datapane.client.api.report.core.App`
  - Layout Blocks
    - `datapane.client.api.report.blocks.Group`
    - `datapane.client.api.report.blocks.Select`
  - Interactive Blocks
    - `datapane.client.api.report.blocks.Interactive`
    - `datapane.client.api.report.blocks.Empty`
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


..note::  These docs describe the latest version of the datapane API available on [pypi](https://pypi.org/project/datapane/)
    <a href="https://pypi.org/project/datapane/">
        <img src="https://img.shields.io/pypi/v/datapane?color=blue" alt="Latest release" />
    </a>

"""
# flake8: noqa:F401
from .app import AppFormatting, AppWidth, FontChoice, PageLayout, Report, TextAlignment
from .common import Resource
from .dp_object import DPObjectRef
from .file import File
from .user import hello_world, login, logout, ping, signup, template
