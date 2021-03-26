import abc
import json
import os
import pickle
from functools import singledispatch
from pathlib import Path
from typing import IO, Any, BinaryIO, Generic, Optional, TextIO, Type, TypeVar

import bleach
from altair.utils import SchemaBase
from numpy import ndarray
from pandas import DataFrame
from pandas.io.formats.style import Styler

from datapane.common import log

from .. import DPError
from .common import DPTmpFile
from .files_optional import Axes, BFigure, BLayout, Figure, Map, PFigure
from .report.blocks import DataBlock, DataTable, File, Plot, Table, Text

T = TypeVar("T")
U = TypeVar("U", DataFrame, Styler)
# V = TypeVar("V", SingleBlock)


################################################################################
# Base Assets
class BaseAsset(Generic[T], abc.ABC):
    mimetype: str
    obj_type: T
    block_type: Type[DataBlock]
    ext: str
    file_mode: str = "w"

    def write(self, x: T) -> DPTmpFile:
        fn = DPTmpFile(self.ext)
        # fn = Path(file_name).with_suffix(self.ext)
        # add UTF-8 encoding if a text file
        f_kwargs = {} if "b" in self.file_mode else dict(encoding="utf-8")
        with fn.file.open(self.file_mode, **f_kwargs) as f:
            self.write_file(f, x)
        # NOTE - used to set mime-type as extended-file attrib using xttrs here
        return fn

    # NOTE: not abstract by design
    def write_file(self, f: IO, x: T):
        raise NotImplementedError("")

    def to_block(self, x: T) -> DataBlock:
        return self.block_type(x)


class BasePickleWriter(BaseAsset):
    """ Creates a pickle file from any object """

    mimetype = "application/vnd.pickle+binary"
    obj_type = Any
    block_type = File
    ext = ".pkl"
    file_mode = "wb"

    def write_file(self, f: TextIO, x: Any):
        pickle.dump(x, f)


class BaseJsonWriter(BaseAsset):
    """ Creates a JSON file from any object """

    mimetype = "application/json"
    obj_type = Any
    block_type = File
    ext = ".json"

    def write_file(self, f: TextIO, x: Any):
        json.dump(x, f)


class StringWrapper(BaseAsset):
    """Creates a Json for a string File, or Markdown for a Block"""

    mimetype = "application/json"
    obj_type = str
    block_type = Text
    ext = ".json"

    def write_file(self, f: TextIO, x: Any):
        json.dump(json.loads(x), f)


class PathWrapper(BaseAsset):
    """Creates a File block around Path objects"""

    obj_type = Path
    block_type = File

    def to_block(self, x: T) -> DataBlock:
        return File(file=x)


################################################################################
# Table Assets
class BaseTable(BaseAsset):
    mimetype = "application/vnd.datapane.table+html"
    ext = ".tbl.html"
    TABLE_CELLS_LIMIT: int = 5000
    obj_type: U
    block_type = Table
    # TODO - move to own bleach class/module?
    allowed_attrs = ["id", "class", "type", "style"]
    allowed_tags = ["style", "table", "thead", "tbody", "tr", "td", "th"]
    allowed_protocols = ["http", "https"]

    def write_file(self, f: IO, x: U):
        n_cells = self._get_cells(x)
        if n_cells > self.TABLE_CELLS_LIMIT:
            raise ValueError(
                f"Dataframe over limit of {self.TABLE_CELLS_LIMIT} cells for dp.Table, consider using dp.DataTable instead or aggregating the df first"
            )

        # sanitise the generated HTML
        safe_html = bleach.clean(
            self.render_html(x),
            tags=self.allowed_tags,
            attributes=self.allowed_attrs,
            protocols=self.allowed_protocols,
        )
        f.write(safe_html)

    def to_block(self, x: T) -> DataBlock:
        return Table(x) if self._get_cells(x) <= self.TABLE_CELLS_LIMIT else DataTable(x)

    def _get_cells(self, x: U) -> int:
        df = self._get_df(x)
        # TODO - need to truncate the styler...
        # df1 = truncate_dataframe(df, max_cells=2000)
        return df.shape[0] * df.shape[1]

    @abc.abstractmethod
    def _get_df(self, obj: U) -> DataFrame:
        ...

    @abc.abstractmethod
    def render_html(self, obj: U) -> str:
        ...


