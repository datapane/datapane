"""
Datapane Processors

API for processing Views, e.g. rendering it locally and publishing to a remote server

# TODO - move this out into a new top-level module
"""

from __future__ import annotations

import os
import typing as t
from pathlib import Path
from shutil import rmtree

from datapane.client import DPClientError
from datapane.client import config as c
from datapane.client.utils import display_msg, open_in_browser
from datapane.cloud_api.report import CloudReport
from datapane.common import NPath, dict_drop_empty
from datapane.view import Blocks, BlocksT

from .file_store import B64FileEntry, GzipTmpFileEntry
from .processors import (
    ConvertXML,
    ExportHTMLFileAssets,
    ExportHTMLInlineAssets,
    ExportHTMLStringInlineAssets,
    PreProcessView,
    PreUploadProcessor,
)
from .types import Formatting, Pipeline, ViewState

if t.TYPE_CHECKING:
    from datapane.cloud_api.common import FileAttachmentList


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
        This outputs compressed assets into the dir as well, may be an issue if self-hosting...

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
        raise DPClientError(f"App exists at given path {str(app_dir)} -- set `overwrite=True` to allow overwrite")

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
    blocks: BlocksT,
    name: str,
    description: str = "",
    source_url: str = "",
    publicly_visible: t.Optional[bool] = None,
    tags: t.Optional[t.List[str]] = None,
    project: t.Optional[str] = None,
    open: bool = False,
    formatting: t.Optional[Formatting] = None,
    overwrite: bool = False,
    **kwargs,
) -> CloudReport:
    """
    Upload as a report, including its attached assets, to the logged-in Datapane Server.
    Args:
        blocks: The `Blocks` object or a list of Blocks
        name: The document name - can include spaces, caps, symbols, etc., e.g. "Profit & Loss 2020"
        description: A high-level description for the document, this is displayed in searches and thumbnails
        source_url: A URL pointing to the source code for the document, e.g. a GitHub repo or a Colab notebook
        publicly_visible: Visible to anyone with the link
        tags: A list of tags (as strings) used to categorise your document
        project: Project to add the app to
        open: Open the file in your browser after creating
        formatting: Set the basic styling for your app
        overwrite: Overwrite the app
    """
    # NOTE - this will become App deploy entrypoint also

    display_msg("Uploading report and associated data - *please wait...*")

    kwargs.update(
        name=name,
        description=description,
        tags=tags or [],
        source_url=source_url,
        publicly_visible=publicly_visible,
        project=project,
    )
    # additional formatting params
    if formatting:
        kwargs.update(
            width=formatting.width.value,
            style_header=(
                f'<style type="text/css">\n{formatting.to_css()}\n</style>' if c.config.is_org else formatting.to_css()
            ),
            is_light_prose=formatting.light_prose,
        )
    # current protocol is to strip all empty args and patch (via a post)
    kwargs = dict_drop_empty(kwargs)

    s = ViewState(blocks=Blocks.wrap_blocks(blocks), file_entry_klass=GzipTmpFileEntry)
    (view_xml, file_list) = (
        Pipeline(s).pipe(PreProcessView(is_finalised=True)).pipe(ConvertXML()).pipe(PreUploadProcessor()).result
    )

    # attach the view and upload as an App
    files: FileAttachmentList = dict(attachments=file_list)
    report = CloudReport.post_with_files(
        files, overwrite=overwrite, document=view_xml, files_already_gzipped=True, **kwargs
    )

    if open:
        open_in_browser(report.web_url)

    display_msg(
        "Report successfully uploaded - view and share at {web_url:l}.",
        web_url=report.web_url,
    )
    return report
