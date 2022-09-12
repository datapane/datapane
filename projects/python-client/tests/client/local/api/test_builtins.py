"""Tests for the API that can run locally (due to design or mocked out)"""
from glom import T, glom

import datapane as dp

from ....client.e2e.common import gen_df
from .test_reports import assert_report, element_to_str, md_block


################################################################################
# Templates
def test_demo_report():
    report = dp.builtins.build_demo_report()
    assert_report(report, 22, 66)


def test_add_code():
    b = dp.builtins.add_code(md_block, "print(1)")
    assert isinstance(b, dp.Select)
    assert glom(b, ("blocks", ["_tag"])) == ["Text", "Code"]
    assert "print(1)" in element_to_str(b)


def test_build_md_report():
    text = """
# Hello

{{}}

{{table}}
"""

    report = dp.builtins.build_md_report(text, gen_df(4), table=gen_df(8))
    assert_report(report, 2, 5)


def test_add_header():
    text = "HEADER"

    r = dp.App(blocks=[dp.Page(md_block, md_block) for _ in range(3)])

    r1 = dp.builtins.add_header(r, header=text, all_pages=True)
    assert_report(r1, 0, 15)
    assert glom(r1, ("pages", ["blocks.0.blocks.0.content"])) == [text, text, text]

    r1 = dp.builtins.add_header(r, header=text, all_pages=False)
    assert_report(r1, 0, 11)
    assert glom(r1, ("pages", T[:1], ["blocks.0.blocks.0.content"])) == [text]
    assert glom(r1, ("pages", T[1:], ["blocks.0.content"])) == [md_block.content, md_block.content]


def test_add_footer():
    text = "FOOTER"

    r = dp.App(blocks=[dp.Page(md_block, md_block) for _ in range(3)])

    r1 = dp.builtins.add_footer(r, footer=text, all_pages=True)
    assert_report(r1, 0, 15)
    assert glom(r1, ("pages", ["blocks.0.blocks.-1.content"])) == [text, text, text]

    r1 = dp.builtins.add_footer(r, footer=text, all_pages=False)
    assert_report(r1, 0, 11)
    assert glom(r1, ("pages", T[:1], ["blocks.0.blocks.-1.content"])) == [text]
    assert glom(r1, ("pages", T[1:], ["blocks.0.content"])) == [md_block.content, md_block.content]
