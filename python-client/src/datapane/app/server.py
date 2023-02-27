"""
Basic app server implementation, using,
- chroot as the web server
- bottle as a WSGI micro-framework
- custom json-rpc dispatcher
"""
from __future__ import annotations

import atexit
import os
import sys
import tempfile
import threading
import typing as t
from contextlib import suppress
from getpass import getpass
from pathlib import Path

import cheroot.server
import cheroot.ssl.builtin
import cheroot.wsgi
import importlib_resources as ir

import datapane._vendor.bottle as bt
from datapane.blocks import Controls
from datapane.client import log
from datapane.client.analytics import capture
from datapane.common.dp_types import SECS_1_HOUR, SIZE_1_MB
from datapane.common.utils import guess_type
from datapane.ipython.environment import get_environment
from datapane.processors.processors import ExportBaseHTMLOnly
from datapane.view import Blocks, BlocksT

try:
    import ipywidgets
except ImportError:
    ipywidgets = None

from .json_rpc import app_rpc_call
from .plugins import DPBottlePlugin
from .runtime import FunctionRef, GlobalState, get_session_state

# globally set the max request size to 100 MB
bt.BaseRequest.MEMFILE_MAX = int(os.getenv("MAX_REQUEST_BODY", 100 * SIZE_1_MB))


def create_bottle_app(debug: bool) -> bt.Bottle:
    # Create the app and all nested routes
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

    bt.debug(debug)
    if debug:
        # enable serving the web-components assets directly from py app server
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


# See tests/client/test_server.py for important info on testing this code.
def _build_app(entry: Blocks, *, debug: bool = False, embed_mode: bool = False) -> bt.Bottle:
    # setup GlobalState
    app_dir = Path(tempfile.mkdtemp(prefix="dp-"))
    assets_dir = app_dir / "assets"
    assets_dir.mkdir(parents=True)

    # hardcode the main app entry
    entry_f = lambda params: entry  # noqa: E731
    cache = True
    main_entry = FunctionRef(f=entry_f, controls=Controls.empty(), f_id="app.main", cache=cache)
    g_s = GlobalState(app_dir, main_entry)

    # create app and add routes
    app = create_bottle_app(debug)
    app.route("/app-rpc-call/", ["POST"], lambda: app_rpc_call(g_s))
    app.route("/assets/<filename>", ["GET"], lambda filename: serve_file(g_s, filename))
    app.route("/control/reset/", ["POST"], lambda: None)

    # start the server
    app.config.update({})
    app.install(DPBottlePlugin(g_s, embed_mode))

    if debug is not None:
        bt._debug(debug)

    return app


def serve_app(
    entry: BlocksT,
    *,
    port: t.Optional[int] = None,
    host: t.Optional[str] = None,
    debug: bool = False,
    ui: t.Optional[str] = None,
    public: bool = False,
    embed_mode: bool = False,
) -> None:
    """
    Main app serve entrypoint.

    Args:
        port: Select a specific port, otherwise one will be chosen automatically.
        host: Specify a specific host.
        debug: Enable debug mode.
        ui: Select a specific UI to use (`console` or `ipywidgets`).
        public: Expose the app to the Internet with ngrok (requires auth_token).
        embed_mode: Allows embedding in some third-party products by disabling security policies which will not work in an iframe.
    """
    wrapped_entry = Blocks.wrap_blocks(entry)
    if not wrapped_entry.has_compute:
        log.warning("Running serve_app on a static report - do you want to use save_report or upload_report instead?")

    app = _build_app(wrapped_entry, debug=debug, embed_mode=embed_mode)
    capture("App Server Started")

    if port is None:
        if _port := os.environ.get("PORT"):
            port = int(_port)

            # when the port is provided from the environment, it likely means
            # we're running in a hosted environment.
            # Bind to all interfaces so the proxy can route to us.
            if host is None:
                host = "0.0.0.0"
    if host is None:
        host = "127.0.0.1"

    server = CherootServer(app, host=host, port=port, preferred_port=8080, quiet=False)
    ui_cls: t.Type[ControllerUI]
    if ui is None:
        ui_cls = _choose_ui_class()
    else:
        if ui not in CONTROLLER_UIS:
            raise ValueError(f"UI choice '{ui}' is not a known option. Choose from: {', '.join(CONTROLLER_UIS.keys())}")
        ui_cls = CONTROLLER_UIS[ui]
    controller = ServerController(server, cleanups=[app.close], ui_cls=ui_cls, public=public)
    controller.go()


MAX_ACQUIRE_PORT_ATTEMPTS = 1000


