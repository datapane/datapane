"""Tests for the API that can run locally (due to design or mocked out)"""
import os
from pathlib import Path

import altair as alt
import pytest
from dominate.tags import h2
from glom import glom
from lxml import etree
from lxml.etree import DocumentInvalid

import datapane as dp
from datapane.client import DPError, api
from datapane.client.api.report.blocks import BaseElement
from datapane.client.api.report.core import BuilderState
from datapane.common.report import validate_report_doc

from ..e2e.common import gen_df

md_block_id = dp.Text(text="# Test markdown block <hello/> \n Test **content**", id="test-id-1")
md_block = dp.Text(text="# Test markdown block <hello/> \n Test **content**")
str_md_block = "Simple string Markdown"


def element_to_str(e: BaseElement) -> str:
    s = e._to_xml(BuilderState())
    return etree.tounicode(s.elements[0], pretty_print=True)


def num_blocks(report_str: str) -> int:
    x = "count(/Report/Main//*[not(self::Caption)])"
    return int(etree.fromstring(report_str).xpath(x))


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
    plot_asset = dp.Plot(data=alt.Chart(gen_df()).mark_line().encode(x="x", y="y"), caption="Plot Asset")
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


################################################################################
# Reporting
def assert_report(report: dp.Report, expected_attachments: int = None, expected_num_blocks: int = None):
    report_str, attachments = report._gen_report(embedded=False, title="TITLE", description="DESCRIPTION")
    # print(report_str)
    if expected_attachments:
        assert len(attachments) == expected_attachments
    if expected_num_blocks:
        assert num_blocks(report_str) == expected_num_blocks
    assert validate_report_doc(xml_str=report_str)
    return (report_str, attachments)


def gen_report_simple() -> dp.Report:
    return dp.Report(
        blocks=[
            md_block_id,
            str_md_block,
        ]
    )


def gen_report_complex_no_files() -> dp.Report:
    """Generate a complex layout report with simple elements"""
    select = dp.Select(blocks=[md_block, md_block], type=dp.SelectType.TABS)
    group = dp.Group(md_block, md_block, columns=2)

    return dp.Report(
        dp.Page(
            blocks=[
                dp.Group(md_block, md_block, columns=2),
                dp.Select(blocks=[md_block, group], type=dp.SelectType.DROPDOWN),
            ],
            label="Page Uno",
        ),
        dp.Page(
            blocks=[
                dp.Group(select, select, columns=2),
                dp.Select(blocks=[md_block, md_block, md_block], type=dp.SelectType.TABS),
            ],
            label="Page Duo",
        ),
        dp.Page(
            blocks=[
                dp.Group(group, group, columns=2),
                dp.Select(blocks=[select, select], type=dp.SelectType.TABS),
            ],
            label="Page Tres",
        ),
    )


def gen_report_complex_with_files(datadir: Path, single_file: bool = False) -> dp.Report:
    # Asset tests
    lis = [1, 2, 3]
    small_df = gen_df()
    big_df = gen_df(10000)

    # text
    # md_block
    html_block = dp.HTML(html="<h1>Hello World</h1>")
    html_block_1 = dp.HTML(html=h2("Hello World"))
    code_block = dp.Code(code="print('hello')", language="python")
    big_number = dp.BigNumber(heading="Tests written", value=1234)
    big_number_1 = dp.BigNumber(heading="Real Tests written :)", value=11, change=2, is_upward_change=True)

    # assets
    plot_asset = dp.Plot(data=alt.Chart(gen_df()).mark_line().encode(x="x", y="y"), caption="Plot Asset")
    list_asset = dp.File(data=lis, name="List Asset", is_json=True)
    img_asset = dp.File(file=datadir / "datapane-logo.png")

    # tables
    table_asset = dp.Table(data=small_df, caption="Test Basic Table")
    dt_asset = dp.DataTable(df=big_df, caption="Test DataTable")
    dt_pivot_asset = dp.DataTable(df=big_df, caption="Test DataTable with Pivot", can_pivot=True)

    if single_file:
        return dp.Report(dp.Group(blocks=[md_block, plot_asset]))
    else:
        return dp.Report(
            dp.Page(
                dp.Select(md_block, html_block, html_block_1, code_block, type=dp.SelectType.TABS),
                dp.Group(big_number, big_number_1, columns=2),
            ),
            dp.Page(
                plot_asset,
                list_asset,
                img_asset,
                table_asset,
                dt_asset,
                dt_pivot_asset,
            ),
        )


def test_gen_report_simple():
    report = gen_report_simple()
    assert_report(report, 0)
    # TODO - replace accessors here with glom / boltons / toolz
    assert len(report.pages[0].blocks[0].blocks) == 2
    assert isinstance(report.pages[0].blocks[0].blocks[1], dp.Text)
    assert report.pages[0].blocks[0].blocks[0].id == "test-id-1"


