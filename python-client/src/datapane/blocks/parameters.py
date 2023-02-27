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
import math
import tempfile
import typing as t
from datetime import date, datetime, time
from pathlib import Path

import pydantic as pyd
from lxml.builder import ElementMaker
from lxml.etree import _Element as Element

from datapane.client.exceptions import DPClientError
from datapane.common import SDict, SList
from datapane.common.viewxml_utils import mk_attribs

E = ElementMaker()
X = t.TypeVar("X")
Field = t.Tuple[t.Type, t.Any]
ValidatorF = t.Callable[[X], X]

Numeric = t.Union[float, int]


class Parameter(abc.ABC, t.Generic[X]):
    _T: type[X]
    _tag: str
    cacheable: bool = True
    name: t.Optional[str]
    attribs: SDict

    def __init__(
        self,
        name: t.Optional[str] = None,
        label: t.Optional[str] = None,
        initial: t.Optional[X] = None,
        *,
        allow_empty: bool = False,
    ):
        if name == "":
            raise DPClientError(f"A non empty name must be provided, got '{name}'")
        if label == "":
            raise DPClientError("label must be a non-empty string or None")
        self.name = name
        self.label = label
        self.initial = initial

        initial_attrib = self._proc_initial(self.initial) if self.initial is not None else None
        self.attribs = dict(name=self.name, label=self.label, required=not allow_empty, initial=initial_attrib)

    def _check_instance(self):
        """
        Perform basic checks that the Parameter was constructed correctly.
        """
        # This method throws a fairly clear error if user passes bad strings,
        # which we want to catch as soon as possible.

        # `self.name` can be set by our parent (`dp.Controls`) for rendering.
        # This makes `self.name is None` valid for the class instance, just not for the XML.
        self._to_xml(name=self.name or "DEFERRED")

    def _proc_initial(self, x: X) -> t.Any:
        return x

    def _as_field(self) -> Field:
        return (self._T, self.initial)

    def _validator(self) -> ValidatorF:
        # return identity
        return lambda x: x

    def _to_xml(self, *, name: t.Optional[str] = None) -> Element:
        return getattr(E, self._tag)(self.make_attribs(name=name))

    def make_attribs(self, *, name: t.Optional[str] = None) -> SDict:
        overlay = dict(name=name) if name is not None else {}
        return mk_attribs(**{**self.attribs, **overlay})


class Switch(Parameter[bool]):
    _T = bool
    _tag = "Switch"

    def __init__(
        self,
        name: t.Optional[str] = None,
        label: t.Optional[str] = None,
        *,
        initial: bool = False,
    ):
        """
        A switch allowing the user to select on/true or off/false

        Args:
            name: The name of the parameter.
            label: The label of the parameter, visible to the user.
            initial: The initial value of the parameter.
        """
        super().__init__(name, label, initial)
        self._check_instance()


class TextBox(Parameter[str]):
    _T = str
    _tag = "TextBox"

    def __init__(
        self,
        name: t.Optional[str] = None,
        label: t.Optional[str] = None,
        *,
        initial: str = "",
        allow_empty: bool = False,
    ):
        """
        A single-line text field where the user can enter data.

        Args:
            name: The name of the parameter.
            label: The label of the parameter, visible to the user.
            initial: The initial value of the parameter.
            allow_empty: Whether to allow the user to enter an empty string.
        """
        super().__init__(name, label, initial, allow_empty=allow_empty)
        self._check_instance()


class NumberBox(Parameter[float]):
    _T = float
    _tag = "NumberBox"

    def __init__(
        self,
        name: t.Optional[str] = None,
        label: t.Optional[str] = None,
        *,
        initial: float = 0,
    ):
        """
        A number field where the user can enter data.

        Args:
            name: The name of the parameter.
            label: The label of the parameter, visible to the user.
            initial: The initial value of the parameter.
        """
        super().__init__(name, label, initial)
        self._check_instance()


class Range(Parameter):
    _T = float
    _tag = "Range"

    def __init__(
        self,
        name: t.Optional[str] = None,
        label: t.Optional[str] = None,
        *,
        initial: Numeric,
        min: Numeric,
        max: Numeric,
        step: t.Optional[Numeric] = None,
    ):
        """
        A slider where the user can select a value within a range.

        Args:
            name: The name of the parameter.
            label: The label of the parameter, visible to the user.
            initial: The initial value of the parameter.
            min: The minimum allowed value of the parameter.
            max: The maximum allowed value of the parameter.
            step: The step size of the parameter.
        """
        super().__init__(name, label, self._T(initial))
        if any(isinstance(v, float) and (math.isinf(v) or math.isnan(v)) for v in (min, max, step)):
            raise DPClientError("min/max/step must not be `inf` or `nan`")
        self.min = self.attribs["min"] = self._T(min)
        self.max = self.attribs["max"] = self._T(max)
        self.step = self.attribs["step"] = None if step is None else self._T(step)
        self._check_instance()

    def _as_field(self) -> Field:
        return (pyd.confloat(ge=self.min, le=self.max), self.initial)


