"""Tests for the API that can run locally (due to design or mocked out)"""
from pathlib import Path

import altair as alt
from tests.client.server.common import gen_df

import datapane as dp
from datapane.client import api
from datapane.client.api import reset_api


def test_params_loading(datadir: Path):
    """Test that the API allows loading params from the datapane file"""
    config_fn = datadir / "datapane.yaml"
    initial_vals = dict(p1="a", p3=3)

    assert len(dp.Params) == 0

    # load some values
    reset_api(initial_vals)
    assert len(dp.Params) == 2
    assert dp.Params["p1"] == initial_vals["p1"]

    # clear and load again
    reset_api({})
    assert len(dp.Params) == 0
    reset_api(initial_vals)

    # load from file
    dp.Params.load_defaults(config_fn=config_fn)
    # ensure values are merged
    assert len(dp.Params) == 3
    assert dp.Params["p1"] == "hello"
    assert dp.Params["p2"] == 4
    assert dp.Params["p3"] == initial_vals["p3"]


def test_local_report():
    try:
        # Asset tests
        lis = [1, 2, 3]
        df = gen_df(10000)
        md_block = api.Markdown(content="# Test markdown block \n Test **content**")
        list_asset = api.Asset.upload_obj(data=lis, title="List Asset", is_json=True)
        # img_asset = api.Asset.upload_file(file=Path("/path/to/image.png"))
        plot_asset = api.Asset.upload_obj(
            data=alt.Chart(gen_df()).mark_line().encode(x="x", y="y"), title="Plot Asset"
        )
        df_asset = api.Asset.upload_df(df=df, title="Test Dataframe")
        report = api.Report(list_asset, df_asset, md_block, plot_asset, name="local_report")
        report.save(path="test_out.html")
    finally:
        x = Path("test_out.html")
        if x.exists():
            x.unlink()
