import math
import typing

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.core import example
from hypothesis.internal.compat import get_type_hints
from hypothesis.strategies._internal.types import _global_type_lookup

import datapane as dp
from datapane.blocks.parameters import Parameter
from datapane.client.exceptions import DPClientError
from datapane.processors import AppTransformations, ConvertXML, PreProcessView
from datapane.processors.types import mk_null_pipe
from tests.common.utils import all_subclasses

# Simplest tests: specific issues with specific Parameter subclasses:


def test_range_required_arguments():
    # These are required at runtime, we should make the interface fail early rather than late.
    with pytest.raises(TypeError, match="3 required keyword-only arguments: 'initial', 'min', and 'max'"):
        dp.Range("value")

    # Step is optional
    range_control = dp.Range("value", min=1, initial=3, max=3)
    assert range_control.step is None


def test_range_argument_types():
    range_control = dp.Range("value", min=1, initial=3.5, max=10, step=0.5)
    assert type(range_control.min) is float
    assert type(range_control.max) is float
    assert type(range_control.initial) is float
    assert type(range_control.step) is float


def test_range_xml():
    range_control = dp.Range("value", min=1, initial=3.5, max=10, step=0.5)
    assert parameter_produces_valid_xml_in_view(range_control)


def parameter_produces_valid_xml_in_view(param: Parameter) -> bool:
    controls = dp.Controls(param)

    def f(params):
        return None

    view = dp.View(dp.Function(f, target="x", controls=controls), dp.Text("text", name="x"))

    # ConvertXML raises a validation error if the XML doesn't match the schema, which is what we want:
    state = mk_null_pipe(view).pipe(PreProcessView()).pipe(AppTransformations()).pipe(ConvertXML()).state
    assert param._tag in state.view_xml  # Sanity check
    return True


# The following test is one level up in terms of generic testing i.e. test a
# specific Parameter subclass against the property that it should accept any
# arguments advertised in its signature. The test was written with the help of
# the `hypothesis.extra.ghostwriter` module


@given(
    name=st.text(),
    label=st.one_of(st.none(), st.text()),
    initial=st.text(),
    options=st.lists(st.text()),
)
@example(name="x", label="x", initial="", options=[])
def test_fuzz_Choice(name: str, label: typing.Optional[str], initial: str, options: typing.List[str]) -> None:
    _test_param_class_with_args(dp.Choice, (), dict(name=name, label=label, initial=initial, options=options))


def _test_param_class_with_args(param_class: type, args: tuple, kwargs: dict):
    # We should either raise some clear validation error immediately...
    obj = None
    try:
        obj = param_class(*args, **kwargs)
    except DPClientError:
        # our custom validation messages
        return
    except ValueError as e:
        if "All strings must be XML compatible: Unicode or ASCII, no NULL bytes or control characters" in e.args[0]:
            # This is a good clear error produced by lxml for bad inputs, that's fine
            return
        raise
    # ... or, we should accept it and NOT generate a validation error when served later on.
    assert parameter_produces_valid_xml_in_view(obj)


# The above has the disadvantage that we have to write a test for every Parameter
# subclass, and we have to keep the test in sync with the signature. So we then
# go one step up again, testing all the Parameter subclass constructors against
# their introspected signatures:

PARAMETER_CLASSES = [
    dp.Switch,
    dp.TextBox,
    dp.NumberBox,
    dp.Range,
    dp.Choice,
    dp.MultiChoice,
    dp.Tags,
    dp.Date,
    dp.Time,
    dp.DateTime,
    dp.File,
]


def test_PARAMETER_CLASSES_complete():
    parameter_subclasses = all_subclasses(Parameter)
    for cls in parameter_subclasses:
        if hasattr(dp, cls.__name__):  # exported publicly
            assert cls in PARAMETER_CLASSES, f"{cls} should be in PARAMETER_CLASSES to ensure fuzz tests run against it"


@st.composite
def parameter_class_with_valid_args(draw, classes=st.sampled_from(PARAMETER_CLASSES)):
    # This strategy is very similar to hypothesis.strategies.builds. But unlike
    # `builds`, we don't want the strategy to call the callable, we want our
    # tests to do that part.

    cls = draw(classes)
    infer_for = get_type_hints(cls.__init__)

    # Currently support just kwargs, if Parameter constructors gain positional only
    # this will need changing:
    arg_strategies = ()

    kwarg_strategies = {}
    for kw, t in infer_for.items():
        if getattr(t, "__module__", None) in ("builtins", "typing") or t in _global_type_lookup:
            kwarg_strategies[kw] = st.from_type(t)
        else:
            kwarg_strategies[kw] = st.deferred(lambda t=t: st.from_type(t))

    args = tuple(draw(s) for s in arg_strategies)
    kwargs = {kw: draw(s) for kw, s in kwarg_strategies.items()}
    return cls, args, kwargs


@given(parameter_class_with_valid_args())
@settings(max_examples=1000)
@example((dp.Switch, (), {"name": "\x1f"}))
@example((dp.Range, (), {"name": "x", "initial": 0, "min": 0, "max": -math.nan}))
def test_fuzz_all_parameters(parameter_class_and_args):
    return _test_param_class_with_args(*parameter_class_and_args)
