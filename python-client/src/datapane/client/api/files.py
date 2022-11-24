import abc
import json
import os
import pickle
from functools import singledispatch
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any, Generic, List, Optional, Type, TypeVar

from altair.utils import SchemaBase
from numpy import ndarray
from pandas import DataFrame
from pandas.io.formats.style import Styler

from datapane.common import log

from .. import DPError
from .common import DPTmpFile
from .files_optional import Axes, BFigure, BLayout, Figure, Map, PFigure, Visualisation
from .report.blocks import Attachment, DataBlock, DataTable, Plot, Table, Text

if TYPE_CHECKING:
    from bokeh.model import Model

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
        encoding = None if "b" in self.file_mode else "utf-8"
        with fn.file.open(mode=self.file_mode, encoding=encoding) as f:
            self.write_file(f, x)
        # NOTE - used to set mime-type as extended-file attrib using xttrs here
        return fn

    # NOTE: not abstract by design
    def write_file(self, f: IO, x: T):
        raise NotImplementedError("")

    def to_block(self, x: T) -> DataBlock:
        return self.block_type(x)  # type: ignore


class BasePickleWriter(BaseAsset):
    """Creates a pickle file from any object"""

    mimetype = "application/vnd.pickle+binary"
    block_type = Attachment
    ext = ".pkl"
    file_mode = "wb"
    obj_type = Any

    def write_file(self, f: IO, x: Any):
        pickle.dump(x, f)


class StringWrapper(BaseAsset):
    """Creates a Json for a string File, or Markdown for a Block"""

    mimetype = "application/json"
    block_type = Text
    ext = ".json"
    obj_type = str

    def write_file(self, f: IO, x: str):
        json.dump(json.loads(x), f)


class PathWrapper(BaseAsset):
    """Creates an Attachment block around Path objects"""

    obj_type = Path
    block_type = Attachment

    def to_block(self, x: Path) -> DataBlock:
        return Attachment(file=x)


################################################################################
# Table Assets
class BaseTable(BaseAsset, Generic[U]):
    mimetype = "application/vnd.datapane.table+html"
    ext = ".tbl.html"
    TABLE_CELLS_LIMIT: int = 100
    obj_type: U
    block_type = Table

    def write_file(self, f: IO, x: U):
        f.write(self.render_html(x))

    def to_block(self, x: T) -> DataBlock:
        return Table(x) if self._get_cells(x) <= self.TABLE_CELLS_LIMIT else DataTable(x)

    def _get_cells(self, x: U) -> int:
        df = self._get_df(x)
        # TODO - need to truncate the styler...
        # df1 = truncate_dataframe(df, max_cells=2000)
        return df.shape[0] * df.shape[1]

    @abc.abstractmethod
    def _get_df(self, obj: U) -> DataFrame:
        pass

    @abc.abstractmethod
    def render_html(self, obj: U) -> str:
        pass


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
        x.savefig(str(fn), bbox_inches="tight")
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

    def write_file(self, f: IO, app: "Model"):
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

    def write_file(self, f: IO, chart: SchemaBase):
        json.dump(chart.to_dict(), f)


class PlotlyPlot(PlotAsset):
    """Creates a plotly graph from a figure object"""

    mimetype = "application/vnd.plotly.v1+json"
    ext = ".pl.json"
    obj_type = PFigure

    def write_file(self, f: IO, chart: PFigure):
        json.dump(chart.to_json(), f)


class FoliumPlot(PlotAsset):
    mimetype = "application/vnd.folium+html"
    ext = ".fl.html"
    obj_type = Map

    def write_file(self, f: IO, m: Map):
        html: str = m.get_root().render()
        f.write(html)


class PlotapiPlot(PlotAsset):
    mimetype = "application/vnd.plotapi+html"
    ext = ".plotapi.html"
    obj_type = Visualisation

    def write_file(self, f: IO, chart: Visualisation):
        html: str = chart.to_string()
        f.write(html)


################################################################################
# register all the plot types
plots: List = [
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
    PlotapiPlot,
]


@singledispatch
def get_wrapper(x: Any, error_msg: Optional[str] = None) -> BaseAsset:
    if error_msg:
        raise DPError(error_msg)

    # The base writer is a pickle writer
    return BasePickleWriter()


for p in plots:
    get_wrapper.register(p.obj_type, lambda _, error_msg, p=p: p())


# Entry Points
def save(obj: Any) -> DPTmpFile:
    fn = get_wrapper(obj, error_msg=None).write(obj)
    log.debug(f"Saved object to {fn} ({os.path.getsize(fn.file)} bytes)")
    return fn


def convert(obj: Any) -> "DataBlock":
    """Attempt to convert/wrap a 'primitive' Python object into a Datapane 'boxed' object"""
    error_msg = f"{type(obj)} not supported directly, please pass into in the appropriate dp object (including dp.Attachment if want to upload as a pickle)"
    return get_wrapper(obj, error_msg=error_msg).to_block(obj)
