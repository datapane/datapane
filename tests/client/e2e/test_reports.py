import json
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import pytest
import requests
from furl import furl
from lxml import etree

import datapane as dp
from datapane.client import config as c

from ..local.api.test_reports import gen_report_complex_with_files, gen_report_simple
from .common import check_name, deletable, gen_description, gen_df, gen_name, gen_plot

pytestmark = pytest.mark.usefixtures("dp_login")


def test_report_simple():
    report = gen_report_simple()
    report.upload(name="TEST", description="DESCRIPTION")
    with deletable(report):
        ...


@pytest.mark.org
def test_report_simple_permissions():
    # TODO(e2e-move) - already moved - obsolete
    report = gen_report_simple()
    report.upload(name="TEST", description="DESCRIPTION")
    with deletable(report):
        # check we can't access api & web urls
        r = requests.get(url=report.url)
        assert r.status_code == 403
        r = requests.get(url=report.web_url)
        assert r.history[0].status_code == 302  # redirect to login
        assert r.status_code == 200
        # check we can't embed a private report
        f = furl(origin=c.config.server, path="api/oembed/", args=dict(url=report.web_url))
        r = requests.get(url=f.url)
        assert r.status_code in [400, 401, 403]


def test_report_update_metadata():
    report = gen_report_simple()
    name = "TEST-META"
    props = dict(
        description="TEST-DESCRIPTION",
        source_url="https://www.github.com/datapane",
        tags=["a", "b"],
    )

    same_props = (
        "url",
        "id",
        "owner",
        "username",
        "web_url",
        "embed_url",
        "type",
        "files",
        "num_blocks",
    )

    report.upload(name, **props)

    def check(x, y):
        assert x == y or sorted(x) == sorted(y)

    with deletable(report):
        for (k, v) in props.items():
            check(report.dto[k], v)
        orig_dto = deepcopy(report.dto)

        # upload again, using defaults
        report.upload(name)
        # check props haven't changed
        for (k, v) in props.items():
            check(report.dto[k], v)

        # check other elements haven't changed?
        for x in same_props:
            check(report.dto[x], orig_dto[x])


def test_report_with_single_file(datadir: Path):
    report = gen_report_complex_with_files(datadir, single_file=True, local_report=True)
    # Test we can save then upload
    report.save(str(datadir / "test_report.html"))
    report.upload(name="TEST", description="DESCRIPTION")
    with deletable(report):
        ...


def test_report_with_files(datadir: Path):
    report = gen_report_complex_with_files(datadir)
    report.upload(name="TEST", description="DESCRIPTION")
    with deletable(report):
        ...


def test_demo_report():
    report = dp.templates.build_demo_report()
    report.upload(name="TEST", description="DESCRIPTION")
    with deletable(report):
        ...


def test_full_report(tmp_path: Path):
    df = gen_df()
    name = gen_name()
    description = gen_description()
    source_url = "https://github.com/datapane/datapane"
    # create a basic report
    m = dp.Text("hello world!!")

    # Asset tests
    lis = [1, 2, 3]
    json_list: str = json.dumps(lis)
    plot = gen_plot()

    # create the DP
    fn = tmp_path / "json_list.json"
    fn.write_text(data=json_list)
    file_asset = dp.File(file=fn)
    json_asset = dp.File(data=json_list, is_json=True)
    plot_asset = dp.Plot(data=plot)
    list_asset = dp.File(data=lis, is_json=True)
    df_asset = dp.DataTable(df=df, caption="Our Dataframe")
    dp_report = dp.Report(m, file_asset, df_asset, json_asset, plot_asset, list_asset)
    dp_report.upload(name=name, description=description, source_url=source_url)

    with deletable(dp_report):
        # are the fields ok
        check_name(dp_report, name)
        assert dp_report.description == description
        assert dp_report.source_url == source_url
        assert len(dp_report.pages[0].blocks[0].blocks) == 6

        # NOTE - Asset objects no longer exists - thus below tests can't be supported
        # we do store `id` on the object, that can be used to pull out from the XML report
        # but currently unsupported

        # # --- FILE ASSET --- #
        # # [1, 2, 3] uploaded via a JSON file
        #
        # fn = tmpdir / "tmp1.json"
        # file_asset.download_file(fn)
        # asset1 = fn.read_text()
        # assert asset1 == json_list
        #
        # # check the file asset via download_obj
        # loaded_file = file_asset.download_obj()
        # assert loaded_file == lis
        #
        # # --- JSON ASSET --- #
        # # [1, 2, 3] uploaded as a JSON string
        #
        # # check the json asset via download_file
        # with temp_fname(".json") as fn:
        #     fn = Path(fn)
        #     json_asset.download_file(fn)
        #     assert fn.read_text() == json_list
        #
        # # check the json asset via download_obj
        # loaded_json = json_asset.download_obj()
        # assert loaded_json == lis
        #
        # # --- LIST ASSET --- #
        # # [1, 2, 3] uploaded as a native Python list
        #
        # # check the list asset via download_file
        # with temp_fname(".json") as fn:
        #     fn = Path(fn)
        #     list_asset.download_file(fn)
        #     assert fn.read_text() == json_list
        #
        # # check the list asset via download_obj
        # loaded_list = list_asset.download_obj()
        # assert loaded_list == lis
        #
        # # --- PLOT ASSET --- #
        #
        # # check the plot asset via download_file
        # with temp_fname(".json") as fn:
        #     fn = Path(fn)
        #     plot_asset.download_file(fn)
        #     assert json.loads(fn.read_text()) == plot.to_dict()
        #
        # # check the plot asset via download_obj
        # loaded_obj = plot_asset.download_obj()
        # assert loaded_obj == plot.to_dict()
        #
        # # --- DF ASSET --- #
        #
        # # check the df asset
        # df1 = df_asset.download_df()
        # check_df_equal(df1, df)


