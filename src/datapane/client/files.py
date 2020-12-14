"""
Creating charts.
---------------

We recommend using Altair/pdvega for generating interactive charts: use the supplied `save`
function.

Example
-------

altair_pandas::
  # uses the default pandas plotting API
  from datapane.files import save

  import numpy as np

  pd.set_option('plotting.backend', 'altair')  # Installing altair_pandas registers this.

  data = pd.DataFrame({'x': np.random.randn(200),
                       'y': np.random.randn(200)})

  plot = data.plot.scatter('x', 'y')
  save(plot, "scatter")

pdvega::

  from datapane.files import save

  import numpy as np
  import pdvega

  data = pd.DataFrame({'x': np.random.randn(200),
                       'y': np.random.randn(200)})

  plot = data.vgplot.scatter('x', 'y')
  save(plot, "scatter")

altair::

  from datapane.files import save

  import altair as alt
  import numpy as np

  data = pd.DataFrame({'x': np.random.randn(20),
                      'y': np.random.randn(20)})
  plot = alt.Chart(data).mark_bar().encode(
      y='y',
      x='x'
  )

  save(plot, "bars")

Also for your convenience the `save` function is compatible with matplotlib figures, Bokeh Figures, and pandas dataframes (it saves a table in this instance).

Example
-------

::

  from datapane.files import save

  import matplotlib.pyplot as plt

  fig, ax = plt.subplots()
  ax.plot([1, 2, 3, 4], [1, 4, 9, 16])
  save(figure, "line.svg")
  out_df = in_df
"""

import abc
import json
import pickle
from functools import singledispatch
from typing import IO, Any, BinaryIO, Generic, TextIO, TypeVar

import bleach
import matplotlib.pyplot as plt
from altair.utils import SchemaBase
from bokeh.embed import json_item
from bokeh.layouts import LayoutDOM as BLayout
from bokeh.plotting.figure import Figure as BFigure
from folium import Map
from matplotlib.figure import Axes, Figure
from numpy import ndarray
from pandas import DataFrame
from pandas.io.formats.style import Styler
from plotly.graph_objects import Figure as PFigure

from .api.common import DPTmpFile

T = TypeVar("T")
U = TypeVar("U", DataFrame, Styler)


class BasePlot(Generic[T], abc.ABC):
    mimetype: str
    ext: str
    fig_type: T
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
        pass


class PickleWriter(BasePlot):
    """ Creates a pickle file from a pre-pickled object """

    mimetype = "application/vnd.pickle+binary"
    fig_type = bytes
    ext = ".pkl"
    file_mode = "wb"

    def write_file(self, f: BinaryIO, x: bytes):
        f.write(x)


class BasePickleWriter(PickleWriter):
    """ Creates a pickle file from any object """

    fig_type = Any

    def write_file(self, f: TextIO, x: any):
        pickle.dump(x, f)


class BaseJsonWriter(BasePlot):
    """ Creates a JSON file from any object """

    mimetype = "application/json"
    fig_type = Any
    ext = ".json"

    def write_file(self, f: TextIO, x: any):
        if isinstance(x, str):
            json.dump(json.loads(x), f)
        else:
            json.dump(x, f)


class MatplotBasePlot(BasePlot):
    ext = ".svg"
    mimetype = "image/svg+xml"

    def _write_figure(self, x: Figure) -> DPTmpFile:
        """Creates an SVG from figure"""
        fn = DPTmpFile(self.ext)
        x = x or plt.gcf()
        x.savefig(str(fn))
        return fn


class MatplotFigurePlot(MatplotBasePlot):
    fig_type = Figure

    def write(self, x: Figure) -> DPTmpFile:
        return super()._write_figure(x)


class MatplotAxesPlot(MatplotBasePlot):
    fig_type = Axes

    def write(self, x: Axes) -> DPTmpFile:
        f: Figure = x.get_figure()
        return super()._write_figure(f)


class MatplotNDArrayPlot(MatplotBasePlot):
    fig_type = ndarray

    def write(self, x: ndarray) -> DPTmpFile:
        f: Figure = x.flatten()[0].get_figure()
        return super()._write_figure(f)


