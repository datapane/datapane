import json
from pathlib import Path
from typing import Optional

import altair as alt
import pandas as pd
import pytest
from tests import check_df_equal

import datapane as dp
from datapane.client import api
from datapane.common import temp_fname
from datapane.common.df_processor import convert_csv_pd

from .common import gen_df, gen_headline, gen_name

pytestmark = pytest.mark.usefixtures("dp_login")


def test_report():
    dp_report: Optional[dp.Report] = None
    try:
        df = gen_df()
        name = gen_name()
        headline = gen_headline()

        # create a basic report
        m = api.Markdown(content="hello world!!")

        # Asset tests
        lis = [1, 2, 3]
        json_list: str = json.dumps(lis)
        plot = alt.Chart(df).mark_line().encode(x="x", y="y")

        # create the DP
        with temp_fname(".json") as fn:
            fn = Path(fn)
            fn.write_text(json_list)
            file_asset = api.Asset.upload_file(file=fn)
            json_asset = api.Asset.upload_obj(data=json_list, is_json=True)
            plot_asset = api.Asset.upload_obj(data=plot)
            list_asset = api.Asset.upload_obj(data=lis, is_json=True)
            df_asset = api.Asset.upload_df(df=df)
            dp_report = api.Report(
                m, file_asset, df_asset, json_asset, plot_asset, list_asset, name=name
            )
            dp_report.publish(headline=headline)
            # make sure the user file wasn't deleted during /tmp/ cleanup
            assert file_asset.file.exists()

        # are the fields ok
        assert dp_report.headline == headline
        assert len(dp_report.blocks) == 6

        # --- FILE ASSET --- #
        # [1, 2, 3] uploaded via a JSON file

        with temp_fname(".json") as fn:
            fn = Path(fn)
            file_asset.download_file(fn)
            asset1 = fn.read_text()
            assert asset1 == json_list

        # check the file asset via download_obj
        loaded_file = file_asset.download_obj()
        assert loaded_file == lis

        # --- JSON ASSET --- #
        # [1, 2, 3] uploaded as a JSON string

        # check the json asset via download_file
        with temp_fname(".json") as fn:
            fn = Path(fn)
            json_asset.download_file(fn)
            assert fn.read_text() == json_list

        # check the json asset via download_obj
        loaded_json = json_asset.download_obj()
        assert loaded_json == lis

        # --- LIST ASSET --- #
        # [1, 2, 3] uploaded as a native Python list

        # check the list asset via download_file
        with temp_fname(".json") as fn:
            fn = Path(fn)
            list_asset.download_file(fn)
            assert fn.read_text() == json_list

        # check the list asset via download_obj
        loaded_list = list_asset.download_obj()
        assert loaded_list == lis

        # --- PLOT ASSET --- #

        # check the plot asset via download_file
        with temp_fname(".json") as fn:
            fn = Path(fn)
            plot_asset.download_file(fn)
            assert json.loads(fn.read_text()) == plot.to_dict()

        # check the plot asset via download_obj
        loaded_obj = plot_asset.download_obj()
        assert loaded_obj == plot.to_dict()

        # --- DF ASSET --- #

        # check the df asset
        df1 = df_asset.download_df()
        check_df_equal(df1, df)

    finally:
        # delete the dp
        if dp_report:
            dp_report.delete()
            with pytest.raises(api.HTTPError) as _:
                _ = api.Report.get(dp_report.name)


def test_complex_df_report():
    """Test our dataframe importing with types of DFs user's upload"""
    tz_df = convert_csv_pd(
        """
        date,datetime,datetime_tz
        2017-01-10,2017-01-21T23:10:24,2020-03-23T00:00:00.000Z
        2017-01-11,2017-01-23T23:01:24,2020-04-23T00:00:00.000Z
    """
    )

    raw_data = {
        "first_name": ["Jason", "Molly", "Tina", "Jake", "Amy"],
        "last_name": ["Miller", "Jacobson", "Ali", "Milner", "Cooze"],
        "age": [42, 52, 36, 24, 73],
        "preTestScore": [4, 24, 31, 2, 3],
        "postTestScore": [25, 94, 57, 62, 70],
    }
    index_df = pd.DataFrame(
        raw_data, columns=["first_name", "last_name", "age", "preTestScore", "postTestScore"]
    )
    df_desc = index_df.describe()
    df_desc_2 = df_desc.reset_index()

    dp_report: Optional[dp.Report] = None
    try:
        tz_t = dp.Table.create(tz_df)
        index_t = dp.Table.create(index_df)
        df_desc_t = dp.Table.create(df_desc)
        df_desc_2_t = dp.Table.create(df_desc_2)

        dp_report = dp.Report(tz_t, index_t, df_desc_t, df_desc_2_t, name=gen_name())
        dp_report.publish()

        check_df_equal(tz_df, tz_t.download_df())
        check_df_equal(index_df, index_t.download_df())
        check_df_equal(df_desc, df_desc_t.download_df())
        check_df_equal(df_desc_2, df_desc_2_t.download_df())
    finally:
        if dp_report:
            dp_report.delete()


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
