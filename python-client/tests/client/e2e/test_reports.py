import json
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import pytest
import requests

import datapane as dp
from datapane.client import config as c

from ..local.api.test_reports import gen_legacy_report_simple, gen_report_complex_with_files, gen_report_simple
from .common import check_name, deletable, gen_description, gen_df, gen_name, gen_plot

pytestmark = pytest.mark.usefixtures("dp_login")


def test_legacy_report_with_single_file(datadir: Path):
    """Ensure deprecated Report.save and Report.upload work as expected"""
    report = gen_report_complex_with_files(datadir, single_file=True, local_report=True)
    # Test we can save then upload
    report.save(str(datadir / "test_report.html"))
    report.upload(name=gen_name(), description="DESCRIPTION")
    with deletable(report):
        pass


def test_legacy_report_simple():
    """Ensure deprecated dp.Report works as expected"""
    report = gen_legacy_report_simple()
    report.upload(name=gen_name(), description="DESCRIPTION", project="default")
    with deletable(report):
        pass


def test_report_simple():
    report = gen_report_simple()
    dp.upload(report, name=gen_name(), description="DESCRIPTION", project="default")
    with deletable(report):
        pass


def test_report_update_metadata():
    report = gen_report_simple()
    name = gen_name()

    props = dict(description="TEST-DESCRIPTION", source_url="https://www.github.com/datapane", tags=["a", "b"])
    if c.config.is_public:
        props["publicly_visible"] = True

    same_props = (
        "url",
        "id",
        "author",
        "web_url",
        "width",
        "report_files",
        "num_blocks",
    )

    dp.upload(report, name, **props)

    with deletable(report):

        def check_props():
            assert report.dto["description"] == props["description"]
            assert report.dto["source_url"] == props["source_url"]
            assert sorted(report.dto["tags"]) == sorted(props["tags"])
            assert report.dto["publicly_visible"] == props.get("publicly_visible", False)

        check_props()
        orig_dto = deepcopy(report.dto)

        # overwrite and upload again, using defaults
        dp.upload(report, name, overwrite=True)

        # check specified props haven't changed
        check_props()

        # check other elements haven't changed?
        for x in same_props:
            assert report.dto[x] == orig_dto[x]


def test_report_visibility():
    report = gen_report_simple()
    name = gen_name()

    dp.upload(report, name)

    with deletable(report):

        def assert_visibility(visible: bool):
            assert report.dto["publicly_visible"] is visible

        # check initial report with no specified visibility defaults to `False`
        assert_visibility(False)

        # overwrite and upload again, setting public visibility
        dp.upload(report, name, overwrite=True, publicly_visible=True)

        # check updated report is publicly visible
        assert_visibility(True)

        # overwrite and upload, leaving visibility unspecified
        dp.upload(report, name, overwrite=True)

        # check visibility is unchanged
        assert_visibility(True)


def test_report_with_single_file(datadir: Path):
    report = gen_report_complex_with_files(datadir, single_file=True, local_report=True)
    # Test we can save, build then upload
    dp.save_report(report, str(datadir / "test_report.html"))
    dp.build(report, name="test_report", dest=datadir)
    dp.upload(report, name=gen_name(), description="DESCRIPTION")
    with deletable(report):
        pass


def test_report_with_files(datadir: Path):
    report = gen_report_complex_with_files(datadir)
    dp.upload(report, name=gen_name(), description="DESCRIPTION")
    with deletable(report):
        pass


def test_report_update_with_files(datadir: Path):
    report = gen_report_complex_with_files(datadir)
    dp.upload(report, name=gen_name(), description="DESCRIPTION")
    with deletable(report):
        doc_a = report.document
        dp.upload(report, name=gen_name(), description="DESCRIPTION")
        doc_b = report.document
        assert doc_a == doc_b


def test_demo_report():
    report = dp.builtins.build_demo_report()
    dp.upload(report, name=gen_name(), description="DESCRIPTION")
    with deletable(report):
        pass


def test_full_report(tmp_path: Path, shared_datadir: Path, monkeypatch):
    monkeypatch.chdir(shared_datadir)
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
    file_asset = dp.Attachment(file=fn)
    plot_asset = dp.Plot(data=plot)
    list_asset = dp.Attachment(data=lis)
    media_asset = dp.Media(file=Path("datapane-logo.png"))
    df_asset = dp.DataTable(df=df, caption="Our Dataframe")
    divider = dp.Divider()
    empty_block = dp.Empty(name="empty-block")
    dp_report = dp.App(m, file_asset, df_asset, plot_asset, list_asset, divider, empty_block, media_asset)
    dp.upload(dp_report, name=name, description=description, source_url=source_url)

    with deletable(dp_report):
        # are the fields ok
        check_name(dp_report, name)
        assert dp_report.description == description
        assert dp_report.source_url == source_url
        assert len(dp_report.pages[0].blocks) == 8

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

    with deletable(dp.App(tz_t, index_t, df_desc_t, df_desc_2_t)) as dp_report:
        dp.upload(dp_report, name=gen_name())

        # NOTE - as above, downloading embedded assets from a report currently not supported in API
        # check_df_equal(tz_df, tz_t.download_df())
        # check_df_equal(index_df, index_t.download_df())
        # check_df_equal(df_desc, df_desc_t.download_df())
        # check_df_equal(df_desc_2, df_desc_2_t.download_df())


def test_report_project():
    # TODO - add additional checks like uploading to a report the user isn't a member of
    # i.e. both in the same team, or another project in a diff team
    # update a report that will automatically be added to the default project
    report = gen_report_simple()
    dp.upload(report, name="test_report_project")
    # check if the project name is default
    with deletable(report):
        assert report.project == "default"

    # explicitly add to the project
    dp.upload(report, name="test_report_project_2", project="default")
    with deletable(report):
        assert report.project == "default"

    # test adding report to a group that doesn't exist
    report2 = gen_report_simple()

    with pytest.raises(requests.HTTPError) as e:
        dp.upload(report2, name="test_wrong_project", project="wrong-project")
        assert e.response.status_code == 400
