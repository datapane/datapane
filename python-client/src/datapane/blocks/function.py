from __future__ import annotations

import secrets
import typing as t

from pydantic import BaseConfig, BaseModel, create_model, validator
from typing_extensions import Self

from datapane.common.dp_types import StrEnum
from datapane.common.viewxml_utils import mk_attribs

from .base import BaseElement, BlockId
from .parameters import E, Parameter

if t.TYPE_CHECKING:
    from lxml.etree import _Element as Element

    from datapane.view import View


def gen_name() -> str:
    """Return a (safe) name for use in a Block"""
    return f"id-{secrets.token_urlsafe(8)}"


class Empty(BaseElement):
    """
    An empty block that can be patched later

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
    def __init__(self, *params: Parameter, label: t.Optional[str] = None):
        self.label = label
        self.params = list(params)
        self._check()

    @classmethod
    def empty(cls) -> Controls:
        return cls()

    def __add__(self, other: Controls) -> Self:
        self.params.extend(other.params)
        self._check()
        return self

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

    def _to_xml(self) -> Element:
        attribs = mk_attribs(label=self.label)
        return E.Controls(*[p._to_xml() for p in self.params], **attribs)

    @property
    def is_cacheable(self) -> bool:
        """Can the controls be cached"""
        return all(p.cacheable for p in self.params)


class Swap(StrEnum):
    REPLACE = "replace"
    INNER = "inner"
    PREPEND = "prepend"
    APPEND = "append"


class Trigger(StrEnum):
    SUBMIT = "submit"
    SCHEDULE = "schedule"  # every 30s


class TargetMode(StrEnum):
    SELF = "self"
    BELOW = "below"
    SIDE = "side"


class Function(BaseElement):
    """Function blocks allow for dynamic views based on running functions"""

    _tag = "Function"

    def __init__(
        self,
        function: t.Callable[..., View],
        target: t.Union[BlockId, TargetMode],
        controls: t.Union[Controls, t.Iterable[Parameter], None] = None,
        name: BlockId = None,
        label: t.Optional[str] = None,
        swap: Swap = Swap.REPLACE,
        trigger: Trigger = Trigger.SUBMIT,
        # function params - wrap around @dp.function
        cache: bool = False,
        submit_label: str = "Go",
        timer: int = 30,
    ):
        if controls is None:
            self.controls = Controls.empty()
        elif isinstance(controls, Controls):
            self.controls = controls
        else:  # iterable
            self.controls = Controls(*controls)

        self.function = function
        self.cache = cache
        self.target = target

        # NOTE - using id for the function_id means we can't persist sessions
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
            opt_attribs.update(timer=timer)

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