def test_gen_report_nested_mixed():
    report = dp.Report(
        dp.Group(
            md_block_id,
            str_md_block,
        ),
        "Simple string Markdown #2",
    )

    assert_report(report, 0)
    assert len(glom(report, "pages.0.blocks")) == 1
    assert isinstance(glom(report, "pages.0.blocks.0"), dp.Group)
    assert isinstance(report.pages[0].blocks[0].blocks[0], dp.Group)
    assert isinstance(report.pages[0].blocks[0].blocks[1], dp.Text)
    assert report.pages[0].blocks[0].blocks[0].blocks[0].id == "test-id-1"


def test_gen_report_primitives(datadir: Path):
    # check we don't allow arbitary python primitives - must be pickled directly via dp.File
    with pytest.raises(DPError):
        _ = dp.Report([1, 2, 3])

    report = dp.Report(
        "Simple string Markdown #2",  # Markdown
        gen_df(),  # Table
        alt.Chart(gen_df()).mark_line().encode(x="x", y="y"),  # Plot
        datadir / "datapane-logo.png",  # File
    )
    assert_report(report, 3)
    assert glom(report, ("pages.0.blocks.0.blocks", ["_tag"])) == ["Text", "Table", "Plot", "File"]


def test_gen_failing_reports():
    # nested pages
    with pytest.raises((DocumentInvalid, DPError)):
        r = dp.Report(dp.Page(dp.Page(md_block)))
        r._gen_report(embedded=False, title="TITLE", description="DESCRIPTION")
    with pytest.raises((DocumentInvalid, DPError)):
        r = dp.Report(dp.Group(dp.Page(md_block)))
        r._gen_report(embedded=False, title="TITLE", description="DESCRIPTION")

    # group with 0 object
    with pytest.raises((DocumentInvalid, DPError)):
        r = dp.Report(dp.Page(dp.Group(blocks=[])))
        r._gen_report(embedded=False, title="TITLE", description="DESCRIPTION")

    # select with 1 object
    with pytest.raises((DocumentInvalid, DPError)):
        r = dp.Report(dp.Page(dp.Select(blocks=[md_block])))
        r._gen_report(embedded=False, title="TITLE", description="DESCRIPTION")


def test_gen_report_nested_blocks():
    s = "# Test markdown block <hello/> \n Test **content**"
    report = dp.Report(
        blocks=[
            dp.Group(dp.Text(s, id="test-id-1"), "Simple string Markdown", label="test-group-label"),
            dp.Select(
                blocks=[
                    dp.Text(s, id="test-id-2", label="test-block-label"),
                    "Simple string Markdown",
                ],
                label="test-select-label",
            ),
        ]
    )

    # No additional wrapper block
    assert len(report.pages[0].blocks) == 2
    assert isinstance(report.pages[0].blocks[0], dp.Group)
    assert isinstance(report.pages[0].blocks[1], dp.Select)
    assert isinstance(report.pages[0].blocks[1].blocks[1], dp.Text)
    assert glom(report, ("pages.0.blocks", ["_attributes.label"])) == ["test-group-label", "test-select-label"]
    assert glom(report, "pages.0.blocks.0.blocks.0.id") == "test-id-1"
    assert glom(report, "pages.0.blocks.1.blocks.0._attributes.label") == "test-block-label"
    assert_report(report, 0)


def test_gen_report_complex_no_files():
    report = gen_report_complex_no_files()
    assert_report(report, 0)
    assert len(report.pages) == 3


def test_gen_report_with_files(datadir: Path):
    report = gen_report_complex_with_files(datadir)
    assert_report(report, 6, 17)


################################################################################
# Templates
def test_demo_report():
    report = dp.templates.build_demo_report()
    assert_report(report, 23, 61)


def test_add_code():
    b = dp.templates.add_code(md_block, "print(1)")
    assert isinstance(b, dp.Select)
    assert glom(b, ("blocks", ["_tag"])) == ["Text", "Code"]
    assert "print(1)" in element_to_str(b)


def test_build_md_report():
    text = """
# Hello

{{}}

{{table}}
"""

    report = dp.templates.build_md_report(text, gen_df(4), table=gen_df(8))
    assert_report(report, 2, 5)


################################################################################
# Local saving
@pytest.mark.skipif("CI" in os.environ, reason="Currently depends on building fe-components first")
def test_local_report_simple(datadir: Path, monkeypatch):
    monkeypatch.chdir(datadir)
    report = gen_report_simple()
    report.save(path="test_out.html")


@pytest.mark.skipif("CI" in os.environ, reason="Currently depends on building fe-components first")
def test_local_report_with_files(datadir: Path, monkeypatch):
    monkeypatch.chdir(datadir)
    report = gen_report_complex_with_files(datadir)
    report.save(path="test_out.html")
