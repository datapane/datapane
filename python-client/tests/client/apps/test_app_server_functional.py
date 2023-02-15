import dataclasses as dc
import json
import random
import typing as t
from contextlib import contextmanager
from datetime import datetime

import dacite
from lxml import etree
from webtest import TestApp, TestResponse

import datapane as dp
from datapane.app import server
from datapane.app.json_rpc import RpcError, RpcRequest, RpcResponse
from datapane.app.plugins import DPBottlePlugin
from datapane.builtins import gen_df, gen_plot
from datapane.common.dp_types import URL, SDict
from datapane.common.viewxml_utils import ElementT

from .test_function_views import mk_controls


@dc.dataclass
class AssetDTO:
    """Asset objects returned from server"""

    hash: str
    mime: str
    size: int
    src: URL


@dc.dataclass
class ViewXMLDTO:
    """Successful RPC result representing a ViewXML fragment command"""

    is_fragment: bool
    view_xml: str
    assets: t.Dict[str, AssetDTO]
    root: ElementT = dc.field(init=False)

    def __post_init__(self):
        self.root = etree.fromstring(self.view_xml)

    @property
    def functions(self) -> t.List[ElementT]:
        # return the function specified by the index
        return self.root.findall(".//Function")


@contextmanager
def mk_app(view: dp.View) -> t.ContextManager[t.Tuple[TestApp, DPBottlePlugin]]:
    """Wrap a View into a instrumented WSGI local app"""
    bt_app, cleanup_f = server.build_app(view, debug=True)
    dp_plugin: DPBottlePlugin = bt_app.plugins[-1]
    assert isinstance(dp_plugin, DPBottlePlugin)
    app = TestApp(bt_app)
    yield (app, dp_plugin)
    cleanup_f()


def mk_rpc_req(f_name: str, *args, **kwargs) -> RpcRequest:
    """Build a json-rpc request"""
    assert not (kwargs and args), "only support args or kwargs, not both"
    _args = kwargs or list(args)
    return RpcRequest(jsonrpc="2.0", id=random.randint(1, 1000), method=f_name, params=_args.copy())


def call_rpc(app: TestApp, f_name: str, **kwargs) -> ViewXMLDTO:
    """Make a synthetic json-rpc request/response call to the app server"""
    rpc_req = mk_rpc_req(f_name, **kwargs)
    http_res: TestResponse = app.post_json("/dispatch/", rpc_req.dict())

    assert http_res.status_int == 200
    assert http_res.content_type == "application/json"
    http_res_dict = http_res.json
    # convert to rpc response
    if "result" in http_res_dict:
        rpc_res = RpcResponse(**http_res_dict)
        assert rpc_req.id == rpc_res.id
        return dacite.from_dict(ViewXMLDTO, rpc_res.result)
    elif "error" in http_res_dict:
        rpc_res = RpcError(**http_res_dict)
        if rpc_res.id:
            assert rpc_req.id == rpc_res.id
        raise AssertionError(rpc_res)
    else:
        raise AssertionError(f"Unknown response - {http_res_dict}")


def bootup_app(app: TestApp, dp_plugin: DPBottlePlugin, *, expected_assets: int = 0) -> ViewXMLDTO:
    """Boot up the app and assert that app.main has been called successfully"""
    # get the initial chrome
    assert not app.cookies
    res: TestResponse = app.get("/")
    assert res.status_int == 200
    assert res.has_body
    assert res.content_type == "text/html"
    assert "mountReport" in res
    assert res.lxml.find(".//div[@id='report']") is not None

    # have we added the user session
    assert app.cookies
    assert "dp_session_id" in app.cookies
    initial_cookies = app.cookies.copy()

    # let's call app.main
    main_res = call_rpc(app, "app.main")
    assert not main_res.is_fragment
    assert len(main_res.assets) == expected_assets
    # check same session
    assert initial_cookies == app.cookies
    assert len(dp_plugin.sessions._cache) == 1
    return main_res


def call_dp_function(
    app: TestApp, res: ViewXMLDTO, *, dp_fun: dp.Function = None, f_idx: int = 0, params: t.Dict = None
) -> ViewXMLDTO:
    """Helper to call a dp.Function referened in a View fragment via json-rpc"""
    params = params or {}
    fun = res.functions[f_idx]
    if dp_fun:
        assert fun.get("function_id") == dp_fun.function_id
    res1 = call_rpc(app, fun.get("function_id"), **params)
    assert res1.is_fragment
    return res1