def _choose_ui_class() -> t.Type[ControllerUI]:
    env = get_environment()
    if env.is_notebook_environment:
        if env.supports_ipywidgets:
            if ipywidgets is not None:
                return IPyWidgetsControllerUI
            else:
                print(
                    "Please install Jupyter Widgets for an improved experienced with apps in Notebook environments: "
                    + "https://ipywidgets.readthedocs.io/en/latest/user_install.html",
                    file=sys.stderr,
                )
                return FallbackNotebookControllerUI
        else:
            print(
                "You can run this notebook in Jupyter Lab or Jupyter Notebook for an improved experience.\n",
                file=sys.stderr,
            )
            return FallbackNotebookControllerUI

    else:
        return ConsoleControllerUI


# Server/controller/UI classes:

# CherootServer
# -------------
#
# This class is similar to bottle's ServerAdapter abstraction, but with our own
# needs, specifically:
#
# - automatic port numbering
# - communicates with a controller to display messages

# Internally it wraps the `cheroot.wsgi.Server` to provide all HTTP functionality


# ServerController
# ----------------

# Responsible for starting and stopping the server. Connects with both
# CherootServer and the UI class

# ControllerUI
# ------------
#
# Abstract, has implementations for console, ipywidgets and other notebook fallbacks
#
# Responsible for displaying messages to the user, and "Stop server" controls.
# Communicates with ServerController.


class CherootHTTPRequest(cheroot.server.HTTPRequest):
    def ensure_headers_sent(self, *args, **kwargs):
        try:
            super().ensure_headers_sent(*args, **kwargs)
        except OSError:
            # We're at a low enough level to know that OSError means the socket
            # closed, likely from a timeout.
            # bail out silently, to let Cheroot handle response cleanup correctly.
            # This also keeps the messy traceback from showing.
            pass


class CherootHTTPConnection(cheroot.server.HTTPConnection):
    RequestHandlerClass = CherootHTTPRequest


