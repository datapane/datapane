"""
Basic View / XML level tests for the dp.Function block
"""
import datetime
import typing as t

from glom import glom

import datapane as dp
from datapane.common.viewxml_utils import ElementT
from tests.client.views import test_views as tv


def f(params):
    return dp.Blocks("Hello")


def mk_controls() -> dp.Controls:
    return dp.Controls(
        dp.Switch("switch", "switch-label"),
        dp.TextBox("textbox"),
        dp.NumberBox("numberbox", initial=10),
        dp.Range("range", initial=4, min=1, max=5),
        dp.Choice("choice", options=["滚滚长江东逝水", "2"]),
        dp.MultiChoice("multichoice", options=["1", "2"]),
        dp.Tags(name="tags"),
        dp.Date("date", initial=datetime.date.today()),
        dp.DateTime("datetime"),
        dp.Time("time"),
    )


def test_dp_function():
    view = dp.Blocks(dp.Compute(f, target="x"))
    tv.assert_view(view, 0, 2)  # inc empty Controls element
    root = view.get_dom()
    _controls: t.List[ElementT] = root.xpath("//Controls/*")
    assert len(_controls) == 0
    assert glom(view, ("blocks", ["_tag"])) == ["Compute"]


def test_dp_function_controls():
    # all controls, test to xml, block length/name/ordering, etc.

    view = dp.Blocks(dp.Compute(f, target="x", controls=mk_controls()))
    tv.assert_view(view, 0, 12)
    root = view.get_dom()
    assert glom(view, ("blocks", ["_tag"])) == ["Compute"]

    # test the controls
    control_names = [
        "switch",
        "textbox",
        "numberbox",
        "range",
        "choice",
        "multichoice",
        "tags",
        "date",
        "datetime",
        "time",
    ]

    assert glom(view, ("blocks.0.controls.params", ["name"])) == control_names

    _controls: t.List[ElementT] = root.xpath("//Controls/*")
    assert control_names == root.xpath("//Controls/*/@name")
    assert glom(view, ("blocks.0.controls.params", ["_tag"])) == [x.tag for x in _controls]


def test_dp_function_controls_app_trans():
    # test the resulting FunctionEntry
    pass