def test_basic():
    """Test serving a simple view with no assets or functions"""
    view = dp.View("Hello World")

    with mk_app(view) as (app, dp_plugin):
        main_res = bootup_app(app, dp_plugin)
        assert not main_res.functions
        assert main_res.root.find("./Text").text == "Hello World"


def test_assets():
    """Test serving a simple view with assets"""
    view = dp.View("Hello World", gen_df(), gen_plot())

    with mk_app(view) as (app, dp_plugin):
        main_res = bootup_app(app, dp_plugin, expected_assets=2)
        assert not main_res.functions

        # let's try pull some assets
        # TODO - check the asset is the same as the initial...
        for asset in main_res.assets.values():
            _res: TestResponse = app.get(asset.src)
            assert _res.status_int == 200
            assert _res.content_type == asset.mime


def test_functions():
    """Test calling a simple view with a single function"""

    def f(params):
        assert params == {}
        return dp.View("Fragment Hello")

    dp_fun = dp.Function(f, target="x")
    view = dp.View(dp_fun)

    with mk_app(view) as (app, dp_plugin):
        main_res = bootup_app(app, dp_plugin)

        # call the function
        res1 = call_dp_function(app, main_res, dp_fun=dp_fun)
        assert res1.root.find("./Text").text == "Fragment Hello"


def test_nested_functions():
    """Test calling a view with a nested / linked function"""

    def f(params):
        x = 1

        def g(params):
            assert params == {}
            assert x == 1
            return dp.View(f"Nested Fragment Hello - {x}")

        assert params == {}
        return dp.Function(g, target="y")

    view = dp.View(dp.Function(f, target="x"))

    with mk_app(view) as (app, dp_plugin):
        main_res = bootup_app(app, dp_plugin)
        # call the function
        res1 = call_dp_function(app, main_res)
        res2 = call_dp_function(app, res1)
        assert res2.root.find("./Text").text == "Nested Fragment Hello - 1"


def test_session_state():
    """Test that session state works across multiple functions in a View"""

    def f(params, session: t.Dict):
        session["count"] = session.get("count", 0) + 1
        return dp.View(dp.Empty("z"))

    def g(params, session: t.Dict):
        return dp.View(f"count - {session['count']}")

    view = dp.View(dp.Function(f, target="x"), dp.Function(g, target="y"))

    with mk_app(view) as (app, dp_plugin):
        main_res = bootup_app(app, dp_plugin)
        # make the session function calls
        _ = call_dp_function(app, main_res, f_idx=0)
        _ = call_dp_function(app, main_res, f_idx=0)
        _ = call_dp_function(app, main_res, f_idx=0)
        res2 = call_dp_function(app, main_res, f_idx=1)
        assert res2.root.find("./Text").text == "count - 3"


def test_controls():
    """Test that control inputs can be passed into a function in a view and used sucessfully"""
    controls = mk_controls()

    def mk_str_dict(d: SDict) -> str:
        return json.dumps({k: str(v) for k, v in d.items()})

    def f(params: t.Dict, switch: bool, textbox: str):
        assert ["switch", "textbox"] + list(params.keys()) == [p.name for p in controls.params]
        params1 = {**dict(switch=switch, textbox=textbox), **params}
        return dp.View(mk_str_dict(params1))

    view = dp.View(dp.Function(f, controls=controls, target="x"))

    with mk_app(view) as (app, dp_plugin):
        main_res = bootup_app(app, dp_plugin)

        # make the function call
        _datetime = datetime.utcnow()
        input_params = dict(
            switch=True,
            textbox="2",
            numberbox=2.0,
            range=3.0,
            choice="1",
            multichoice=["2"],
            tags=["a", "b"],
            date=_datetime.date().isoformat(),
            datetime=_datetime.isoformat(sep=" "),
            time=_datetime.time().isoformat(),
        )
        # call with no input
        _ = call_dp_function(app, main_res)
        # call with input
        f_res1 = call_dp_function(app, main_res, params=input_params)
        # check round-trip
        assert f_res1.root.find("./Text").text == mk_str_dict(input_params)
