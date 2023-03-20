from __future__ import annotations

import dataclasses as dc
import inspect
import pickle
import random
import secrets
import shutil
import sys
import typing as t
import uuid
from pathlib import Path

from boltons.cacheutils import LRU
from pydantic import ValidationError

import datapane._vendor.bottle as bt
from datapane.blocks import Controls, Swap
from datapane.client import log
from datapane.processors import AppTransformations, ConvertXML, Pipeline, PreProcessView, ViewState
from datapane.processors.file_store import GzipTmpFileEntry
from datapane.view import Blocks

if t.TYPE_CHECKING:
    from datapane.common.dp_types import SDict


@dc.dataclass
class FunctionRef:
    f: t.Callable
    controls: Controls
    f_id: str
    swap: Swap = Swap.REPLACE
    # other (decorator) params, ...
    cache: bool = False
    state: bool = dc.field(init=False)
    needs_param: bool = dc.field(init=False)
    # reset: bool

    def __post_init__(self):
        # validate the function
        f_sig = inspect.signature(self.f)
        self.state = "session" in f_sig.parameters

        if "params" in f_sig.parameters:
            self.needs_param = True
        else:
            # check the function has explicit args for all controls
            missing_params = self.controls.param_names - set(f_sig.parameters.keys())
            self.needs_param = bool(missing_params)
            if self.needs_param:
                raise ValueError(
                    f"{self.f} needs either a `params` argument or to handle additional parameters - {missing_params}"
                )

        if self.state or not self.controls.is_cacheable:
            if self.cache:
                log.debug(f"Disabling cache hint for {self.f}")
            self.cache = False

        if self.cache:
            log.debug(f"Enabling experimental cache support for {self.f}")

        log.debug(f"Registered {self.f} ({self.cache=}, {self.state=})")


FEntries = t.Dict[str, FunctionRef]


@dc.dataclass
class GlobalState:
    """Stored within the lifetime of an App and passed through to handlers"""

    app_dir: Path
    main: FunctionRef
    # todo - make threadsafe
    state: SDict = dc.field(default_factory=dict)
    server_id: str = dc.field(default_factory=lambda: uuid.uuid4().hex)
    function_cache: LRU[t.Tuple[str, bytes], ViewState] = dc.field(default_factory=lambda: LRU(max_size=128))

    def clear(self) -> None:
        """Wipe global state - called on app.close"""
        self.function_cache.clear()
        self.state.clear()
        shutil.rmtree(self.app_dir, ignore_errors=True)


@dc.dataclass
class SessionState:
    """Per-user / session state"""

    s_id: str = dc.field(init=False)
    user: str = "anonymous"
    # dict of assets - TODO - type this
    assets: t.Dict = dc.field(default_factory=dict)
    # app function entry points
    entries: FEntries = dc.field(default_factory=dict)
    # internal session storage
    user_state: t.Dict[str, t.Any] = dc.field(default_factory=dict)

    def __post_init__(self):
        self.s_id = secrets.token_urlsafe(18)

    def add_entry(self, app_entry: FunctionRef) -> None:
        """Add the entry to the known entries for the state"""
        self.entries[app_entry.f_id] = app_entry

    def apply_view_state(self, view_state: ViewState) -> None:
        # mutate session state based on latest view update
        self.assets.update(view_state.store.as_dict())
        self.entries.update(view_state.entries)

    def __hash__(self) -> int:
        # TODO - implement a proper hash function for session state
        return random.randint(0, sys.maxsize)


def get_session_state() -> SessionState:
    """Relies on the TLS request object"""
    return t.cast(SessionState, bt.request.session)


def get_global_state() -> GlobalState:
    return ...


def apply_ref(g_s: GlobalState, s_s: SessionState, ref: FunctionRef, params: t.Dict) -> t.Dict:
    """
    Run the referenced app function with the given parameters and return the result
    suitable for encoding in an RPC response
    """
    from .json_rpc import RPCException

    def check_cache() -> t.Optional[t.Dict]:
        # do we have this in the cache??
        if ref.cache:
            _key = (ref.f_id, pickle.dumps(params))
            f_cache = g_s.function_cache
            _val: t.Optional[ViewState] = f_cache.get(_key)
            _hit_ratio = (f_cache.hit_count / (f_cache.soft_miss_count + f_cache.hit_count)) * 100
            log.debug(f"Cache info - {f_cache.soft_miss_count} misses, {f_cache.hit_count} hits ({_hit_ratio:.2f}%)")

            if _val:
                log.debug("Got cache hit for request")
                return build_rpc_res(_val)
        return None

    def store_cache(vs: ViewState) -> None:
        if ref.cache:
            _key = (ref.f_id, pickle.dumps(params))
            g_s.function_cache[_key] = vs

    def gen_args():
        # "massage" the parameters to the function
        try:
            ParamsModel = ref.controls._to_pydantic()
            params_model = ParamsModel(**params)
            in_params: dict = params_model.dict()

        except ValidationError as e:
            # TODO - fix json-rpc id handling here
            raise RPCException(-32602, "Invalid Parameters", data=e.errors()) from e

        # function arg handling / binding
        f_sig = inspect.signature(ref.f, follow_wrapped=True)

        # unpack params
        kwargs = {}
        for k in list(in_params.keys()):
            if k in f_sig.parameters:
                kwargs[k] = in_params.pop(k)

        # add params if needed
        if ref.needs_param:
            kwargs["params"] = in_params
        elif len(in_params) > 0:
            log.warning(f"'params' not present in {ref.f} but additional parameters present - {in_params}, dropping")

        # add optional state param
        if ref.state:  # "state" in f_sig.parameters:
            kwargs["session"] = s_s.user_state

        f_args = f_sig.bind(**kwargs)
        f_args.apply_defaults()
        return f_args

    is_fragment = ref.f_id != "app.main"

    def build_view(res) -> ViewState:
        # Build a view for serving, using the view_ast as a base state and storing assets in dest
        # TODO - use ref.swap to validate return type
        blocks = Blocks.wrap_blocks(res)
        assets_dir = g_s.app_dir / "assets"

        # write the app html and assets
        vs = ViewState(blocks=blocks, file_entry_klass=GzipTmpFileEntry, dir_path=assets_dir)

        return (
            Pipeline(vs)
            .pipe(PreProcessView(is_finalised=False))
            .pipe(AppTransformations())
            .pipe(ConvertXML(fragment=is_fragment))
            .state
        )

    def build_rpc_res(vs: ViewState) -> dict:
        # we need to reapply the viewstate for the specific user session
        s_s.apply_view_state(vs)
        return dict(is_fragment=is_fragment, view_xml=vs.view_xml, assets=vs.store.as_dict())

    ############################################################################
    # Core logic
    if rpc_res := check_cache():
        return rpc_res

    # call the function with the processed input parameters
    f_args = gen_args()
    res = ref.f(*f_args.args, **f_args.kwargs)
    # build the view response
    vs = build_view(res)
    # construct the RPC return
    rpc_res = build_rpc_res(vs)
    store_cache(vs)

    return rpc_res
