"""## App runtime API

Runtime API used when running a Datapane App

..note:: The objects in this module are available on Datapane Enterprise
"""
import dataclasses as dc
import os
import typing as t
from collections import deque
from pathlib import Path

from datapane import ON_DATAPANE
from datapane.client.apps import DATAPANE_YAML, DatapaneCfg
from datapane.common import NPath, SDict, log

if t.TYPE_CHECKING:
    from .report.core import App

###############################################################################
# top level functions here - move to runner?
# TODO - make thread/context safe and determine a better approach for vars
# TODO - add API tests

__all__ = []  # type: ignore


# we're running the datapane runner (also checked by __name__ == "__datapane__" in user script)
# NOTE - is this materially different to ON_DATAPANE?
by_datapane: bool = ON_DATAPANE or "DATAPANE_BY_DATAPANE" in os.environ

_report: t.Deque["App"] = deque(maxlen=1)


class _Params(dict):
    def load_defaults(self, config_fn: NPath = DATAPANE_YAML) -> None:
        if not by_datapane:
            log.debug(f"loading parameter defaults from {config_fn}")
            # TODO - move dp-server parameter handling into common to use runnerconfig.format
            # NOTE - this is a bit hacky as we don't do any type formatting
            cfg = DatapaneCfg.create_initial(config_file=Path(config_fn))
            defaults = {p["name"]: p["default"] for p in cfg.parameters if "default" in p}
            self.update(defaults)
        else:
            log.debug("Ignoring call to load_defaults as by datapane")

    def replace(self, new_vals: dict) -> None:
        self.clear()
        self.update(new_vals)


Params: _Params = _Params()


@dc.dataclass
class _Result:
    result: t.Any = None

    def set(self, x: t.Any):
        self.result = x

    def get(self) -> t.Any:
        return self.result

    def exists(self) -> bool:
        return self.result is not None


Result = _Result()


def _reset_runtime(params: SDict):
    """Called between each script invocation"""
    # TODO - refactor this all and make thread/context-safe
    Params.clear()
    Params.update(params)
    Result.set(None)
