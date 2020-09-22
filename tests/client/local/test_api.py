"""Tests for the API that can run locally (due to design or mocked out)"""
import os
from pathlib import Path

import altair as alt
import pytest

import datapane as dp
from datapane.client import api
from datapane.common.report import validate_report_doc

from ..e2e.common import gen_df


def test_params_loading(datadir: Path):
    """Test that the API allows loading params from the datapane file"""
    config_fn = datadir / "datapane.yaml"
    initial_vals = dict(p1="a", p3=3)

    assert len(dp.Params) == 0

    # load some values
    api._reset_runtime(initial_vals)
    assert len(dp.Params) == 2
    assert dp.Params["p1"] == initial_vals["p1"]

    # clear and load again
    api._reset_runtime({})
    assert len(dp.Params) == 0
    api._reset_runtime(initial_vals)

    # load from file
    dp.Params.load_defaults(config_fn=config_fn)
    # ensure values are merged
    assert len(dp.Params) == 3
    assert dp.Params["p1"] == "hello"
    assert dp.Params["p2"] == 4
    assert dp.Params["p3"] == initial_vals["p3"]


def gen_report_simple() -> dp.Report:
    return dp.Report(
        blocks=[
            dp.Markdown(text="# Test markdown block <hello/> \n Test **content**", id="test-id-1"),
            "Simple string Markdown",
        ]
    )


def gen_report_with_files(datadir: Path, single_file: bool = False) -> dp.Report:
    # Asset tests
    lis = [1, 2, 3]
    df = gen_df(10000)
    md_block = dp.Markdown(text="# Test markdown block <hello/> \n Test **content**")

    list_asset = dp.File(data=lis, name="List Asset", is_json=True)

    img_asset = dp.File(file=datadir / "datapane-logo.png")

    plot_asset = dp.Plot(
        data=alt.Chart(gen_df()).mark_line().encode(x="x", y="y"), caption="Plot Asset"
    )

    df_asset = dp.Table(df=df, caption="Test Dataframe Table")

    pivot_asset = dp.Table(df=df, caption="Test Dataframe PivotTable", can_pivot=True)

    if single_file:
        return dp.Report(dp.Blocks([md_block, plot_asset]))
    else:
        return dp.Report(list_asset, img_asset, df_asset, md_block, plot_asset, pivot_asset)


def test_gen_report_simple():
    report = gen_report_simple()
    report_str, attachments = report._gen_report(
        embedded=False, title="TITLE", description="DESCRIPTION"
    )

    # print(report_str)
    assert len(attachments) == 0
    assert len(report.top_block.blocks) == 2
    assert report.top_block.blocks[0].id == "test-id-1"
    assert report.top_block.blocks[1].id == "block-2"
    assert isinstance(report.top_block.blocks[1], dp.Markdown)
    assert validate_report_doc(xml_str=report_str)


def test_gen_report_with_files(datadir: Path):
    report = gen_report_with_files(datadir)
    report_str, attachments = report._gen_report(
        embedded=False, title="TITLE", description="DESCRIPTION"
    )

    # print(report_str)
    assert len(attachments) == 5
    assert validate_report_doc(xml_str=report_str)


@pytest.mark.skipif("CI" in os.environ, reason="Currently depends on building fe-components first")
def test_local_report_simple(datadir: Path, monkeypatch):
    monkeypatch.chdir(datadir)
    report = gen_report_simple()
    report.save(path="test_out.html")


@pytest.mark.skipif("CI" in os.environ, reason="Currently depends on building fe-components first")
def test_local_report_with_files(datadir: Path, monkeypatch):
    monkeypatch.chdir(datadir)
    report = gen_report_with_files(datadir)
    report.save(path="test_out.html")