def test_complex_df_report():
    """Test our dataframe importing with types of DFs user's upload"""
    tz_df = pd.DataFrame(
        dict(
            duration_col=[timedelta(seconds=x) for x in range(30)],
            date_col=[date.today() for _ in range(30)],
            datetime_col=[datetime.utcnow() for _ in range(30)],
            datetimez_col=[datetime.now(timezone.utc) for _ in range(30)],
        )
    )

    raw_data = {
        "first_name": ["Jason", "Molly", "Tina", "Jake", "Amy"],
        "last_name": ["Miller", "Jacobson", "Ali", "Milner", "Cooze"],
        "age": [42, 52, 36, 24, 73],
        "preTestScore": [4, 24, 31, 2, 3],
        "postTestScore": [25, 94, 57, 62, 70],
    }
    index_df = pd.DataFrame(raw_data, columns=["first_name", "last_name", "age", "preTestScore", "postTestScore"])
    df_desc = index_df.describe()
    df_desc_2 = df_desc.reset_index()

    tz_t = dp.DataTable(tz_df)
    index_t = dp.DataTable(index_df)
    df_desc_t = dp.DataTable(df_desc)
    df_desc_2_t = dp.DataTable(df_desc_2)

    with deletable(dp.Report(tz_t, index_t, df_desc_t, df_desc_2_t)) as dp_report:
        dp_report.upload(name=gen_name())

        # NOTE - as above, downloading embedded assets from a report currently not supported in API
        # check_df_equal(tz_df, tz_t.download_df())
        # check_df_equal(index_df, index_t.download_df())
        # check_df_equal(df_desc, df_desc_t.download_df())
        # check_df_equal(df_desc_2, df_desc_2_t.download_df())


@pytest.mark.org
def test_report_group():
    report = gen_report_simple()
    report.upload(name="test_report_group")
    # check if the group name is default
    with deletable(report):
        assert report.group == "default"

    # test adding report to a group that doesn't exist
    report2 = gen_report_simple()
    try:
        report2.upload(name="test_wrong_group", group="wrong-group")
    except requests.HTTPError as e:
        assert e.response.status_code == 400


###############################################################################
# TextReport
def _calc_text_blocks(report: dp.TextReport, expected_blocks: int):
    r = etree.fromstring(report.api_document)
    assert r.xpath("count(//Group[1]/*)") == expected_blocks


def test_text_report():
    # a simple report
    report = dp.TextReport("test").upload(name="Test")
    with deletable(report):
        # inc Page and Group blocks
        _calc_text_blocks(report, 1)

        # overwrite via name
        report = dp.TextReport("Text-1", "Text-2").upload(name="Test")
        _calc_text_blocks(report, 2)

        # overwrite via id
        report = dp.TextReport("Text-1", "Text-2", "Text-3").upload(id=report.id)
        _calc_text_blocks(report, 3)

        # get report by id
        report_1 = dp.TextReport.by_id(report.id)
        assert report.id == report_1.id
        assert report.num_blocks == report_1.num_blocks


def test_text_report_files():
    s_df = gen_df()
    b_df = gen_df(1000)
    plot_asset = dp.Plot(data=gen_plot(), caption="Plot Asset")

    report = dp.TextReport(s_df, b_df, plot_asset).upload(name="Test")
    with deletable(report):
        _calc_text_blocks(report, 3)

        report = dp.TextReport(text="Text", s_df=s_df, b_df=b_df, plot=plot_asset).upload(name="Test")
        _calc_text_blocks(report, 4)
