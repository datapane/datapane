from __future__ import annotations

import dataclasses as dc
import typing as t
from pathlib import Path

from datapane.common import ViewXML
from datapane.view import View

from .file_store import FileEntry, FileStore

if t.TYPE_CHECKING:
    from datapane.app.runtime import InteractiveRef


@dc.dataclass
class ViewState:
    # maybe a FileHandler interface??
    view: View
    file_entry_klass: dc.InitVar[t.Type[FileEntry]]
    store: FileStore = dc.field(init=False)
    view_xml: ViewXML = ""
    entries: t.Dict[str, InteractiveRef] = dc.field(default_factory=dict)
    dir_path: dc.InitVar[t.Optional[Path]] = None

    def __post_init__(self, file_entry_klass, dir_path):
        # TODO - should we use a lambda for file_entry_klass with dir_path captured?
        self.store = FileStore(fw_klass=file_entry_klass, assets_dir=dir_path)


# Step = t.Callable[[ViewState, t.Any], t.Tuple[ViewState, t.Any]]


# TODO - type this properly
class Pipeline:
    """A simple, programmable, eagerly-evaluated, pipeline specialised on ViewAST transformations"""

    # TODO - should we just use a lib for this?

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


class BaseProcessor:
    """
    Processor class that handles pipeline operations
    # TODO - should we just make state an attribute here instead of threading?
    """

    s: ViewState
    #
    # @contextmanager
    # def update_state(self):
    #     # return a copy of state
    #     yield self.state
    #     # modifiy state here??
    #
    # @property
    # def sstate(self) -> ViewState:
    #     return self.state
    #
    # @sstate.setter
    # def sstate(self, x: ViewState):
    #     self.state = x

    def __call__(self, _: t.Any) -> t.Any:
        raise NotImplementedError("Implement in subclass")