class StylerTable(BaseTable):
    """Creates a styled html table from a pandas Styler object"""

    obj_type = Styler

    def _get_df(self, obj: U) -> DataFrame:
        return obj.data

    def render_html(self, obj: U) -> str:
        return obj.render()


class DataFrameTable(BaseTable):
    """Creates an html table from the dataframe"""

    obj_type = DataFrame

    def _get_df(self, obj: U) -> DataFrame:
        return obj

    def render_html(self, obj: U) -> str:
        return obj.to_html()


################################################################################
# Plot Assets
class PlotAsset(BaseAsset):
    block_type = Plot


class MatplotBasePlot(PlotAsset):
    ext = ".svg"
    mimetype = "image/svg+xml"

    def _write_figure(self, x: Figure) -> DPTmpFile:
        """Creates an SVG from figure"""
        import matplotlib.pyplot as plt

        fn = DPTmpFile(self.ext)
        x = x or plt.gcf()
        x.savefig(str(fn))
        return fn


class MatplotFigurePlot(MatplotBasePlot):
    obj_type = Figure

    def write(self, x: Figure) -> DPTmpFile:
        return super()._write_figure(x)


class MatplotAxesPlot(MatplotBasePlot):
    obj_type = Axes

    def write(self, x: Axes) -> DPTmpFile:
        f: Figure = x.get_figure()
        return super()._write_figure(f)


class MatplotNDArrayPlot(MatplotBasePlot):
    obj_type = ndarray

    def write(self, x: ndarray) -> DPTmpFile:
        f: Figure = x.flatten()[0].get_figure()
        return super()._write_figure(f)


class BokehBasePlot(PlotAsset):
    """Returns an interactive Bokeh application, supports both basic plots and layout plots via subclasses"""

    mimetype = "application/vnd.bokeh.show+json"
    ext = ".bokeh.json"

    def write_file(self, f: TextIO, app):
        from bokeh.embed import json_item

        json.dump(json_item(app), f)


class BokehPlot(BokehBasePlot):
    obj_type = BFigure


class BokehLayoutPlot(BokehBasePlot):
    obj_type = BLayout


class AltairPlot(PlotAsset):
    """Creates a vega-light chart from Altair Chart / pdvega Axes object."""

    mimetype = "application/vnd.vegalite.v4+json"
    ext = ".vl.json"
    obj_type = SchemaBase

    def write_file(self, f: TextIO, chart: SchemaBase):
        json.dump(chart.to_dict(), f)


class PlotlyPlot(PlotAsset):
    """Creates a plotly graph from a figure object"""

    mimetype = "application/vnd.plotly.v1+json"
    ext = ".pl.json"
    obj_type = PFigure

    def write_file(self, f: TextIO, chart: PFigure):
        json.dump(chart.to_json(), f)


class FoliumPlot(PlotAsset):
    mimetype = "application/vnd.folium+html"
    ext = ".fl.html"
    obj_type = Map

    def write_file(self, f: BinaryIO, m: Map):
        html: str = m.get_root().render()
        f.write(html)


################################################################################
# register all the plot types
plots = [
    StringWrapper,
    PathWrapper,
    # dataframes / tables
    StylerTable,
    DataFrameTable,
    # plots
    BokehPlot,
    BokehLayoutPlot,
    AltairPlot,
    PlotlyPlot,
    MatplotFigurePlot,
    MatplotAxesPlot,
    MatplotNDArrayPlot,
    FoliumPlot,
]


@singledispatch
def get_wrapper(x: Any, default_to_json: bool, error_msg: Optional[str] = None) -> BaseAsset:
    if error_msg:
        raise DPError(error_msg)

    # The base writer is either a pickle writer or JSON writer.
    return BaseJsonWriter() if default_to_json else BasePickleWriter()


for p in plots:
    get_wrapper.register(p.obj_type, lambda _, default_to_json, error_msg, p=p: p())


# Entry Points
def save(obj: Any, default_to_json: bool = False) -> DPTmpFile:
    fn = get_wrapper(obj, default_to_json=default_to_json, error_msg=None).write(obj)
    log.debug(f"Saved object to {fn} ({os.path.getsize(fn.file)} bytes)")
    return fn


def convert(obj: Any) -> "DataBlock":
    """Attempt to convert/wrap a 'primitive' Python object into a Datapane 'boxed' object"""
    error_msg = f"{type(obj)} not supported directly, please pass into in the appropriate dp object (including dp.File if want to upload as a pickle)"
    return get_wrapper(obj, default_to_json=False, error_msg=error_msg).to_block(obj)