class Choice(Parameter[str]):
    _T = str
    _tag = "Choice"

    def __init__(
        self,
        name: t.Optional[str] = None,
        label: t.Optional[str] = None,
        *,
        options: SList,
        initial: t.Optional[str] = None,
    ):
        """
        A drop-down allowing the selection of a single value from a list.

        Args:
            name: The name of the parameter.
            label: The label of the parameter, visible to the user.
            options: The list of options to choose from.
            initial: The initial value of the parameter.
        """
        # valid params
        if not options:
            raise DPClientError("At least one option must be provided")
        if initial is not None and initial not in options:
            raise DPClientError(f"Initial value `{initial}` must be present in the options")
        if any(opt == "" for opt in options):
            raise DPClientError("All options must be non-empty strings")
        super().__init__(name, label, initial)
        self.options = options
        self.attribs.update(options=options)
        self._check_instance()

    def _validator(self) -> ValidatorF[str]:
        def f(x: str):
            assert x in self.options, "not in options"
            return x

        return f


class MultiChoice(Parameter[SList]):
    _T = SList
    _tag = "MultiChoice"

    def __init__(
        self,
        name: t.Optional[str] = None,
        label: t.Optional[str] = None,
        *,
        initial: SList = [],
        options: SList,
        allow_empty: bool = False,
    ):
        """
        A drop-down allowing the selection of a multiple values from a list.

        Args:
            name: The name of the parameter.
            label: The label of the parameter, visible to the user.
            options: The list of options to choose from.
            initial: The initial value of the parameter.
            allow_empty: Whether to allow the user to select no options.
        """
        # valid params
        initial = initial or []
        if not options:
            raise DPClientError("At least one option must be provided")
        if any(d not in options for d in initial):
            raise DPClientError(f"All items in default value `{initial}` must be present in the options")
        if any(opt == "" for opt in options):
            raise DPClientError("All options must be non-empty strings")
        super().__init__(name, label, initial, allow_empty=allow_empty)
        self.options = options
        self.attribs.update(options=options)
        self._check_instance()

    def _check(self, xs: SList, ys: SList):
        return set(xs).issubset(ys)

    def _validator(self) -> ValidatorF[SList]:
        def f(xs: SList):
            assert self._check(xs, self.options), "not in options"
            return xs

        return f


class Tags(Parameter[SList]):
    _T = SList
    _tag = "Tags"

    def __init__(
        self,
        name: t.Optional[str] = None,
        label: t.Optional[str] = None,
        *,
        initial: SList = [],
        allow_empty: bool = False,
    ):
        """
        A drop-down allowing the selection of multiple values from a list. Allows adding new items to the list.

        Args:
            name: The name of the parameter.
            label: The label of the parameter, visible to the user.
            initial: An initial selection of tags
            allow_empty: Whether to allow the user to select no tags.
        """
        initial = initial or []
        if any(x in ("", '"') for x in initial):
            raise DPClientError("Empty initial tags or those consisting of a single quote not supported")
        super().__init__(name, label, initial, allow_empty=allow_empty)
        self._check_instance()


class Date(Parameter[date]):
    _T = date
    _tag = "Date"

    def __init__(
        self,
        name: t.Optional[str] = None,
        label: t.Optional[str] = None,
        *,
        initial: t.Optional[date] = None,
    ):
        """
        A control allowing the selection of a date (`dd/mm/yyyy`).

        Args:
            name: The name of the parameter.
            label: The label of the parameter, visible to the user.
            initial: The initial value of the parameter.
        """
        super().__init__(name, label, initial)
        self._check_instance()

    def _proc_initial(self, x: date) -> t.Any:
        return x.isoformat()


class Time(Parameter[time]):
    _T = time
    _tag = "Time"

    def __init__(
        self,
        name: t.Optional[str] = None,
        label: t.Optional[str] = None,
        *,
        initial: t.Optional[time] = None,
    ):
        """
        A control allowing the entry of a time (`hh:mm:ss`).

        Args:
            name: The name of the parameter.
            label: The label of the parameter, visible to the user.
            initial: The initial value of the parameter.
        """
        super().__init__(name, label, initial)
        self._check_instance()

    def _proc_initial(self, x: time) -> t.Any:
        return x.isoformat()


class DateTime(Parameter[datetime]):
    _T = datetime
    _tag = "DateTime"

    def __init__(
        self,
        name: t.Optional[str] = None,
        label: t.Optional[str] = None,
        *,
        initial: t.Optional[datetime] = None,
    ):
        """
        A control allowing the selection of a date and time (`dd/mm/yyyy, hh:mm:ss`).

        Args:
            name: The name of the parameter.
            label: The label of the parameter, visible to the user.
            initial: The initial value of the parameter.
        """
        super().__init__(name, label, initial)
        self._check_instance()

    def _proc_initial(self, x: datetime) -> t.Any:
        return x.isoformat()


class B64Path(Path):
    """Pydantic custom type based upon Path object"""

    # Hack to deal with Path not being directly subclassable (fixed in Py3.12)
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
        name: t.Optional[str] = None,
        label: t.Optional[str] = None,
        initial: t.Optional[B64Path] = None,
        allow_empty: bool = False,
    ):
        """
        A control allowing the upload of a File from the user's device. Max size 25MB

        Args:
            name: The name of the parameter.
            label: The label of the parameter, visible to the user.
            initial: The initial value of the parameter.
            allow_empty: Whether to allow the user to not upload a file.
        """

        # Set default to None to mark an optional File
        super().__init__(name, label, initial, allow_empty=allow_empty)
        self._check_instance()

    def _validator(self) -> ValidatorF:
        # bit hacky, but create a Path object from the internal B64Path object
        def f(x: B64Path):
            assert x.is_file() and x.exists()
            return Path(x)

        return f

    def _proc_initial(self, x: X) -> t.Any:
        return None
