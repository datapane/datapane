# flake8: noqa F401
try:
    from ._version import __rev__
except ImportError:
    # NOTE - could use subprocess to get from git?
    __rev__ = "local"

__version__ = "0.7.0"

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
    Table,
    Variable,
    by_datapane,
    init,
    on_datapane,
)