class BaseTablePlot(BasePlot):
    mimetype = "application/vnd.datapane.table+html"
    ext = ".tbl.html"
    TABLE_CELLS_LIMIT: int = 2000
    fig_type: U
    # TODO - move to own bleach class/module?
    allowed_attrs = ["id", "class", "type", "style"]
    allowed_tags = ["style", "table", "thead", "tbody", "tr", "td", "th"]
    allowed_protocols = ["http", "https"]

    def write_file(self, f: IO, x: U):
        df = self.get_df(x)
        # TODO - need to truncate the styler...
        # df1 = truncate_dataframe(df, max_cells=2000)
        n_cells = df.shape[0] * df.shape[1]
        if n_cells > self.TABLE_CELLS_LIMIT:
            raise ValueError(
                f"Dataframe over limit of {self.TABLE_CELLS_LIMIT} cells for dp.Table, consider using dp.DataTable instead"
            )

        # sanitise the generated HTML
        safe_html = bleach.clean(
            self.render_html(x),
            tags=self.allowed_tags,
            attributes=self.allowed_attrs,
            protocols=self.allowed_protocols,
        )
        f.write(safe_html)

    @abc.abstractmethod
    def get_df(self, obj: U) -> DataFrame:
        ...

    @abc.abstractmethod
    def render_html(self, obj: U) -> str:
        ...


class StylerTablePlot(BaseTablePlot):
    """Creates a styled html table from a pandas Styler object"""

    fig_type = Styler

    def get_df(self, obj: U) -> DataFrame:
        return obj.data

    def render_html(self, obj: U) -> str:
        return obj.render()


class DataFrameTablePlot(BaseTablePlot):
    """Creates an html table from the dataframe"""

    fig_type = DataFrame

    def get_df(self, obj: U) -> DataFrame:
        return obj

    def render_html(self, obj: U) -> str:
        return obj.to_html()


class BokehBasePlot(BasePlot):
    """Returns an interactive Bokeh application, supports both basic plots and layout plots via subclasses"""

    mimetype = "application/vnd.bokeh.show+json"
    ext = ".bokeh.json"

    def _write_file(self, f: TextIO, app: any) -> DPTmpFile:
        json.dump(json_item(app), f)


class BokehPlot(BokehBasePlot):
    fig_type = BFigure

    def write_file(self, f: TextIO, app: BFigure) -> DPTmpFile:
        super()._write_file(f, app)


class BokehLayoutPlot(BokehBasePlot):
    fig_type = BLayout

    def write_file(self, f: TextIO, app: BLayout) -> DPTmpFile:
        super()._write_file(f, app)


class AltairPlot(BasePlot):
    """Creates a vega-light chart from Altair Chart / pdvega Axes object."""

    mimetype = "application/vnd.vegalite.v3+json"
    ext = ".vl.json"
    fig_type = SchemaBase

    def write_file(self, f: TextIO, chart: SchemaBase):
        json.dump(chart.to_dict(), f)


class PlotlyPlot(BasePlot):
    """Creates a plotly graph from a figure object"""

    mimetype = "application/vnd.plotly.v1+json"
    ext = ".pl.json"
    fig_type = PFigure

    def write_file(self, f: TextIO, chart: PFigure):
        json.dump(chart.to_json(), f)


class FoliumPlot(BasePlot):
    mimetype = "application/vnd.folium+html"
    ext = ".fl"
    fig_type = Map

    def write_file(self, f: BinaryIO, m: Map):
        html: str = m.get_root().render()
        f.write(html)


# register all the plot types
plots = [
    StylerTablePlot,
    DataFrameTablePlot,
    BokehPlot,
    BokehLayoutPlot,
    AltairPlot,
    PlotlyPlot,
    FoliumPlot,
    MatplotFigurePlot,
    MatplotAxesPlot,
    MatplotNDArrayPlot,
    PickleWriter,
]


@singledispatch
def get_plotter(figure: Any, default_to_json: bool) -> BasePlot:
    # The base writer is either a pickle writer or JSON writer.
    return BaseJsonWriter() if default_to_json else BasePickleWriter()


for p in plots:
    get_plotter.register(p.fig_type, lambda _, p=p, default_to_json=False: p())


def save(figure: Any, default_to_json: bool = False) -> DPTmpFile:
    return get_plotter(figure, default_to_json=default_to_json).write(figure)
