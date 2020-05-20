from pathlib import Path

import altair as alt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

from datapane.client.files import show

data = pd.DataFrame({"x": np.random.randn(20), "y": np.random.randn(20)})


def test_save_base(tmp_path: Path, monkeypatch):
    # absolute filename tests
    # test with no filename
    show(data, output_dir=tmp_path)
    show(data, output_dir=tmp_path)
    # replace filename ext
    show(data, filename="test_table.pdf", output_dir=tmp_path)

    # relative filename tests
    monkeypatch.chdir(tmp_path)
    # test with no filename
    show(data)
    show(data)
    # replace filename ext
    show(data, filename="test_table.pdf")
    show(data, filename=tmp_path / "test_table_1.pdf")


def test_save_matplotlib(tmp_path: Path):
    pd.set_option("plotting.backend", "matplotlib")
    fig, ax = plt.subplots()
    data.plot.scatter("x", "y", ax=ax)
    show(fig, tmp_path / "test_matplotlib.png")
    # test svg default
    show(fig, tmp_path / "test_matplotlib")
    # test save axes only
    show(ax, output_dir=tmp_path)
    # test save ndarray
    show(data.hist(), output_dir=tmp_path)


def test_save_bokeh(tmp_path: Path):
    source = ColumnDataSource(data)
    p = figure()
    p.circle(x="x", y="y", source=source)
    show(p, tmp_path / "test_bokeh")


def test_save_altair(tmp_path: Path):
    plot = alt.Chart(data).mark_bar().encode(y="y", x="x")
    show(plot, tmp_path / "test_altair")


# NOTE - test disabled until pip release of altair_pandas - however should work if altair test passes
# def test_save_altair_pandas(tmp_path: Path):
#     pd.set_option("plotting.backend", "altair")  # Installing altair_pandas registers this.
#     plot = data.plot.scatter("x", "y")
#     show(plot, tmp_path / "test_altair_pandas")


# NOTE - test disabled updated pip release of pdvega that tracks git upstream - however should work if altair test passes
# def test_save_pdvega(tmp_path: Path):
#     import pdvega  # noqa: F401
#
#     plot = data.vgplot.scatter("x", "y")
#     show(plot, tmp_path / "test_pdvega")


def test_save_table(tmp_path: Path):
    show(data, tmp_path / "test_table")
