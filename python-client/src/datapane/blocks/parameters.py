"""
Parameter handling, each instance supports,
- converting to XML for sending to the FE
- conversion into a Pydantic field for validating on the BE during an RPC call

# TODO - fix generics
"""
from __future__ import annotations

import abc
import base64
import io
import json
import tempfile
import typing as t
from datetime import date, datetime, time
from pathlib import Path
from types import EllipsisType

import pydantic as pyd
from lxml.builder import ElementMaker
from lxml.etree import _Element as Element

from datapane.common import SDict, SList
from datapane.common.viewxml_utils import mk_attribs

E = ElementMaker()
X = t.TypeVar("X")
Field = t.Tuple[t.Type, t.Union[t.Any, EllipsisType]]
ValidatorF = t.Callable[[X], X]


class Parameter(abc.ABC, t.Generic[X]):
    _T: X
    _tag: str
    cacheable: bool = True

    def __init__(self, name: str, label: t.Optional[str], default: t.Union[X, EllipsisType]):
        # NOTE - in pydantic, `...` is used to denote a required value
        self.name = name
        self.label = label
        self.default = default

        # NOTE - currently we use default as initial and set required based on default also
        required = self.default is ...
        initial = self._proc_initial(self.default) if self.default is not ... else None
        self.attribs: SDict = dict(name=self.name, label=self.label, required=required, initial=initial)

    def _proc_initial(self, x: X) -> t.Any:
        return x

    def _as_field(self) -> Field:
        return (self._T, self.default)

    def _validator(self) -> ValidatorF:
        # return identity
        return lambda x: x

    def _to_xml(self) -> Element:
        return getattr(E, self._tag)(**self._attribs)

    @property
    def _attribs(self) -> SDict:
        return mk_attribs(**self.attribs)


class Switch(Parameter[bool]):
    _T = bool
    _tag = "Switch"

    def __init__(self, name: str, label: t.Optional[str] = None, default: bool = ...):
        super().__init__(name, label, default)


class TextBox(Parameter[str]):
    _T = str
    _tag = "TextBox"

    def __init__(self, name: str, label: t.Optional[str] = None, default: str = ...):
        super().__init__(name, label, default)


class NumberBox(Parameter[float]):
    _T = float
    _tag = "NumberBox"

    def __init__(self, name: str, label: t.Optional[str] = None, default: float = ...):
        super().__init__(name, label, default)


class Range(Parameter):
    _T = float
    _tag = "Range"

    def __init__(
        self,
        name: str,
        label: t.Optional[str] = None,
        default: int = ...,
        min: t.Optional[int] = None,
        max: t.Optional[int] = None,
        step: t.Optional[int] = None,
    ):
        super().__init__(name, label, default)
        self.min = min
        self.max = max
        self.step = step

    def _as_field(self) -> Field:
        return (pyd.confloat(ge=self.min, le=self.max), self.default)

    def _to_xml(self) -> Element:
        attribs = mk_attribs(**self.attribs, min=self.min, max=self.max, step=self.step)
        return E.Range(**attribs)


class Choice(Parameter[str]):
    """Choose a single element from a set"""

    _T = str
    _tag = "Choice"

    def __init__(
        self,
        name: str,
        label: t.Optional[str] = None,
        default: str = ...,
        options: SList = None,
    ):
        # valid params
        assert options
        assert (default in options) if (default is not ...) else True
        super().__init__(name, label, default)
        self.options = options

    def _validator(self) -> ValidatorF[str]:
        def f(x: str):
            assert x in self.options, "not in options"
            return x

        return f

    def _to_xml(self) -> Element:
        attribs = mk_attribs(**self.attribs, choices=json.dumps(self.options))
        return E.Choice(**attribs)


class MultiChoice(Parameter[SList]):
    """Choose nultiple elements from a set"""

    _T = SList
    _tag = "MultiChoice"

    def __init__(
        self,
        name: str,
        label: t.Optional[str] = None,
        default: SList = ...,
        options: SList = None,
    ):
        # valid params
        assert options
        assert (self._check(default, options)) if (default is not ...) else True
        super().__init__(name, label, default)
        self.options = options

    def _check(self, xs: SList, ys: SList):
        return set(xs).issubset(ys)

    def _validator(self) -> ValidatorF[SList]:
        def f(xs: SList):
            assert self._check(xs, self.options), "not in options"
            return xs

        return f

    def _proc_initial(self, x: X) -> t.Any:
        return json.dumps(x)

    def _to_xml(self) -> Element:
        attribs = mk_attribs(**self.attribs, choices=json.dumps(self.options))
        return E.MultiChoice(**attribs)


class Tags(Parameter[SList]):
    """Create a list of strings"""

    _T = SList
    _tag = "Tags"

    def __init__(
        self,
        name: str,
        label: t.Optional[str] = None,
        default: SList = ...,
    ):
        super().__init__(name, label, default)

    def _proc_initial(self, x: X) -> t.Any:
        return json.dumps(x)


class Date(Parameter[date]):
    _T = date
    _tag = "Date"

    def __init__(
        self,
        name: str,
        label: t.Optional[str] = None,
        default: date = ...,
    ):
        super().__init__(name, label, default)

    def _proc_initial(self, x: date) -> t.Any:
        return x.isoformat()


class Time(Parameter[time]):
    _T = time
    _tag = "Time"

    def __init__(
        self,
        name: str,
        label: t.Optional[str] = None,
        default: time = ...,
    ):
        super().__init__(name, label, default)

    def _proc_initial(self, x: time) -> t.Any:
        return x.isoformat()


class DateTime(Parameter[datetime]):
    _T = datetime
    _tag = "DateTime"

    def __init__(
        self,
        name: str,
        label: t.Optional[str] = None,
        default: datetime = ...,
    ):
        super().__init__(name, label, default)

    def _proc_initial(self, x: datetime) -> t.Any:
        return x.isoformat()


class B64Path(Path):
    """Pydantic custom type based upon Path object"""

    # HACk to deal with Path not being directly subclassable (fix in Py3.12)
    _flavour = type(Path())._flavour

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: str):
        """Decode and save the b64 string to a temp file on disk"""
        f_v = io.StringIO(v)
        with tempfile.NamedTemporaryFile("wb", delete=False, prefix="dp-uploaded-") as out_f:
            base64.decode(f_v, out_f)
        return cls(out_f.name)


class File(Parameter[B64Path]):
    _T = t.Optional[B64Path]
    _tag = "File"
    # NOTE - currently cacheable controls will make an interactive block as non-cacheable
    # we could use sha of the file eventually
    cacheable = False

    def __init__(
        self,
        name: str,
        label: t.Optional[str] = None,
        default: t.Optional[B64Path] = ...,
    ):
        # Set default to None to mark an optional File
        super().__init__(name, label, default)

    def _validator(self) -> ValidatorF:
        # bit hacky, but create a Path object from the internal B64Path object
        def f(x: B64Path):
            assert x.is_file() and x.exists()
            return Path(x)

        return f
