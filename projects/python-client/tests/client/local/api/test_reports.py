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
from datapane.client.api.report.blocks import BaseElement, BuilderState
from datapane.client.utils import DPError
from datapane.common.report import load_doc, validate_report_doc

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
    x = "count(/Report/Pages//*)"
    return int(load_doc(report_str).xpath(x))


def assert_report(
    report: dp.App, expected_attachments: int = None, expected_num_blocks: int = None
) -> t.Tuple[str, t.List[Path]]:
    report_str, attachments = dp.Processor(report)._gen_report(
        embedded=False, served=False, title="TITLE", description="DESCRIPTION"
    )
    # print(report_str)
    if expected_attachments:
        assert len(attachments) == expected_attachments
    if expected_num_blocks:
        assert num_blocks(report_str) == expected_num_blocks
    assert validate_report_doc(xml_str=report_str)
    return (report_str, attachments)


################################################################################
# Generators
def gen_report_simple() -> dp.App:
    return dp.App(
        blocks=[
            md_block_id,
            str_md_block,
        ]
    )


def gen_legacy_report_simple() -> dp.Report:
    return dp.Report(
        blocks=[
            md_block_id,
            str_md_block,
        ]
    )


def gen_report_complex_no_files() -> dp.App:
    """Generate a complex layout report with simple elements"""
    select = dp.Select(blocks=[md_block, md_block], type=dp.SelectType.TABS)
    group = dp.Group(md_block, md_block, columns=2)
    toggle = dp.Toggle(md_block, md_block)

    return dp.App(
        dp.Page(
            blocks=[
                dp.Group(md_block, md_block, columns=2),
                dp.Select(blocks=[md_block, group, toggle], type=dp.SelectType.DROPDOWN),
            ],
            title="Page Uno",
        ),
        dp.Page(
            blocks=[
                dp.Group(select, select, toggle, columns=2),
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


def gen_report_complex_with_files(datadir: Path, single_file: bool = False, local_report: bool = False) -> dp.App:
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
    divider_block = dp.Divider()
    empty_block = dp.Empty(name="empty-block")

    # assets
    plot_asset = dp.Plot(data=gen_plot(), caption="Plot Asset")
    list_asset = dp.Attachment(data=lis, filename="List Asset")
    img_asset = dp.Media(file=datadir / "datapane-logo.png")

    # tables
    table_asset = dp.Table(data=small_df, caption="Test Basic Table")
    # local reports don't support DataTable
    dt_asset = (
        table_asset if local_report else dp.DataTable(df=big_df, name="big-table-block", caption="Test DataTable")
    )

    if single_file:
        return dp.App(dp.Group(blocks=[md_block, dt_asset]))
    else:
        return dp.App(
            dp.Page(
                dp.Select(
                    md_block, html_block, html_block_1, code_block, formula_block, embed_block, type=dp.SelectType.TABS
                ),
                dp.Group(big_number, big_number_1, columns=2),
                dp.Toggle(md_block, html_block, label="Test Toggle"),
            ),
            dp.Page(
                plot_asset,
                divider_block,
                empty_block,
                list_asset,
                img_asset,
                table_asset,
                dt_asset,
            ),
        )


################################################################################
# PyReport Tests
def test_gen_report_single():
    # report with single block
    report = dp.App("test block")
    assert_report(report, 0)
    assert len(report.pages[0].blocks) == 1
    assert isinstance(report.pages[0].blocks[0], dp.Text)


def test_gen_report_simple():
    report = gen_report_simple()
    assert_report(report, 0)
    # TODO - replace accessors here with glom / boltons / toolz
    assert len(report.pages[0].blocks) == 2
    assert isinstance(report.pages[0].blocks[1], dp.Text)
    assert report.pages[0].blocks[0].name == "test-id-1"


def test_gen_report_nested_mixed():
    report = dp.App(
        dp.Group(
            md_block_id,
            str_md_block,
        ),
        "Simple string Markdown #2",
    )

    assert_report(report, 0)
    assert len(glom(report, "pages.0.blocks")) == 2
    assert isinstance(glom(report, "pages.0.blocks.0"), dp.Group)
    assert isinstance(report.pages[0].blocks[0], dp.Group)
    assert isinstance(report.pages[0].blocks[1], dp.Text)
    assert glom(report, "pages.0.blocks.0.blocks.0.name") == "test-id-1"


def test_gen_report_primitives(datadir: Path):
    # check we don't allow arbitary python primitives - must be pickled directly via dp.Attachment
    with pytest.raises(DPError):
        _ = dp.App([1, 2, 3])

    report = dp.App(
        "Simple string Markdown #2",  # Markdown
        gen_df(),  # Table
        gen_plot(),  # Plot
        datadir / "datapane-logo.png",  # Attachment
    )
    assert_report(report, 3)
    assert glom(report, ("pages.0.blocks", ["_tag"])) == ["Text", "Table", "Plot", "Attachment"]


def test_gen_failing_reports():
    # nested pages
    with pytest.raises(DPError):
        r = dp.App(dp.Page(dp.Page(md_block)))
        dp.Processor(r)._gen_report(embedded=False, served=False, title="TITLE", description="DESCRIPTION")
    with pytest.raises(DPError):
        r = dp.App(dp.Group(dp.Page(md_block)))
        dp.Processor(r)._gen_report(embedded=False, served=False, title="TITLE", description="DESCRIPTION")

    # page/pages with 0 objects
    with pytest.raises(DPError):
        r = dp.App(dp.Page(blocks=[]))
        dp.Processor(r)._gen_report(embedded=False, served=False, title="TITLE", description="DESCRIPTION")

    # select with 1 object
    with pytest.raises(DPError):
        r = dp.App(dp.Page(dp.Select(blocks=[md_block])))
        dp.Processor(r)._gen_report(embedded=False, served=False, title="TITLE", description="DESCRIPTION")

    # empty text block
    with pytest.raises(AssertionError):
        r = dp.App(dp.Text(" "))
        dp.Processor(r)._gen_report(embedded=False, served=False, title="TITLE", description="DESCRIPTION")

    # empty df
    with pytest.raises(DPError):
        r = dp.App(dp.DataTable(pd.DataFrame()))
        dp.Processor(r)._gen_report(embedded=False, served=False, title="TITLE", description="DESCRIPTION")

    # invalid names
    with pytest.raises(DocumentInvalid):
        r = dp.App(dp.Text("a", name="my-name"), dp.Text("a", name="my-name"))
        dp.Processor(r)._gen_report(embedded=False, served=False, title="TITLE", description="DESCRIPTION")

    with pytest.raises(DPError):
        dp.App(dp.Text("a", name="3-invalid-name"))


def test_gen_report_nested_blocks():
    s = "# Test markdown block <hello/> \n Test **content**"
    report = dp.App(
        blocks=[
            dp.Group(dp.Text(s, name="test-id-1"), "Simple string Markdown", label="test-group-label"),
            dp.Select(
                blocks=[
                    dp.Text(s, name="test-id-2", label="test-block-label"),
                    "Simple string Markdown",
                ],
                label="test-select-label",
            ),
            dp.Toggle(
                blocks=[
                    dp.Text(s, name="test-id-3"),
                    "Simple string Markdown",
                ],
                label="test-toggle-label",
            ),
        ]
    )

    # No additional wrapper block
    assert len(report.pages[0].blocks) == 3
    assert isinstance(report.pages[0].blocks[0], dp.Group)
    assert isinstance(report.pages[0].blocks[1], dp.Select)
    assert isinstance(report.pages[0].blocks[2], dp.Toggle)
    assert isinstance(report.pages[0].blocks[1].blocks[1], dp.Text)
    assert glom(report, ("pages.0.blocks", ["_attributes.label"])) == [
        "test-group-label",
        "test-select-label",
        "test-toggle-label",
    ]
    assert glom(report, "pages.0.blocks.0.blocks.0.name") == "test-id-1"
    assert glom(report, "pages.0.blocks.1.blocks.0._attributes.label") == "test-block-label"
    assert_report(report, 0)


def test_gen_report_complex_no_files():
    report = gen_report_complex_no_files()
    assert_report(report, 0)
    assert len(report.pages) == 3


def test_gen_report_with_files(datadir: Path):
    report = gen_report_complex_with_files(datadir)
    assert_report(report, 5, 23)


################################################################################
# Local saving
@pytest.mark.skipif("CI" in os.environ, reason="Currently depends on building fe-components first")
def test_local_report_simple(datadir: Path, monkeypatch):  # noqa: ANN
    monkeypatch.chdir(datadir)
    report = gen_report_simple()
    report.save(path="test_out.html", name="My Wicked Report", author="Datapane Team")


@pytest.mark.skipif("CI" in os.environ, reason="Currently depends on building fe-components first")
def test_local_report_with_files(datadir: Path, monkeypatch):  # noqa: ANN
    monkeypatch.chdir(datadir)
    report = gen_report_complex_with_files(datadir, local_report=True)
    report.save(path="test_out.html", name="Even better report")
