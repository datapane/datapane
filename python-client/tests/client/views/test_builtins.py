"""Tests for the API that can run locally (due to design or mocked out)"""
from glom import glom

import datapane as dp
from datapane.builtins import gen_df

from .test_views import assert_view, element_to_str, md_block


################################################################################
# Templates
def test_demo():
    view = dp.builtins.demo()

    assert_view(view)


def test_add_code():
    b = dp.builtins.add_code(md_block, "print(1)")
    assert isinstance(b, dp.Select)
    assert glom(b, ("blocks", ["_tag"])) == ["Text", "Code"]
    assert "print(1)" in element_to_str(b)


def test_build_md_view():
    text = """
# Hello

{{}}

{{table}}
"""

    view = dp.builtins.build_md_view(text, gen_df(4), table=gen_df(8))
    assert_view(view, 2, 4)
