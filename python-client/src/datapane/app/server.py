"""
Basic app server implementation, using,
- chroot as the web server
- bottle as a WSGI micro-framework
- custom json-rpc dispatcher
"""
import inspect
import shutil
import tempfile
import typing as t
from pathlib import Path

import bottle as bt
from cheroot.ssl import builtin
from cheroot.wsgi import Server

from datapane.blocks import Controls
from datapane.client import display_msg, log
from datapane.common.dp_types import SECS_1_HOUR
from datapane.common.utils import guess_type
from datapane.processors.processors import ExportBaseHTMLOnly
from datapane.view import View

from .json_rpc import dispatch
from .plugins import DPBottlePlugin
from .runtime import GlobalState, InteractiveRef, f_cache, get_session_state

########################################################################
# App Server
# TODO
#  - caching

app: bt.Bottle = bt.Bottle()
# Update app config
app.config.update(
    {
        # 'autojson': True,
        # "dp_bottle.session_timeout": SECS_1_HOUR,
        "dp_bottle.CORS": "*",
    }
)


# Test API endpoint
@app.get("/hello/")
def hello():
    return "Hello World!"


# @app.get("/assets/<filename>")
def serve_file(global_state: GlobalState, filename: str):
    _ = get_session_state()

    # pull from the asset store, or directly from the file?
    headers = {
        "Content-Encoding": "gzip",
        "Cache-Control": f"private, max-age={SECS_1_HOUR}, must-revalidate, no-transform, immutable",
    }
    root = global_state.app_dir / "assets"
    mime = guess_type(root / filename)
    log.info(f"Serving asset file {filename=} ({mime=})")
    return bt.static_file(filename=filename, root=root, mimetype=mime, headers=headers)


@app.get("/")
def initial_app() -> str:
    # TODO - cache this
    # this is kinda hacky, reusing the template system
    # for exporting reports here for the chrome only
    html = ExportBaseHTMLOnly().generate_chrome()
    return html


def serve(
    entry: t.Union[View, t.Callable[[], View]], port: int = 8080, host: str = "localhost", debug: bool = False
) -> None:
    """Main app serve entrypoint"""
    # setup GlobalState
    f_cache.clear()
    # set up the initial env
    app_dir = Path(tempfile.mkdtemp(prefix="dp-"))
    assets_dir = app_dir / "assets"
    assets_dir.mkdir(parents=True)

    # hardcode the main app entry
    if inspect.isfunction(entry):
        entry_f = lambda params: entry()  # noqa: E731
        cache = False
    else:
        entry_f = lambda params: entry  # noqa: E731
        cache = True
    main_entry = InteractiveRef(f=entry_f, controls=Controls.empty(), f_id="app.main", cache=cache)
    g_s = GlobalState(app_dir, main_entry)

    # TODO - move the app inside main func?
    app.route("/dispatch/", ["POST"], lambda: dispatch(g_s))
    app.route("/assets/<filename>", ["GET"], lambda filename: serve_file(g_s, filename))

    # start the server
    app.config.update({})
    app.install(DPBottlePlugin(g_s))

    try:
        display_msg(f"Server started at {host}:{port}")
        if debug:
            # TODO - add the CDN route here too
            bt.run(app, server="wsgiref", host=host, port=port, debug=True)
        else:
            bt.run(app, server="cheroot", host=host, port=port, interval=1, reloader=False)
    except KeyboardInterrupt:
        pass
    finally:
        app.close()
        shutil.rmtree(app_dir, ignore_errors=True)
        log.info("Shutting down server")

    # start_server(app)


def start_server(app, host: str = "localhost", port: int = 8080, **kwargs):
    """Start the dedicated, performant, cheroot server for the WSGI bottle app"""
    log.info(f"Starting server on {host}:{port}")

    certfile = kwargs.pop("certfile", None)
    keyfile = kwargs.pop("keyfile", None)
    chainfile = kwargs.pop("chainfile", None)

    server = Server(bind_addr=(host, port), wsgi_app=app)
    if certfile and keyfile:
        server.ssl_adapter = builtin.BuiltinSSLAdapter(certfile, keyfile, chainfile)
    try:
        server.start()
    finally:
        server.stop()
