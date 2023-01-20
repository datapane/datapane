from __future__ import annotations

import dataclasses as dc
import inspect
import pickle
import random
import secrets
import sys
import typing as t
from copy import copy
from functools import wraps
from pathlib import Path

import bottle as bt
from boltons.cacheutils import LRU
from pydantic import ValidationError

from datapane.blocks import Controls, Swap
from datapane.client import log
from datapane.processors import AppTransformations, ConvertXML, Pipeline, PreProcessView, ViewState
from datapane.processors.file_store import GzipTmpFileEntry
from datapane.view import View

if t.TYPE_CHECKING:
    from .json_rpc import RPC_JSON

# global function cache
f_cache: LRU[t.Tuple[str, bytes], ViewState] = LRU(max_size=128)


@dc.dataclass
class FunctionRef:
    f: t.Callable
    controls: Controls
    f_id: str
    swap: Swap = Swap.REPLACE
    # other (decorator) params, ...
    cache: bool = False
    state: bool = dc.field(init=False)
    # reset: bool

    def __post_init__(self):
        # validate the function
        f_sig = inspect.signature(self.f)
        self.state = "state" in f_sig.parameters

        if "params" not in f_sig.parameters:
            # TODO - support optional params if all controls exists in the
            #  function signature as args/kwargs?
            raise ValueError(f"{self.f} needs a params argument")

        if self.state or not self.controls.is_cacheable:
            if self.cache:
                log.warning(f"Disabling cache hint for {self.f}")
            self.cache = False

        if self.cache:
            log.warning(f"Enabling experimental cache support for {self.f}")

        log.debug(f"Registered {self.f} ({self.cache=}, {self.state=})")


FEntries = t.Dict[str, FunctionRef]


@dc.dataclass
class GlobalState:
    """Stored within the lifetime of an App and passed through to handlers"""

    app_dir: Path
    main: FunctionRef


@dc.dataclass
class SessionState:
    """Per-user / session state"""

    session_id: str = dc.field(init=False)
    user: str = "anonymous"
    # dict of assets - TODO - type this
    assets: t.Dict = dc.field(default_factory=dict)
    # app function entry points
    entries: FEntries = dc.field(default_factory=dict)
    # internal session storage
    user_state: t.Dict[str, t.Any] = dc.field(default_factory=dict)

    def __post_init__(self):
        self.session_id = secrets.token_urlsafe(18)

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
            f_cache[_key] = vs

    def gen_args():
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

        # add optional state param
        if ref.state:  # "state" in f_sig.parameters:
            kwargs["state"] = s_s.user_state

        f_args = f_sig.bind(params=in_params, **kwargs)
        f_args.apply_defaults()
        return f_args

    def build_view(res) -> ViewState:
        # Build a view for serving, using the view_ast as a base state and storing assets in dest
        # TODO - use ref.swap to validate return type
        view: View
        if isinstance(res, View):
            view = copy(res)
        elif isinstance(res, list):
            view = View(*res)
        else:
            view = View(res)

        assets_dir = g_s.app_dir / "assets"

        # write the app html and assets
        vs = ViewState(view=view, file_entry_klass=GzipTmpFileEntry, dir_path=assets_dir)
        return Pipeline(vs).pipe(PreProcessView()).pipe(AppTransformations()).pipe(ConvertXML()).state

    def build_rpc_res(vs: ViewState) -> dict:
        # we need to reapply the viewstate for the specific user session
        s_s.apply_view_state(vs)
        return dict(is_fragment=ref.f_id != "app.main", view_xml=vs.view_xml, assets=vs.store.as_dict())

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


def dp_function(name: str, cache: bool = False, state: bool = False):
    """Main function wrapper function
    - unpacks params / args as needed, etc.
    # NOTE - currently unused - will be a helper instead
    """

    def decorator(f: t.Callable):
        @wraps(f)
        def wrapper(s_s: SessionState, *args, **kwargs) -> View:
            print(s_s, args, kwargs)
            # TODO
            #  - apply into `params` object?
            #  - pass in user_state
            #  - pydantic signature validation
            res = f(*args, **kwargs)

            if isinstance(res, View):
                return res
            elif isinstance(res, list):
                return View(blocks=res)
            else:
                return View(blocks=[res])

        return wrapper

    return decorator


# DP System Functions
def hello_rpc(g_s: GlobalState, s_s: SessionState, name: str) -> RPC_JSON:
    return [f"Hello {name}"]


def reset(g_s: GlobalState, s_s: SessionState) -> RPC_JSON:
    from .plugins import COOKIE_NAME

    # remove the user session
    # remove the cookie
    bt.response.delete_cookie(COOKIE_NAME)
    log.info(f"Resetting session for {s_s.session_id=}")
    return None


# global registry, all functions prefixed with dp.
global_rpc_functions: t.Dict[str, t.Callable[..., RPC_JSON]] = {"dp.hello_rpc": hello_rpc, "dp.reset": reset}
