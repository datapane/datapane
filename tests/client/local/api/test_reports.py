"""Tests for the API that can run locally (due to design or mocked out)"""
import os
import typing as t
from pathlib import Path

import pandas as pd
import pytest
from dominate.tags import h2
from glom import glom
from lxml import etree
from lxml.etree import DocumentInvalid

import datapane as dp
from datapane.client import DPError
from datapane.client.api.report.blocks import BaseElement
from datapane.client.api.report.core import BuilderState
from datapane.common.report import validate_report_doc

from ...e2e.common import gen_df, gen_plot

################################################################################
# Helpers
md_block_id = dp.Text(text="# Test markdown block <hello/> \n Test **content**", name="test-id-1")
md_block = dp.Text(text="# Test markdown block <hello/> \n Test **content**")
str_md_block = "Simple string Markdown"


def element_to_str(e: BaseElement) -> str:
    s = e._to_xml(BuilderState())
    return etree.tounicode(s.elements[0], pretty_print=True)


def num_blocks(report_str: str) -> int:
    x = "count(/Report/Main//*)"
    return int(etree.fromstring(report_str).xpath(x))


def assert_report(report: dp.Report, expected_attachments: int = None, expected_num_blocks: int = None):
    report_str, attachments = report._gen_report(embedded=False, title="TITLE", description="DESCRIPTION")
    # print(report_str)
    if expected_attachments:
        assert len(attachments) == expected_attachments
    if expected_num_blocks:
        assert num_blocks(report_str) == expected_num_blocks
    assert validate_report_doc(xml_str=report_str)
    return (report_str, attachments)


################################################################################
# Generators
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
            title="Page Uno",
        ),
        dp.Page(
            blocks=[
                dp.Group(select, select, columns=2),
                dp.Select(blocks=[md_block, md_block, md_block], type=dp.SelectType.TABS),
            ],
            title="Page Duo",
        ),
        dp.Page(
            blocks=[
                dp.Group(group, group, columns=2),
                dp.Select(blocks=[select, select], type=dp.SelectType.TABS),
            ],
            title="Page Tres",
        ),
    )


def gen_report_complex_with_files(datadir: Path, single_file: bool = False, local_report: bool = False) -> dp.Report:
    # Asset tests
    lis = [1, 2, 3]
    small_df = gen_df()
    big_df = gen_df(10000)

    # text
    # md_block
    html_block = dp.HTML(html="<h1>Hello World</h1>")
    html_block_1 = dp.HTML(html=h2("Hello World"))
    code_block = dp.Code(code="print('hello')", language="python")
    formula_block = dp.Formula(formula=r"\frac{1}{\sqrt{x^2 + 1}}")
    big_number = dp.BigNumber(heading="Tests written", value=1234)
    big_number_1 = dp.BigNumber(heading="Real Tests written :)", value=11, change=2, is_upward_change=True)
    embed_block = dp.Embed(url="https://www.youtube.com/watch?v=JDe14ulcfLA")

    # assets
    plot_asset = dp.Plot(data=gen_plot(), caption="Plot Asset")
    list_asset = dp.File(data=lis, filename="List Asset", is_json=True)
    img_asset = dp.File(file=datadir / "datapane-logo.png")

    # tables
    table_asset = dp.Table(data=small_df, caption="Test Basic Table")
    # local reports don't support DataTable
    dt_asset = table_asset if local_report else dp.DataTable(df=big_df, caption="Test DataTable")

    if single_file:
        return dp.Report(dp.Group(blocks=[md_block, dt_asset]))
    else:
        return dp.Report(
            dp.Page(
                dp.Select(
                    md_block, html_block, html_block_1, code_block, formula_block, embed_block, type=dp.SelectType.TABS
                ),
                dp.Group(big_number, big_number_1, columns=2),
            ),
            dp.Page(
                plot_asset,
                list_asset,
                img_asset,
                table_asset,
                dt_asset,
            ),
        )


################################################################################
# PyReport Tests
def test_gen_report_simple():
    report = gen_report_simple()
    assert_report(report, 0)
    # TODO - replace accessors here with glom / boltons / toolz
    assert len(report.pages[0].blocks[0].blocks) == 2
    assert isinstance(report.pages[0].blocks[0].blocks[1], dp.Text)
    assert report.pages[0].blocks[0].blocks[0].name == "test-id-1"


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
    assert report.pages[0].blocks[0].blocks[0].blocks[0].name == "test-id-1"


def test_gen_report_primitives(datadir: Path):
    # check we don't allow arbitary python primitives - must be pickled directly via dp.File
    with pytest.raises(DPError):
        _ = dp.Report([1, 2, 3])

    report = dp.Report(
        "Simple string Markdown #2",  # Markdown
        gen_df(),  # Table
        gen_plot(),  # Plot
        datadir / "datapane-logo.png",  # File
    )
    assert_report(report, 3)
    assert glom(report, ("pages.0.blocks.0.blocks", ["_tag"])) == ["Text", "Table", "Plot", "File"]


