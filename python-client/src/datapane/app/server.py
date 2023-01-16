"""
Basic app server implementation, using,
- chroot as the web server
- bottle as a WSGI micro-framework
- custom json-rpc dispatcher
"""
import inspect
import os
import shutil
import sys
import tempfile
import time
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


class DPCherootServer(bt.ServerAdapter):
    # Customised CherootServer to allow us to use port 0 and still print
    # the port name
    def prepare(self, handler):

        from cheroot import wsgi
        from cheroot.ssl import builtin

        self.options["bind_addr"] = (self.host, self.port)
        self.options["wsgi_app"] = handler
        certfile = self.options.pop("certfile", None)
        keyfile = self.options.pop("keyfile", None)
        chainfile = self.options.pop("chainfile", None)
        server = wsgi.Server(**self.options)
        if certfile and keyfile:
            server.ssl_adapter = builtin.BuiltinSSLAdapter(certfile, keyfile, chainfile)

        # Correct the displayed port:
        server.prepare()
        self.host = server.bind_addr[0]
        self.port = server.bind_addr[1]

        self.server = server

    def run(self, handler):
        try:
            self.server.serve()
        finally:
            self.server.stop()


def serve(
    entry: t.Union[View, t.Callable[[], View]], port: int = 0, host: str = "localhost", debug: bool = False
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
        if debug:
            # TODO - add the CDN route here too
            display_msg(f"Server started at {host}:{port}")
            bt.run(app, server="wsgiref", host=host, port=port, debug=True)
        else:
            dp_bottle_run(app, server=DPCherootServer, host=host, port=port, interval=1, reloader=False)
    except KeyboardInterrupt:
        pass
    finally:
        app.close()
        shutil.rmtree(app_dir, ignore_errors=True)
        log.info("Shutting down server")

    # start_server(app)


# This is mostly copied from bottle.run, with a few simplifications for things
# we don't need, and fixes to enable running on unknown ports
def dp_bottle_run(
    app,
    *,
    server,
    host="127.0.0.1",
    port=8080,
    interval=1,
    reloader=False,
    quiet=False,
    plugins=None,
    debug=None,
    config=None,
    **kargs,
):
    """Start a server instance. This method blocks until the server terminates.

    :param app: WSGI application or target string supported by
           :func:`load_app`. (default: :func:`default_app`)
    :param server: Server adapter to use. See :data:`server_names` keys
           for valid names or pass a :class:`ServerAdapter` subclass.
           (default: `wsgiref`)
    :param host: Server address to bind to. Pass ``0.0.0.0`` to listens on
           all interfaces including the external one. (default: 127.0.0.1)
    :param port: Server port to bind to. Values below 1024 require root
           privileges. (default: 8080)
    :param reloader: Start auto-reloading server? (default: False)
    :param interval: Auto-reloader interval in seconds (default: 1)
    :param quiet: Suppress output to stdout and stderr? (default: False)
    :param options: Options passed to the server adapter.
    """
    if bt.NORUN:
        return
    if reloader and not os.environ.get("BOTTLE_CHILD"):
        import subprocess

        fd, lockfile = tempfile.mkstemp(prefix="bottle.", suffix=".lock")
        environ = os.environ.copy()
        environ["BOTTLE_CHILD"] = "true"
        environ["BOTTLE_LOCKFILE"] = lockfile
        args = [sys.executable] + sys.argv
        # If a package was loaded with `python -m`, then `sys.argv` needs to be
        # restored to the original value, or imports might break. See #1336
        if getattr(sys.modules.get("__main__"), "__package__", None):
            args[1:1] = ["-m", sys.modules["__main__"].__package__]

        try:
            os.close(fd)  # We never write to this file
            while os.path.exists(lockfile):
                p = subprocess.Popen(args, env=environ)
                while p.poll() is None:
                    os.utime(lockfile, None)  # Tell child we are still alive
                    time.sleep(interval)
                if p.returncode == 3:  # Child wants to be restarted
                    continue
                sys.exit(p.returncode)
        except KeyboardInterrupt:
            pass
        finally:
            if os.path.exists(lockfile):
                os.unlink(lockfile)
        return

    try:
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

        if server in bt.server_names:
            server = bt.server_names.get(server)
        if isinstance(server, type):
            server = server(host=host, port=port, **kargs)
        if not isinstance(server, bt.ServerAdapter):
            raise ValueError(f"Unknown or unsupported server: {server!r}")

        server.quiet = server.quiet or quiet

        if reloader:
            lockfile = os.environ.get("BOTTLE_LOCKFILE")
            bgcheck = bt.FileCheckerThread(lockfile, interval)
            with bgcheck:
                server.run(app)
            if bgcheck.status == "reload":
                sys.exit(3)
        else:

            server.prepare(app)
            if not server.quiet:
                bt._stderr(f"Bottle v{bt.__version__} server starting up (using {server.__class__.__name__})...")
                if server.host.startswith("unix:"):
                    bt._stderr(f"App running on {server.host}")
                else:
                    bt._stderr("App running on http://%s:%d/" % (server.host, server.port))
                bt._stderr("Hit Ctrl-C to quit.\n")

            server.run(app)
    except KeyboardInterrupt:
        pass
    except (SystemExit, MemoryError):
        raise
    except:  # noqa:E722
        if not reloader:
            raise
        if not getattr(server, "quiet", quiet):
            bt.print_exc()
        time.sleep(interval)
        sys.exit(3)


def start_server(app, host: str = "localhost", port: int = 0, **kwargs):
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
