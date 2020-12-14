from pathlib import Path

import altair as alt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from pandas.io.formats.style import Styler

from datapane.client.files import save

data = pd.DataFrame({"x": np.random.randn(20), "y": np.random.randn(20)})


def test_save_base(tmp_path: Path, monkeypatch):
    # absolute filename tests
    # test with no filename
    save(data)
    save(data)

    # relative filename tests
    monkeypatch.chdir(tmp_path)
    save(data)


def test_save_matplotlib(tmp_path: Path):
    pd.set_option("plotting.backend", "matplotlib")
    fig, ax = plt.subplots()
    data.plot.scatter("x", "y", ax=ax)
    # test svg default
    save(fig)
    # test save axes only
    save(ax)
    # test save ndarray
    save(data.hist())


def test_save_bokeh(tmp_path: Path):
    source = ColumnDataSource(data)
    p = figure()
    p.circle(x="x", y="y", source=source)
    save(p)


def test_save_bokeh_layout(tmp_path: Path):
    source = ColumnDataSource(data)
    p = figure()
    p.circle(x="x", y="y", source=source)
    save(column(p, p))


def test_save_altair(tmp_path: Path):
    plot = alt.Chart(data).mark_bar().encode(y="y", x="x")
    save(plot)


# NOTE - test disabled until pip release of altair_pandas - however should work if altair test passes
@pytest.mark.skip(reason="altair_pandas not yet supported")
def test_save_altair_pandas(tmp_path: Path):
    pd.set_option("plotting.backend", "altair")  # Installing altair_pandas registers this.
    plot = data.plot.scatter("x", "y")
    save(plot)


# NOTE - test disabled updated pip release of pdvega that tracks git upstream - however should work if altair test passes
@pytest.mark.skip(reason="pdvega not yet supported")
def test_save_pdvega(tmp_path: Path):
    import pdvega  # noqa: F401

    plot = data.vgplot.scatter("x", "y")
    save(plot)


def test_save_table(tmp_path: Path):
    # tests saving a DF directly to a html file
    save(data)
    # save styled table
    save(Styler(data))