def test_gen_failing_reports():
    # nested pages
    with pytest.raises(DPError):
        r = dp.Report(dp.Page(dp.Page(md_block)))
        r._gen_report(embedded=False, title="TITLE", description="DESCRIPTION")
    with pytest.raises(DPError):
        r = dp.Report(dp.Group(dp.Page(md_block)))
        r._gen_report(embedded=False, title="TITLE", description="DESCRIPTION")

    # group with 0 object
    with pytest.raises(DPError):
        r = dp.Report(dp.Page(dp.Group(blocks=[])))
        r._gen_report(embedded=False, title="TITLE", description="DESCRIPTION")

    # select with 1 object
    with pytest.raises(DPError):
        r = dp.Report(dp.Page(dp.Select(blocks=[md_block])))
        r._gen_report(embedded=False, title="TITLE", description="DESCRIPTION")

    # empty text block
    with pytest.raises(AssertionError):
        r = dp.Report(dp.Text(" "))
        r._gen_report(embedded=False, title="TITLE", description="DESCRIPTION")

    # empty df
    with pytest.raises(DPError):
        r = dp.Report(dp.DataTable(pd.DataFrame()))
        r._gen_report(embedded=False, title="TITLE", description="DESCRIPTION")

    # invalid names
    with pytest.raises(DocumentInvalid):
        r = dp.Report(dp.Text("a", name="my-name"), dp.Text("a", name="my-name"))
        r._gen_report(embedded=False, title="TITLE", description="DESCRIPTION")

    with pytest.raises(DPError):
        dp.Report(dp.Text("a", name="3-invalid-name"))


def test_gen_report_nested_blocks():
    s = "# Test markdown block <hello/> \n Test **content**"
    report = dp.Report(
        blocks=[
            dp.Group(dp.Text(s, name="test-id-1"), "Simple string Markdown", label="test-group-label"),
            dp.Select(
                blocks=[
                    dp.Text(s, name="test-id-2", label="test-block-label"),
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
    assert glom(report, "pages.0.blocks.0.blocks.0.name") == "test-id-1"
    assert glom(report, "pages.0.blocks.1.blocks.0._attributes.label") == "test-block-label"
    assert_report(report, 0)


def test_gen_report_complex_no_files():
    report = gen_report_complex_no_files()
    assert_report(report, 0)
    assert len(report.pages) == 3


def test_gen_report_with_files(datadir: Path):
    report = gen_report_complex_with_files(datadir)
    assert_report(report, 5, 18)


################################################################################
# Local saving
@pytest.mark.skipif("CI" in os.environ, reason="Currently depends on building fe-components first")
def test_local_report_simple(datadir: Path, monkeypatch):
    monkeypatch.chdir(datadir)
    report = gen_report_simple()
    report.save(path="test_out.html", name="My Wicked Report", author="Datapane Team")


@pytest.mark.skipif("CI" in os.environ, reason="Currently depends on building fe-components first")
def test_local_report_with_files(datadir: Path, monkeypatch):
    monkeypatch.chdir(datadir)
    report = gen_report_complex_with_files(datadir, local_report=True)
    report.save(path="test_out.html", name="Even better report")


################################################################################
# TextReport
def assert_text_report(tr: dp.TextReport, expected_num_assets: int, names: t.Optional[t.List[str]] = None):
    report_str, _ = tr._gen_report(embedded=False, title="TITLE", description="DESCRIPTION")
    r = etree.fromstring(report_str)
    assert r.xpath("count(//Group[1]/*)") == expected_num_assets
    if names:
        assert r.xpath("//Group[1]/*/@name") == names


def __test_gen_report_id_check():
    """Test case unused atm"""
    # all fresh
    report = dp.Report(md_block, md_block, md_block)
    assert_report(report)  # expected_id_count=5)
    # 2 fresh
    report = dp.Report(md_block, md_block_id, md_block)
    assert_report(report)  # expected_id_count=4)
    # 0 fresh
    report = dp.Report(md_block_id, dp.Text("test", name="test-2"))
    assert_report(report)  # expected_id_count=2)


def test_textreport_gen():
    """Test TextReport API and id/naming handling"""
    s_df = gen_df()

    # Simple
    report = dp.TextReport("Text-3")
    assert_text_report(report, 1)

    # multiple blocks
    report = dp.TextReport("Text-1", "Text-2", s_df)
    assert_text_report(report, 3)

    # empty - raise error
    with pytest.raises(DPError):
        report = dp.TextReport()
        assert_text_report(report, 0)

    # mixed naming usage
    report = dp.TextReport("text-1", dp.Text("Text-4", name="test"))
    assert_text_report(report, 2)

    # arg/kwarg naming tests
    report = dp.TextReport(
        dp.Text("Text-arg-1"),
        dp.Text("Text-arg-2", name="text-arg-2"),
        t1="Text-1",
        t2=dp.Text("Text-2"),
        t3=dp.Text("Text-3", name="overwritten"),
    )
    assert_text_report(report, 5, ["text-1", "text-arg-2", "t1", "t2", "t3"])

    # dict/list test
    report = dp.TextReport(blocks=dict(t1="text-1", t2=dp.Text("Text-2"), t3=dp.Text("Text-3", name="overwritten")))
    assert_text_report(report, 3, ["t1", "t2", "t3"])
    report = dp.TextReport(blocks=["Text-1", dp.Text("Text-2"), dp.Text("Text-3", name="text-3")])
    assert_text_report(report, 3, ["text-1", "text-2", "text-3"])
