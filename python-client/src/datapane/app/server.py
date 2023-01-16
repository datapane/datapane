"""
Basic app server implementation, using,
- chroot as the web server
- bottle as a WSGI micro-framework
- custom json-rpc dispatcher
"""
from __future__ import annotations

import atexit
import inspect
import os
import shutil
import sys
import tempfile
import threading
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
from datapane.ipython.environment import get_environment
from datapane.processors.processors import ExportBaseHTMLOnly
from datapane.view import View

try:
    import ipywidgets
except ImportError:
    ipywidgets = None

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


# See tests/client/test_server.py for important info on testing this code.


def serve(
    entry: t.Union[View, t.Callable[[], View]],
    port: t.Optional[int] = None,
    host: str = "127.0.0.1",
    debug: bool = False,
    ui: str = None,
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

    def app_cleanup():
        shutil.rmtree(app_dir, ignore_errors=True)
        app.close()
        log.info("Shutting down server")

    if debug is not None:
        bt._debug(debug)

    server = CherootServer(app, host=host, port=port, preferred_port=8080, quiet=False)
    ui_cls: t.Type[ControllerUI]
    if ui is None:
        ui_cls = _choose_ui_class()
    else:
        if ui not in CONTROLLER_UIS:
            raise ValueError(f"UI choice '{ui}' is not a known option. Choose from: {', '.join(CONTROLLER_UIS.keys())}")
        ui_cls = CONTROLLER_UIS[ui]
    controller = ServerController(server, cleanup=app_cleanup, ui_cls=ui_cls)
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
    def __init__(self, server: CherootServer, *, cleanup: t.Callable, ui_cls: t.Type[ControllerUI]) -> None:
        self.server: CherootServer = server
        self.cleanup = cleanup
        self.thread: threading.Thread = None
        self.ui: ControllerUI = ui_cls(self)

    def go(self):
        self.server.acquire_port()
        self.ui.display()
        if self.ui.server_needs_background_thread:
            self.run_server_in_thread()
        else:
            self.run_server()

    def run_server(self):
        try:
            self.server.serve()
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

    def run_server_in_thread(self):
        assert self.thread is None
        thread = threading.Thread(target=self.server.serve, daemon=True)
        thread.start()
        self.thread = thread
        # To cover the case of non-clean shutdown:
        atexit.register(self.cleanup)

    def stop_background_server(self):
        # This is only used for threaded mode
        self.server.stop()
        if self.thread is not None:
            self.thread.join()
        self.cleanup()
        atexit.unregister(self.cleanup)

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
        # we don't have a proper updatable display, but it's better to print somewhere than nowhere
        print(value, file=sys.stdout, end="")


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
                    + '  <li>Use <code>dp.serve(ui="console")</code> to use the console UI instead.</li>'
                    + "</ul>"
                ),
            )
        )
        self.show_message(f"App running on {server_url}/\n")


CONTROLLER_UIS = {
    "console": ConsoleControllerUI,
    "ipywidgets": IPyWidgetsControllerUI,
}