class CherootServer:
    quiet = False

    def __init__(
        self,
        handler: t.Callable,
        host: str = "127.0.0.1",
        port: t.Optional[int] = None,
        preferred_port: t.Optional[int] = None,
        quiet: bool = False,
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
        self.quiet = quiet
        self.server: cheroot.wsgi.Server | None = None

    def _make_server(self, port: int) -> None:
        options = self.options.copy()
        options["bind_addr"] = (self.host, port)
        options["wsgi_app"] = self.handler
        certfile = options.pop("certfile", None)
        keyfile = options.pop("keyfile", None)
        chainfile = options.pop("chainfile", None)
        server = cheroot.wsgi.Server(**options)
        server.ConnectionClass = CherootHTTPConnection
        if certfile and keyfile:
            server.ssl_adapter = cheroot.ssl.builtin.BuiltinSSLAdapter(certfile, keyfile, chainfile)
        server.prepare()  # This will raise an error on failure to bind port
        self.server = server
        # Having successfully acquired a port, copy it back to self.
        self.host = server.bind_addr[0]
        self.port = server.bind_addr[1]

    @property
    def url(self) -> str:
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
        if self.port is None:
            if self.preferred_port is None:
                # Fully automatic, any port will do.
                desired_port = 0
                self._make_server(desired_port)
            else:
                # Automatic, starting from preferred_port
                desired_port = self.preferred_port
                # Start with desired_port, or next available if it is taken
                for i in range(0, MAX_ACQUIRE_PORT_ATTEMPTS):
                    try:
                        self._make_server(desired_port)
                    except OSError:
                        desired_port += 1
                    else:
                        break
                if self.server is None:
                    # None of the attempts succeeded
                    raise
        else:
            self._make_server(self.port)

    def serve(self):  # pragma: no cover
        try:
            self.server.serve()
        finally:
            self.server.stop()

    def stop(self):
        self.server.stop()


class ControllerUI:
    server_needs_background_thread: bool = False

    def __init__(self, controller: ServerController) -> None:
        self.controller = controller

    def display(self):
        """
        Display the UI
        """
        raise NotImplementedError()

    def show_message(self, value: str):
        """
        Print a message onto the UI
        """
        raise NotImplementedError()


class ServerController:
    def __init__(
        self, server: CherootServer, *, cleanups: list[t.Callable] = None, ui_cls: t.Type[ControllerUI], public: bool
    ) -> None:
        self.server: CherootServer = server
        self.cleanups: list[t.Callable] = cleanups or []
        self.thread: threading.Thread = None
        self.ui: ControllerUI = ui_cls(self)
        self.public = public

    def go(self):
        self.server.acquire_port()
        if self.public:
            self.start_ngrok()

        self.ui.display()

        if self.ui.server_needs_background_thread:
            self.run_server_in_thread()
        else:
            self.run_server()

    def start_ngrok(self):
        from pyngrok import ngrok

        current_config = {}
        config_path = ngrok.conf.get_default().config_path or ngrok.conf.DEFAULT_NGROK_CONFIG_PATH

        if config_path:
            with suppress(FileNotFoundError):
                current_config = ngrok.installer.get_ngrok_config(config_path, use_cache=False)

        if current_config.get("authtoken", None):
            ngrok_auth_token = current_config.get("authtoken")
        else:
            ngrok_auth_token = getpass("Enter ngrok auth token (see https://ngrok.com): ")

        ngrok.set_auth_token(ngrok_auth_token)
        http_tunnel = ngrok.connect(self.server.port, bind_tls=True)
        self.ui.show_message(f"Public URL: {http_tunnel.public_url}\n")
        self.cleanups.append(ngrok.kill)

    def run_server(self):
        try:
            self.server.serve()
        except KeyboardInterrupt:
            pass
        finally:
            self.do_cleanups()

    def run_server_in_thread(self):
        assert self.thread is None
        thread = threading.Thread(target=self.server.serve, daemon=True)
        thread.start()
        self.thread = thread
        # To cover the case of non-clean shutdown:
        atexit.register(self.do_cleanups)

    def stop_background_server(self):
        # This is only used for threaded mode
        self.server.stop()
        if self.thread is not None:
            self.thread.join()
        self.do_cleanups()
        atexit.unregister(self.do_cleanups)

    def do_cleanups(self):
        for cleanup in self.cleanups:
            cleanup()

    @property
    def server_url(self) -> str:
        return self.server.url


class ConsoleControllerUI(ControllerUI):
    server_needs_background_thread = False

    def display(self):
        self.show_message(f"App running on {self.controller.server_url}/\n")
        self.show_message("Hit Ctrl-C to quit.\n")

    def show_message(self, value: str):
        print(value, file=sys.stderr, end="")


class FallbackNotebookControllerUI(ControllerUI):
    server_needs_background_thread = False

    def display(self):
        from IPython.display import HTML, display

        server_url = self.controller.server_url
        display(
            HTML(
                f'<p>Your app is running on: <a href="{server_url}">{server_url}</a></p>'
                + "<p>Use notebook ⏹ or 'Stop/Interrupt' button to halt.</p>"
            )
        )

    def show_message(self, value: str):
        # Autolink URLs by treating as Markdown
        from IPython.display import Markdown, display

        display(Markdown(value))


if ipywidgets is not None:

    class WarningWidget(ipywidgets.VBox):
        """
        Container widget that shows a fallback message for the case where Jupyter Widgets is not installed.
        """

        def __init__(self, child, html_message):
            super().__init__(children=[child])
            self.html_message = html_message

        def _repr_html_(self):
            return self.html_message


class IPyWidgetsControllerUI(ControllerUI):
    server_needs_background_thread = True

    def __init__(self, controller: ServerController) -> None:
        super().__init__(controller)

        self.button = ipywidgets.Button(description="Stop app server", icon="stop")
        self.output = ipywidgets.Output()

        def on_button_clicked(b):
            self.show_message("Stopping server...")
            self.controller.stop_background_server()
            self.show_message("stopped.\n")
            self.show_message("Re-run cell to run server again.\n")
            self.button.disabled = True
            self.button.description = "Stopped"

        self.button.on_click(on_button_clicked)

    def show_message(self, value: str):
        self.output.append_stdout(value)

    def display(self):
        from IPython.display import display

        server_url = self.controller.server_url
        display(
            WarningWidget(
                ipywidgets.VBox([self.button, self.output]),
                (
                    "<ul>"
                    + f'  <li>Your app is running on: <a href="{server_url}">{server_url}</a></li>'
                    + "   <li>You're seeing this message because 'Jupyer Widgets' is not installed in your Jupyter notebook/lab environment. "
                    + "    so the UI for controlling the app server is not visible. See "
                    + '    <a href="https://ipywidgets.readthedocs.io/en/latest/user_install.html">Jupyter Widgets Installation instructions</a></li>'
                    + '  <li>Use <code>dp.serve_app(ui="console")</code> to use the console UI instead.</li>'
                    + "</ul>"
                ),
            )
        )
        self.show_message(f"App running on {server_url}/\n")


CONTROLLER_UIS = {
    "console": ConsoleControllerUI,
    "ipywidgets": IPyWidgetsControllerUI,
}
