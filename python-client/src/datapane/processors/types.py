from __future__ import annotations

import dataclasses as dc
import typing as t
from enum import Enum
from pathlib import Path

from datapane.common import ViewXML
from datapane.view import Blocks

from .file_store import DummyFileEntry, FileEntry, FileStore


@dc.dataclass
class ViewState:
    # maybe a FileHandler interface??
    blocks: Blocks
    file_entry_klass: dc.InitVar[t.Type[FileEntry]]
    store: FileStore = dc.field(init=False)
    view_xml: ViewXML = ""
    entries: t.Dict[str, str] = dc.field(default_factory=dict)
    dir_path: dc.InitVar[t.Optional[Path]] = None

    def __post_init__(self, file_entry_klass, dir_path):
        # TODO - should we use a lambda for file_entry_klass with dir_path captured?
        self.store = FileStore(fw_klass=file_entry_klass, assets_dir=dir_path)


P_IN = t.TypeVar("P_IN")
P_OUT = t.TypeVar("P_OUT")


class BaseProcessor(t.Generic[P_IN, P_OUT]):
    """Processor class that handles pipeline operations"""

    s: ViewState

    def __call__(self, x: P_IN) -> P_OUT:
        raise NotImplementedError("Implement in subclass")


# TODO - type this properly
class Pipeline(t.Generic[P_IN]):
    """
    A simple, programmable, eagerly-evaluated, pipeline specialised on ViewAST transformations
    similar to f :: State s => s ViewState x -> s ViewState y
    """

    # NOTE - toolz has an untyped function for this

    def __init__(self, s: ViewState, x: P_IN = None):
        self._state = s
        self._x = x

    def pipe(self, p: BaseProcessor[P_IN, P_OUT]) -> Pipeline[P_OUT]:
        p.s = self._state
        y = p.__call__(self._x)  # need to call as positional args
        self._state = p.s
        return Pipeline(self._state, y)

    @property
    def state(self) -> ViewState:
        return self._state

    @property
    def result(self) -> P_IN:
        return self._x


def mk_null_pipe(blocks: Blocks) -> Pipeline[None]:
    s = ViewState(blocks, file_entry_klass=DummyFileEntry)
    return Pipeline(s)


# Top-level API options / types
class Width(Enum):
    NARROW = "narrow"
    MEDIUM = "medium"
    FULL = "full"

    def to_css(self) -> str:
        if self == self.NARROW:
            return "max-w-3xl"
        elif self == self.MEDIUM:
            return "max-w-screen-xl"
        else:
            return "max-w-full"


class TextAlignment(Enum):
    JUSTIFY = "justify"
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"


class FontChoice(Enum):
    DEFAULT = "Inter, ui-sans-serif, system-ui"
    SANS = "ui-sans-serif, sans-serif, system-ui"
    SERIF = "ui-serif, serif, system-ui"
    MONOSPACE = "ui-monospace, monospace, system-ui"


# Currently unused
# class PageLayout(Enum):
#     TOP = "top"
#     SIDE = "side"


@dc.dataclass
class Formatting:
    """Configure styling and formatting"""

    bg_color: str = "#FFF"
    accent_color: str = "#4E46E5"
    font: t.Union[FontChoice, str] = FontChoice.DEFAULT
    text_alignment: TextAlignment = TextAlignment.LEFT
    width: Width = Width.MEDIUM
    light_prose: bool = False

    def to_css(self) -> str:
        if isinstance(self.font, FontChoice):
            font = self.font.value
        else:
            font = self.font

        return f""":root {{
    --dp-accent-color: {self.accent_color};
    --dp-bg-color: {self.bg_color};
    --dp-text-align: {self.text_alignment.value};
    --dp-font-family: {font};
}}"""
