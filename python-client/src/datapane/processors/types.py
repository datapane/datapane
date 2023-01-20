from __future__ import annotations

import dataclasses as dc
import typing as t
from pathlib import Path

from datapane.common import ViewXML
from datapane.view import View

from .file_store import DummyFileEntry, FileEntry, FileStore

if t.TYPE_CHECKING:
    from datapane.app.runtime import FunctionRef


@dc.dataclass
class ViewState:
    # maybe a FileHandler interface??
    view: View
    file_entry_klass: dc.InitVar[t.Type[FileEntry]]
    store: FileStore = dc.field(init=False)
    view_xml: ViewXML = ""
    entries: t.Dict[str, FunctionRef] = dc.field(default_factory=dict)
    dir_path: dc.InitVar[t.Optional[Path]] = None

    def __post_init__(self, file_entry_klass, dir_path):
        # TODO - should we use a lambda for file_entry_klass with dir_path captured?
        self.store = FileStore(fw_klass=file_entry_klass, assets_dir=dir_path)


class BaseProcessor:
    """Processor class that handles pipeline operations"""

    s: ViewState

    def __call__(self, _: t.Any) -> t.Any:
        raise NotImplementedError("Implement in subclass")


# TODO - type this properly
class Pipeline:
    """
    A simple, programmable, eagerly-evaluated, pipeline specialised on ViewAST transformations
    similar to f :: State s => s ViewState x -> s ViewState y
    """

    # NOTE - toolz has an untyped function for this

    def __init__(self, s: ViewState, x: t.Any = None):
        self._state = s
        self._x = x

    def pipe(self, p: BaseProcessor) -> Pipeline:
        p.s = self._state
        y = p(self._x)  # need to call as positional args
        self._state = p.s
        return Pipeline(self._state, y)

    @property
    def state(self) -> ViewState:
        return self._state

    @property
    def result(self) -> t.Any:
        return self._x


def mk_null_pipe(view: View) -> Pipeline:
    s = ViewState(view, file_entry_klass=DummyFileEntry)
    return Pipeline(s)
