from functools import partial

import pytest

import datapane as dp

# Constructor tests


@pytest.mark.parametrize(
    "controls_factory",
    (dp.Controls.empty, dp.Controls),
)
def test_can_be_empty(controls_factory):
    controls = controls_factory()

    assert controls is not None
    assert len(controls.params) == 0
    assert controls.label is None


def test_can_be_labeled():
    label = "Test Label"

    controls = dp.Controls(label=label)

    assert controls.label == label


def test_takes_parameters_as_args(make_parameter):
    param_name = "TestParameter"
    param = make_parameter(name=param_name)

    controls = dp.Controls(param)

    assert len(controls.params) == 1
    assert param is controls.params[0]
    assert controls.params[0].name == param_name


def test_takes_parameters_as_kwargs(make_parameter):
    old_param_name = "TestParameter"
    param = make_parameter(name=old_param_name)

    controls = dp.Controls(foo=param)

    assert len(controls.params) == 1
    assert param is controls.params[0]

    # we rename the parameter itself
    assert controls.params[0].name == "foo"


def test_cannot_take_parameter_as_args_and_kwargs(make_parameter):
    param = make_parameter()
    arg_param = make_parameter(name="foo")

    with pytest.raises(ValueError, match="Cannot have Parameters passed as both args and kwargs"):
        dp.Controls(arg_param, foo=param)


@pytest.fixture()
def make_parameter():
    return partial(dp.blocks.compute.Parameter)
