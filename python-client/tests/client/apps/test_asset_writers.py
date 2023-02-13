from io import BytesIO

import altair as alt
import folium
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as p_go
import pytest
from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from pandas.io.formats.style import Styler

from datapane.view import asset_writers as aw
from datapane.view.xml_visitor import AssetWriterP

data = pd.DataFrame({"x": np.random.randn(20), "y": np.random.randn(20)})


def test_save_matplotlib():
    pd.set_option("plotting.backend", "matplotlib")
    fig, ax = plt.subplots()
    data.plot.scatter("x", "y", ax=ax)

    writer: AssetWriterP = aw.PlotWriter()
    writer.write_file(fig, BytesIO())
    writer.write_file(ax, BytesIO())
    writer.write_file(data.hist(), BytesIO())


def test_save_bokeh():
    source = ColumnDataSource(data)
    p = figure()
    p.circle(x="x", y="y", source=source)

    writer: AssetWriterP = aw.PlotWriter()
    writer.write_file(p, BytesIO())
    assert writer.get_meta(p).mime == "application/vnd.bokeh.show+json"


def test_save_bokeh_layout():
    source = ColumnDataSource(data)
    p = figure()
    p.circle(x="x", y="y", source=source)

    writer: AssetWriterP = aw.PlotWriter()
    writer.write_file(column(p, p), BytesIO())
    assert writer.get_meta(p).mime == "application/vnd.bokeh.show+json"


def test_save_altair():
    plot = alt.Chart(data).mark_bar().encode(y="y", x="x")

    writer: AssetWriterP = aw.PlotWriter()
    writer.write_file(plot, BytesIO())


def test_save_folium():
    _map = folium.Map(location=[45.372, -121.6972], zoom_start=12, tiles="Stamen Terrain")
    writer: AssetWriterP = aw.PlotWriter()
    writer.write_file(_map, BytesIO())


def test_save_plotly():
    fig = p_go.Figure()
    fig.add_trace(p_go.Scatter(x=[0, 1, 2, 3, 4, 5], y=[1.5, 1, 1.3, 0.7, 0.8, 0.9]))
    writer: AssetWriterP = aw.PlotWriter()
    writer.write_file(fig, BytesIO())


# NOTE - test disabled until pip release of altair_pandas - however should work if altair test passes
@pytest.mark.skip(reason="altair_pandas not yet supported")
def test_save_altair_pandas():
    pd.set_option("plotting.backend", "altair")  # Installing altair_pandas registers this.
    plot = data.plot.scatter("x", "y")
    writer: AssetWriterP = aw.PlotWriter()
    writer.write_file(plot, BytesIO())


# NOTE - test disabled updated pip release of pdvega that tracks git upstream - however should work if altair test passes
@pytest.mark.skip(reason="pdvega not yet supported")
def test_save_pdvega():
    import pdvega  # noqa: F401

    plot = data.vgplot.scatter("x", "y")
    writer: AssetWriterP = aw.PlotWriter()
    writer.write_file(plot, BytesIO())


def test_save_table():
    # tests saving a DF directly to a html file
    writer: AssetWriterP = aw.DataTableWriter()
    writer.write_file(data, BytesIO())
    # save styled table
    writer: AssetWriterP = aw.HTMLTableWriter()
    writer.write_file(Styler(data), BytesIO())


def test_save_attachment():
    # tests saving to a pickle
    writer: AssetWriterP = aw.AttachmentWriter()
    writer.write_file(data, BytesIO())
    assert writer.get_meta(data).ext == ".pkl"

    # save saving as json
    f = BytesIO()
    data1 = "[1, 2, 3]"
    writer: AssetWriterP = aw.AttachmentWriter()
    writer.write_file(data1, f)
    assert writer.get_meta(data1).ext == ".json"
    assert f.getvalue().decode() == data1
