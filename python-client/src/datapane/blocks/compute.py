from __future__ import annotations

import secrets
import typing as t

from pydantic import BaseConfig, BaseModel, create_model, validator
from typing_extensions import Self

from datapane.client import DPClientError
from datapane.common.dp_types import StrEnum
from datapane.common.viewxml_utils import mk_attribs

from .base import BaseBlock, BlockId
from .parameters import E, Parameter

if t.TYPE_CHECKING:
    from datapane.common.viewxml_utils import ElementT
    from datapane.view import Blocks


def gen_name() -> str:
    """Return a (safe) name for use in a Block"""
    return f"id-{secrets.token_urlsafe(8)}"


class Empty(BaseBlock):
    """
    An empty block that can be updated / replaced later

    Args:
        name: A unique name for the block to reference when updating the report
    """

    _tag = "Empty"

    def __init__(self, name: BlockId):
        super().__init__(name=name)


class DummyModelConfig(BaseConfig):
    """Pydantic Model Config class for generated Controls models"""

    title = "Dynamic Parameters Model"
    anystr_strip_whitespace = True
    # use_enum_values = False
    # extra = 'ignore'
    allow_mutation = False
    frozen = True


class Controls:
    label: t.Optional[str]
    params: t.List[Parameter]

    def __init__(self, *params: Parameter, label: t.Optional[str] = None, **kwarg_params: Parameter):
        self.label = label
        self.params = self._make_params(*params, **kwarg_params)
        self._check()

    @classmethod
    def empty(cls) -> Controls:
        return cls()

    def __add__(self, other: Controls) -> Self:
        self.params.extend(other.params)
        self._check()
        return self

    def _make_params(self, *args: Parameter, **kwargs: Parameter) -> t.List[Parameter]:
        if args and kwargs:
            raise ValueError("Cannot have Parameters passed as both args and kwargs")
        if args:
            if any(not p.name for p in args):
                raise ValueError("Unnamed parameters cannot be passed as args")
            return list(args)
        params = []
        for name, param in kwargs.items():
            param.name = param.attribs["name"] = name
            params.append(param)
        return params

    def _check(self) -> None:
        # ensure all names are unique
        if len(self.params) != len({p.name for p in self.params}):
            raise ValueError("Several parameters have the same name")

    def _to_pydantic(self) -> t.Type[BaseModel]:
        """Return a dynamically generated Pydantic model for the controls"""
        fields = {p.name: p._as_field() for p in self.params}
        validators = {f"{p.name}_validator": validator(p.name, allow_reuse=True)(p._validator()) for p in self.params}
        DummyModel = create_model("DummyModel", **fields, __config__=DummyModelConfig, __validators__=validators)
        return DummyModel

    def _to_xml(self) -> ElementT:
        attribs = mk_attribs(label=self.label)
        return E.Controls(*[p._to_xml() for p in self.params], **attribs)

    @property
    def is_cacheable(self) -> bool:
        """Can the controls be cached"""
        return all(p.cacheable for p in self.params)

    @property
    def param_names(self) -> t.Set[str]:
        return {p.name for p in self.params}


class Swap(StrEnum):
    REPLACE = "replace"
    INNER = "inner"
    PREPEND = "prepend"
    APPEND = "append"


class Trigger(StrEnum):
    SUBMIT = "submit"
    SCHEDULE = "schedule"  # every 30s
    VISIBLE = "visible"
    LOAD = "load"
    MOUNT = "mount"


class TargetMode(StrEnum):
    SELF = "self"
    BELOW = "below"
    SIDE = "side"
    # TODO - 'parent' - find the nearest group ancestor and replace there
    # PARENT = "parent"


TargetT = t.Union[BlockId, TargetMode, BaseBlock]
ControlsT = t.Union[Controls, t.Iterable[Parameter], t.Mapping[str, Parameter], None]
FunctionT = t.Callable[..., "Blocks"]


