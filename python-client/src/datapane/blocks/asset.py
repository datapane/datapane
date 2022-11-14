"""Asset-based blocks"""
from __future__ import annotations

import typing as t
from pathlib import Path

import pandas as pd
from pandas.io.formats.style import Styler

from datapane.common import NPath, SSDict
from datapane.common.viewxml_utils import mk_attribs

from .base import BlockId, DataBlock

if t.TYPE_CHECKING:
    from datapane.processors.file_store import FileEntry


class AssetBlock(DataBlock):
    """
    AssetBlock objects form basis of all File-related blocks (abstract class, not exported)
    """

    _prev_entry: t.Optional[FileEntry] = None

    # TODO - we may need to support file here as well to handle media, etc.
    def __init__(
        self,
        data: t.Optional[t.Any] = None,
        file: t.Optional[Path] = None,
        caption: str = "",
        name: t.Optional[BlockId] = None,
        label: t.Optional[str] = None,
        **kwargs,
    ):
        # storing objects for delayed upload
        super().__init__(name=name, label=label, **kwargs)
        self.data = data
        self.file = file
        self.caption = caption
        self.file_attribs: SSDict = dict()

    def get_file_attribs(self) -> SSDict:
        return self.file_attribs


class Media(AssetBlock):
    """
    Media blocks are used to attach a file to the report that can be viewed or streamed by report viewers

    ..note:: Supported video, audio and image formats depends on the browser used to view the report. MP3, MP4, and all common image formats are generally supported by modern browsers
    """

    _tag = "Media"

    def __init__(
        self,
        file: NPath,
        name: BlockId = None,
        label: str = None,
        caption: t.Optional[str] = None,
    ):
        """
        Args:
            file: Path to a file to attach to the report (e.g. a JPEG image)
            name: A unique name for the block to reference when adding text or embedding (optional)
            caption: A caption to display below the file (optional)
            label: A label used when displaying the block (optional)
        """
        file = Path(file).expanduser()
        super().__init__(file=file, name=name, caption=caption, label=label)


class Attachment(AssetBlock):
    """
    Attachment blocks are used to attach a file to the report that can be downloaded by report viewers

    Any type of file may be attached, for instance, images (png / jpg), PDFs, JSON data, Excel files, etc.

    ..tip:: To attach streamable / viewable video, audio or images, use the `dp.Media` block instead
    """

    _tag = "Attachment"

    def __init__(
        self,
        data: t.Optional[t.Any] = None,
        file: t.Optional[NPath] = None,
        filename: t.Optional[str] = None,
        caption: t.Optional[str] = None,
        name: BlockId = None,
        label: str = None,
    ):
        """
        Args:
            data: A python object to attach to the report (e.g. a dictionary)
            file: Path to a file to attach to the report (e.g. a csv file)
            filename: Name to be used when downloading the file (optional)
            caption: A caption to display below the file (optional)
            name: A unique name for the block to reference when adding text or embedding (optional)
            label: A label used when displaying the block (optional)

        ..note:: either `data` or `file` must be provided
        """
        if file:
            file = Path(file).expanduser()
            filename = filename or file.name
        elif data:
            filename = filename or "test.data"

        super().__init__(data=data, file=file, filename=filename, name=name, caption=caption, label=label)


class Plot(AssetBlock):
    """
    Plot blocks store a Python-based plot object, including ones created by Altair, Plotly, Matplotlib, Bokeh, Folium, and PlotAPI,
    for interactive display in your report when viewed in the browser.
    """

    _tag = "Plot"

    def __init__(
        self,
        data: t.Any,
        caption: t.Optional[str] = None,
        responsive: bool = True,
        scale: float = 1.0,
        name: BlockId = None,
        label: str = None,
    ):
        """
        Args:
            data: The `plot` object to attach
            caption: A caption to display below the plot (optional)
            responsive: Whether the plot should automatically be resized to fit, set to False if your plot looks odd (optional, default: True)
            scale: Set the scaling factor for the plt (optional, default = 1.0)
            name: A unique name for the block to reference when adding text or embedding (optional)
            label: A label used when displaying the block (optional)
        """
        super().__init__(data=data, caption=caption, responsive=responsive, scale=scale, name=name, label=label)


class Table(AssetBlock):
    """
    Table blocks store the contents of a dataframe as a HTML `table` whose style can be customised using
    pandas' `Styler` API.
    """

    # NOTE - Tables are stored as HTML fragment files rather than inline within the Report document

    _tag = "Table"

    def __init__(
        self,
        data: t.Union[pd.DataFrame, Styler],
        caption: t.Optional[str] = None,
        name: BlockId = None,
        label: str = None,
    ):
        """
        Args:
            data: The pandas `Styler` instance or dataframe to generate the table from
            caption: A caption to display below the table (optional)
            name: A unique name for the block to reference when adding text or embedding (optional)
            label: A label used when displaying the block (optional)
        """
        super().__init__(data=data, caption=caption, name=name, label=label)


class DataTable(AssetBlock):
    """
    DataTable blocks store a dataframe that can be viewed, sorted, filtered by users viewing your report, similar to a spreadsheet,
    and can be downloaded by them as a CSV or Excel file.

    ..tip:: For smaller dataframes where you don't require sorting and filtering, also consider using the `Table` block
    ..note:: The DataTable component has advanced analysis features that requires a server and is not supported when saving locally, please upload such reports to a Datapane Server or use dp.Table

    """

    _tag = "DataTable"

    def __init__(
        self,
        df: pd.DataFrame,
        caption: t.Optional[str] = None,
        name: BlockId = None,
        label: str = None,
    ):
        """
        Args:
            df: The pandas dataframe to attach to the report
            caption: A caption to display below the plot (optional)
            name: A unique name for the block to reference when adding text or embedding (optional)
            label: A label used when displaying the block (optional)
        """
        super().__init__(data=df, caption=caption, name=name, label=label)
        # TODO - support pyarrow schema for local reports
        (rows, columns) = df.shape
        self.file_attribs = mk_attribs(rows=rows, columns=columns, schema="[]")
