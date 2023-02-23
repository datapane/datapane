"""
Basic View / XML level tests for the dp.Function block
"""
import datetime
import typing as t
from functools import partial

import pytest
from glom import glom

import datapane as dp
from datapane.common.viewxml_utils import ElementT
from tests.client.views import test_views as tv


def f(params):
    return dp.Blocks("Hello")


def mk_params_tml() -> t.Dict[str, t.Callable[..., dp.blocks.parameters.Parameter]]:
    p = partial
    return dict(
        switch=p(dp.Switch, label="switch-label"),
        textbox=p(dp.TextBox),
        numberbox=p(dp.NumberBox, initial=10),
        range=p(dp.Range, initial=4, min=1, max=5),
        choice=p(dp.Choice, options=["滚滚长江东逝水", "2"]),
        multichoice=p(dp.MultiChoice, options=["1", "2"]),
        tags=p(dp.Tags),
        date=p(dp.Date, initial=datetime.date.today()),
        datetime=p(dp.DateTime),
        time=p(dp.Time),
    )


def mk_params_as_dict():
    return {k: v() for k, v in mk_params_tml().items()}


def mk_params_as_list():
    return [v(name=k) for k, v in mk_params_tml().items()]


@pytest.fixture(
    params=[
        mk_params_as_list,  # Sequence[Parameter]
        mk_params_as_dict,  # Dict[str, Parameter]
        lambda: dp.Controls(*mk_params_as_list()),
        lambda: dp.Controls(**mk_params_as_dict()),
    ]
)
def mk_controls(request):
    return request.param


def test_dp_function():
    view = dp.Blocks(dp.Compute(f, target="x"))
    tv.assert_view(view, 0, 2)  # inc empty Controls element
    root = view.get_dom()
    _controls: t.List[ElementT] = root.xpath("//Controls/*")
    assert len(_controls) == 0
    assert glom(view, ("blocks", ["_tag"])) == ["Compute"]


def test_dp_function_controls(mk_controls):
    # all controls, test to xml, block length/name/ordering, etc.
    controls = mk_controls()
    view = dp.Blocks(dp.Compute(f, target="x", controls=controls))
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