class Compute(BaseBlock):
    """Compute blocks allow for dynamic views based on running python functions that return blocks"""

    _tag = "Compute"

    def __init__(
        self,
        function: FunctionT,
        target: TargetT,
        controls: ControlsT = None,
        name: BlockId = None,
        label: t.Optional[str] = None,
        swap: Swap = Swap.REPLACE,
        trigger: Trigger = Trigger.SUBMIT,
        immediate: bool = False,
        # function params - wrap around @dp.function
        cache: bool = False,
        submit_label: str = "Go",
        timer: int = 30,
    ):
        """
        Create a compute block that runs the provided function.

        Args:
            function: Function to run
            target: Where the results from the function should be viewed
            controls: Parameters for the Form
            swap: The mechanism to replace the referenced block
            trigger: How the function is called
            cache: Hint that the function output may be cached


        Returns: A Compute block representing the Dynamic behaviour
        """
        if controls is None:
            self.controls = Controls.empty()
        elif isinstance(controls, Controls):
            self.controls = controls
        elif isinstance(controls, t.Mapping):
            self.controls = Controls(**controls)
        else:  # iterable
            self.controls = Controls(*controls)

        self.function = function
        self.cache = cache
        if isinstance(target, BaseBlock):
            if target.name is None:
                raise DPClientError(f"Block {target} must have a name to be used as a target")
            self.target = target.name
        else:
            self.target = str(target)

        # NOTE - using id for the function_id means we can't persist sessions across instances
        # prob ok for now
        self.function_id = f"app.{id(self)}"

        if target in (TargetMode.BELOW, TargetMode.SIDE):
            swap = Swap.INNER
        elif target == TargetMode.SELF:
            swap = Swap.REPLACE
        self.swap = swap

        opt_attribs = {}
        # submit validation
        if trigger == Trigger.SUBMIT:
            opt_attribs.update(submit_label=submit_label)
        elif trigger == Trigger.SCHEDULE:
            opt_attribs.update(timer=timer, immediate=immediate)
        elif trigger in (Trigger.LOAD, Trigger.VISIBLE):
            trigger = Trigger.MOUNT

        # basic attributes
        super().__init__(
            function_id=self.function_id,
            label=label,
            trigger=trigger,
            swap=swap,
            name=name,
            target=target,
            **opt_attribs,
        )


# Compute Helpers
def Form(
    on_submit: FunctionT,
    controls: ControlsT = None,
    target: TargetT = TargetMode.BELOW,
    label: t.Optional[str] = None,
    submit_label: str = "Go",
    cache: bool = False,
) -> Compute:
    """
    Create a form on the page that runs the provided function on submit.

    Args:
        on_submit: Function to run when the form is submitted
        controls: Parameters for the Form
        target (optional): Where the results from the function should be viewed
        label (optional): Description for the Form
        submit_label: Label for the submit button
        cache: Hint that the on_submit function may be cached

    Returns: A Compute block representing the Form
    """
    return Compute(
        function=on_submit, controls=controls, target=target, label=label, submit_label=submit_label, cache=cache
    )


def Dynamic(
    on_load: t.Optional[FunctionT] = None,
    on_timer: t.Optional[FunctionT] = None,
    target: t.Optional[TargetT] = None,
    seconds: int = 30,
    immediate: bool = False,
) -> Compute:
    """
    Create a dynamically updating block that runs the provided function to update the View.

    Args:
        on_load: Function to run when the App is loaded
        on_timer: Function to run on a regular timer
        target (optional): Where the results from the function should be viewed
        seconds (optional, default=30): Number of seconds between running the function specified by on_timer
        immediate (optional, default=False): Run the specified function immediately on page load

    Returns: A Compute block representing the Dynamic behaviour
    """

    if on_load and on_timer:
        raise DPClientError("Can't use both on_load and on_timer simultaneously")
    elif on_load:
        f = on_load
        target = target or TargetMode.SELF
        trigger = Trigger.LOAD
    elif on_timer:
        f = on_timer
        target = target or TargetMode.BELOW
        trigger = Trigger.SCHEDULE
    else:
        raise DPClientError("Must provide one of on_load or on_timer")

    return Compute(function=f, target=target, timer=seconds, trigger=trigger, immediate=immediate)
