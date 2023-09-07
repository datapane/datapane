"""
Datapane Processors

API for processing Views, e.g. rendering it locally and publishing to a remote server
"""

from __future__ import annotations

import os
import typing as t
from pathlib import Path
from shutil import rmtree

from datapane.client import DPClientError
from datapane.common import NPath
from datapane.view import Blocks, BlocksT

from .file_store import B64FileEntry, GzipTmpFileEntry
from .processors import (
    ConvertXML,
    ExportHTMLFileAssets,
    ExportHTMLInlineAssets,
    ExportHTMLStringInlineAssets,
    PreProcessView,
)
from .types import Formatting, Pipeline, ViewState

__all__ = ["upload_report", "save_report", "build_report", "stringify_report"]


################################################################################
# exported public API
def build_report(
    blocks: BlocksT,
    name: str = "Report",
    dest: t.Optional[NPath] = None,
    formatting: t.Optional[Formatting] = None,
    overwrite: bool = False,
) -> None:
    """Build an (static) app with a directory structure, which can be served by a local http server

    !!! note
        This outputs compressed assets into the dir as well, may be an issue if self-hosting

    Args:
        blocks: The `Blocks` object or a list of Blocks
        name: The name of the app directory to be created
        dest: File path to store the app directory
        formatting: Sets the basic app styling
        overwrite: Replace existing app with the same name and destination if already exists (default: False)
    """
    # TODO(product) - unknown if we should keep this...

    # build the dest dir
    app_dir: Path = Path(dest or os.getcwd()) / name
    app_exists = app_dir.is_dir()

    if app_exists and overwrite:
        rmtree(app_dir)
    elif app_exists and not overwrite:
        raise DPClientError(f"Report exists at given path {str(app_dir)} -- set `overwrite=True` to allow overwrite")

    assets_dir = app_dir / "assets"
    assets_dir.mkdir(parents=True)

    # write the app html and assets
    s = ViewState(blocks=Blocks.wrap_blocks(blocks), file_entry_klass=GzipTmpFileEntry, dir_path=assets_dir)
    _: str = (
        Pipeline(s)
        .pipe(PreProcessView(is_finalised=True))
        .pipe(ConvertXML())
        .pipe(ExportHTMLFileAssets(app_dir=app_dir, name=name, formatting=formatting))
        .result
    )


def save_report(
    blocks: BlocksT,
    path: str,
    open: bool = False,
    name: str = "Report",
    formatting: t.Optional[Formatting] = None,
) -> None:
    """Save the app document to a local HTML file

    Args:
        blocks: The `Blocks` object or a list of Blocks
        path: File path to store the document
        open: Open in your browser after creating (default: False)
        name: Name of the document (optional: uses path if not provided)
        formatting: Sets the basic app styling
    """

    s = ViewState(blocks=Blocks.wrap_blocks(blocks), file_entry_klass=B64FileEntry)
    _: str = (
        Pipeline(s)
        .pipe(PreProcessView(is_finalised=True))
        .pipe(ConvertXML())
        .pipe(ExportHTMLInlineAssets(path=path, open=open, name=name, formatting=formatting))
        .result
    )


def stringify_report(
    blocks: BlocksT,
    name: t.Optional[str] = None,
    formatting: t.Optional[Formatting] = None,
) -> str:
    """Stringify the app document to a HTML string

    Args:
        blocks: The `Blocks` object or a list of Blocks
        name: Name of the document (optional: uses path if not provided)
        formatting: Sets the basic app styling
    """

    s = ViewState(blocks=Blocks.wrap_blocks(blocks), file_entry_klass=B64FileEntry)
    report_html: str = (
        Pipeline(s)
        .pipe(PreProcessView(is_finalised=False))
        .pipe(ConvertXML())
        .pipe(ExportHTMLStringInlineAssets(name=name, formatting=formatting))
        .result
    )

    return report_html


def upload_report(
    *args,
    **kwargs,
) -> None:
    """
    (No longer supported).
    Upload as a report, including its attached assets, to the logged-in Datapane Server.
    """
    raise DPClientError(
        "Datapane Cloud is now read-only and does not support Report uploading, only local, saved HTML report output is supported"
    )
