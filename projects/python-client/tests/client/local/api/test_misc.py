"""Tests for the API that can run locally (due to design or mocked out)"""
from pathlib import Path

import pytest
from glom import glom

import datapane as dp
from datapane.client import DPError

from ....client.e2e.common import gen_df, gen_plot
from .test_reports import element_to_str


def test_markdown_format(datadir: Path):
    text = """
# My wicked markdown

{{plot}}

As above we do ...

{{select}}

Here's the dataset used...

{{}}
"""

    table_asset = gen_df()
    plot_asset = dp.Plot(data=gen_plot(), caption="Plot Asset")
    select_asset = dp.Select(dp.Text("Hello"), "World")

    # missing context
    with pytest.raises(DPError):
        dp.Text(text).format(table_asset, plot=plot_asset, select1=select_asset)
    with pytest.raises(DPError):
        dp.Text(text).format(plot=plot_asset, select=select_asset)

    # test string
    group = dp.Text(text).format(table_asset, plot=plot_asset, select=select_asset)
    assert isinstance(group, dp.Group)
    assert glom(group, ("blocks", ["_tag"])) == ["Text", "Plot", "Text", "Select", "Text", "Table"]

    # test file
    group = dp.Text(file=datadir / "report.md").format(table_asset, plot=plot_asset, select=select_asset)
    assert isinstance(group, dp.Group)
    assert glom(group, ("blocks", ["_tag"])) == ["Text", "Plot", "Text", "Select", "Text", "Table"]
    assert "file-input" in element_to_str(group)
    assert "file-input" in glom(group, "blocks.0.content")
