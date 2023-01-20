"""
Basic app server implementation, using,
- chroot as the web server
- bottle as a WSGI micro-framework
- custom json-rpc dispatcher
"""
import inspect
import os
import shutil
import tempfile
import typing as t
from pathlib import Path

import bottle as bt
import cheroot.ssl
import cheroot.wsgi
import importlib_resources as ir

from datapane.blocks import Controls
from datapane.client import log
from datapane.common.dp_types import SECS_1_HOUR, SIZE_1_MB
from datapane.common.utils import guess_type
from datapane.processors.processors import ExportBaseHTMLOnly
from datapane.view import View

from .json_rpc import dispatch
from .plugins import DPBottlePlugin
from .runtime import FunctionRef, GlobalState, f_cache, get_session_state

########################################################################
# App Server
# TODO
#  - caching

# globally set the max request size to 100 MB
bt.BaseRequest.MEMFILE_MAX = int(os.getenv("MAX_REQUEST_BODY", 100 * SIZE_1_MB))


def create_bottle_app(debug: bool) -> bt.Bottle:
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

    @app.get("/")
    def initial_app() -> str:
        # TODO - cache this
        # this is kinda hacky, reusing the template system
        # for exporting reports here for the chrome only
        html = ExportBaseHTMLOnly(debug).generate_chrome()
        return html

    if debug:
        root_dir: Path = t.cast(Path, ir.files("datapane"))
        web_dist_dir = root_dir.parent.parent.parent / "web-components" / "dist"

        @app.get("/web-static/<fpath:path>")
        def serve_web_static(fpath):
            # headers = {
            #     "Cache-Control": f"private, max-age={SECS_1_HOUR}, must-revalidate, no-transform, immutable",
            # }
            headers = {}
            return bt.static_file(filename=fpath, root=web_dist_dir, headers=headers)

    return app


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


def serve(
    entry: t.Union[View, t.Callable[[], View]],
    port: t.Optional[int] = None,
    host: str = "127.0.0.1",
    debug: bool = False,
) -> None:
    """
    Main app serve entrypoint.

    Pass `port` to run on a specific port, otherwise one will be chosen automatically.

    """
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
    main_entry = FunctionRef(f=entry_f, controls=Controls.empty(), f_id="app.main", cache=cache)
    g_s = GlobalState(app_dir, main_entry)

    app = create_bottle_app(debug)
    app.route("/dispatch/", ["POST"], lambda: dispatch(g_s))
    app.route("/assets/<filename>", ["GET"], lambda filename: serve_file(g_s, filename))

    # start the server
    app.config.update({})
    app.install(DPBottlePlugin(g_s))

    try:
        dp_bottle_run(app, host=host, port=port, interval=1)
    finally:
        app.close()
        shutil.rmtree(app_dir, ignore_errors=True)
        log.info("Shutting down server")

    # start_server(app)


# This is based on bottle.run, with simplifications for things we don't need,
# or don't yet support, and fixes to enable our features.
def dp_bottle_run(
    app,
    *,
    host: str = "127.0.0.1",
    port: t.Optional[int] = None,
    interval=1,
    quiet=False,
    plugins=None,
    debug=None,
    config=None,
    **kargs,
):
    """Start a server instance. This method blocks until the server terminates.

    :param app: WSGI application or target string supported by
           :func:`load_app`. (default: :func:`default_app`)
    :param host: Server address to bind to. Pass ``0.0.0.0`` to listens on
           all interfaces including the external one. (default: 127.0.0.1)
    :param port: Server port to bind to. Values below 1024 require root
           privileges. (default: automatic)
    :param interval: Auto-reloader interval in seconds (default: 1)
    :param quiet: Suppress output to stdout and stderr? (default: False)
    :param options: Options passed to the server adapter.
    """
    if debug is not None:
        bt._debug(debug)
    if not callable(app):
        raise ValueError(f"Application is not callable: {app!r}")

    for plugin in plugins or []:
        if isinstance(plugin, str):
            plugin = bt.load(plugin)
        app.install(plugin)

    if config:
        app.config.update(config)

    server_starter = CherootServerStarter(app, host=host, port=port, preferred_port=8080, **kargs)
    server_starter.quiet = server_starter.quiet or quiet

    server_starter.acquire_port()
    if not server_starter.quiet:
        bt._stderr(f"Bottle v{bt.__version__} server starting up (using {server_starter.__class__.__name__})...")
        bt._stderr(f"App running on {server_starter.get_url()}")
        bt._stderr("Hit Ctrl-C to quit.\n")

    try:
        server_starter.run()
    except KeyboardInterrupt:
        pass


MAX_ACQUIRE_PORT_ATTEMPTS = 1000


# This class is similar to bottle's ServerAdapter abstraction, but with our own
# needs:
# - automatic port numbering
class CherootServerStarter:
    quiet = False

    def __init__(
        self,
        handler,
        host: str = "127.0.0.1",
        port: t.Optional[int] = None,
        preferred_port: t.Optional[int] = None,
        **options,
    ):
        """
        Pass port to specify an exact port, or None for automatic
        Pass preferred_port to specify a port that you prefer, but accept others.
        """

        self.handler = handler
        self.options = options
        # force IPv4 for localhost
        # self.host = "127.0.0.1" if host.strip().lower() == "localhost" else host
        self.host = host.strip().lower()
        self.port = port
        self.preferred_port = preferred_port

    def _make_server(self, port: int):
        options = self.options.copy()
        options["bind_addr"] = (self.host, port)
        options["wsgi_app"] = self.handler
        certfile = options.pop("certfile", None)
        keyfile = options.pop("keyfile", None)
        chainfile = options.pop("chainfile", None)
        server = cheroot.wsgi.Server(**options)
        if certfile and keyfile:
            server.ssl_adapter = cheroot.ssl.builtin.BuiltinSSLAdapter(certfile, keyfile, chainfile)
        server.prepare()  # This will raise an error on failure to bind port
        self.host = server.bind_addr[0]
        self.port = server.bind_addr[1]
        return server

    def get_url(self) -> str:
        if self.host.startswith("unix:"):
            return self.host
        elif ":" in self.host:  # IPv6
            return f"http://[{self.host}]:{self.port}"
        else:
            return f"http://{self.host}:{self.port}"

    def acquire_port(self):
        """
        Bind to the requested or an automatic port. Raises an exception if not possible.
        """
        server = None
        if self.port is None:
            if self.preferred_port is None:
                # Fully automatic, any port will do.
                desired_port = 0
                server = self._make_server(desired_port)
            else:
                # Automatic, starting from preferred_port
                desired_port = self.preferred_port
                # Start with desired_port, or next available if it is taken
                for i in range(0, MAX_ACQUIRE_PORT_ATTEMPTS):
                    try:
                        server = self._make_server(desired_port)
                    except OSError:
                        desired_port += 1
                    else:
                        break
                if server is None:
                    raise
        else:
            server = self._make_server(self.port)

        self.server = server

    def run(self):  # pragma: no cover
        try:
            self.server.serve()
        finally:
            self.server.stop()
