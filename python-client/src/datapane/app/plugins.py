"""Bottle plugins
TODO - do we just inline this where needed?
NOTE - basic plugin code vendored from Canister (https://github.com/dagnelies/canister - MIT License)

Canister is a simple plugin for bottle, providing:
- formatted logs
- url and form params unpacking
- sessions (server side) based on a `session_id` cookie
- authentication through basic auth or bearer token (OAuth2)
- CORS for cross-domain REST APIs

Changes Canister -> DPBottle
Removed
- Logging
- Global auth (both Basic and JWT)
  - instead a hardcoded "anonymous" user
- url / form param unpacking - unnecessary, prefer explicit usage
Added
- Typing and modern Python 3.7+ constructs
- General algorithm changes and improvements
"""
import math
import secrets
import threading
import time
import typing as t
from collections import UserDict
from contextlib import suppress
from functools import wraps

import datapane._vendor.bottle as bt
from datapane.client import log
from datapane.client.analytics import capture
from datapane.common.dp_types import SECS_1_HOUR, SECS_1_WEEK

from .runtime import GlobalState, SessionState

K = t.TypeVar("K")
V = t.TypeVar("V")

COOKIE_NAME = "dp_session_id"


class TimedDict(UserDict, t.Generic[K, V]):
    data: t.Dict[K, t.Tuple[float, V]]

    def __getitem__(self, key: K) -> V:
        # get the value and update the access time in the dict
        (_, val) = self.data[key]
        self.data[key] = (time.time(), val)
        return val

    def __setitem__(self, key: K, val: V):
        self.data[key] = (time.time(), val)

    def values(self):
        for _, val in self.data.values():
            yield val

    def items(self):
        for (k, (_, val)) in self.data.items():
            yield (k, val)

    def prune(self, age: float) -> int:
        # drop all values older than age and return the count
        now = time.time()
        initial_len = len(self.data)
        self.data = {k: (access_t, val) for (k, (access_t, val)) in self.data.items() if now - access_t < age}
        return initial_len - len(self.data)


class SessionCache(t.Generic[V]):
    """A thread safe session cache with a cleanup thread"""

    def __init__(self, timeout: int = SECS_1_HOUR):
        self._lock = threading.Lock()
        self._cache: TimedDict[str, V] = TimedDict()
        self.keep_pruning = True

        if timeout <= 0:
            log.warning("Sessions kept indefinitely! (session timeout is <= 0s)")
            return

        interval = int(math.sqrt(timeout))
        log.info(f"Session timeout is {timeout}s, checking for expired sessions every {interval}s")

        def prune() -> t.NoReturn:
            # NOTE - do we set this to falso on clear, or just keep always running when server is live?
            while self.keep_pruning:
                time.sleep(interval)
                with self._lock:
                    n = self._cache.prune(timeout)
                    log.debug(f"{n} expired sessions pruned")

        # daemon thread shuts down without cleanup - ok for now
        threading.Thread(name="SessionCleaner", target=prune, daemon=True).start()

    def __contains__(self, s_id: str) -> bool:
        return s_id in self._cache

    def get(self, s_id: str) -> t.Optional[V]:
        with self._lock:
            return self._cache.get(s_id, None)

    def set(self, s_id: str, data: V) -> None:
        assert s_id
        with self._lock:
            self._cache[s_id] = data

    def create(self, data: V) -> str:
        s_id: str = secrets.token_urlsafe(18)
        with self._lock:
            self._cache[s_id] = data
        return s_id

    def delete(self, s_id: str) -> None:
        with self._lock, suppress(KeyError):
            del self._cache[s_id]

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            # self.keep_pruning = False


class DPBottlePlugin:
    """Specialised to the App Session object"""

    name = "dp_bottle"
    api = 2

    # attributes
    app: bt.Bottle
    sessions: SessionCache[SessionState]
    session_secret: str
    cors: t.Optional[str]
    g_s: GlobalState
    embed_mode: bool

    def __init__(self, g_s: GlobalState, embed_mode: bool):
        self.g_s = g_s
        self.embed_mode = embed_mode

    def setup(self, app: bt.Bottle):
        # if 'canister' not in app.config:
        #    raise Exception('Canister requires a configuration file. Please refer to the docs.')

        # log config
        log.debug("Initializing Bottle and custom plugin")
        log.debug(f"bottle version: {bt.__version__}")
        log.debug("------------------------------------------")
        for k, v in app.config.items():
            log.debug(f"{k:<30} = {v}")
        log.debug("------------------------------------------")

        app.log = log
        self.app = app

        timeout = int(app.config.get("dp_bottle.session_timeout", SECS_1_HOUR))
        self.sessions = SessionCache(timeout=timeout)
        self.session_secret = secrets.token_urlsafe(30)

        self.cors: str = app.config.get("dp_bottle.CORS", "").lower()
        if self.cors in ("", "false"):
            self.cors = None

    def _create_session(self, res: bt.LocalResponse) -> SessionState:
        """Create a new session and return in the response"""
        session = SessionState(user="anonymous")
        session.add_entry(self.g_s.main)

        s_id = session.s_id
        self.sessions.set(s_id, session)
        # NOTE - do we want a timelimit on cookie, or just tie to browser session?
        # if embed_mode is True (default: False), we disable samesite cookies so sessions work in iframes
        res.set_cookie(
            COOKIE_NAME,
            s_id,
            secret=self.session_secret,
            path="/",
            maxage=SECS_1_WEEK,
            secure=self.embed_mode,
            httponly=True,
            samesite="none" if self.embed_mode else "lax",
        )
        log.info(f"Session created: {s_id}")
        return session

    def apply(self, callback: t.Callable, route: bt.Route):
        @wraps(callback)
        def wrapper(*args, **kwargs):

            # grab the session threadlocal and attach to request
            # global session
            req = bt.request
            res = bt.response
            start = time.time()

            # thread name = <ip>-....
            threading.current_thread().name = f"{req.remote_addr}-..."
            log.info(f"{req.method} {req.url}")

            # session handling
            prev_s_id: t.Optional[str] = req.get_cookie(COOKIE_NAME, secret=self.session_secret)
            prev_session = self.sessions.get(prev_s_id)

            if route.rule == "/control/reset/" and route.method == "POST":
                # reset the session
                log.info(f"Resetting session for {prev_s_id=}")
                # remove the user session, if exists, and create a new one
                if prev_session is not None:
                    self.sessions.delete(prev_s_id)
                _ = self._create_session(res)
                res.status = 204
                return None
            elif prev_session is not None:
                session = t.cast(SessionState, prev_session)
                s_id = t.cast(str, prev_s_id)
                log.info(f"Existing session found for {s_id=}")
            elif route.rule == "/":  # and no prev session
                session = self._create_session(res)
                capture("App Session Created")
            else:
                # no valid previous session and calling a route other than "/"
                res.headers["Datapane-Error"] = "unknown-session"
                raise bt.HTTPError(400, "Unknown session", **res.headers)

            # thread name = <ip>-<session_id[0:6]>
            threading.current_thread().name = f"{req.remote_addr}-{session.s_id[0:6]}"

            # NOTE - user handling was here...
            # session.session.user = user = "anonymous"

            # store session directly in the threadlocal request
            _session_hash = hash(session)
            req.session = session

            # call the route dispatcher
            try:
                result = callback(*args, **kwargs)
            except OSError as e:
                # Catch OSError, as `socket` will raise OSError or TimeoutError depending on
                # where it is.
                #
                # occurs when 2 conditions are met:
                #   - the client has sent part of the body, but took too long to finish
                #   - we are currently trying to read the body
                #
                # This can be replicated using 'gnutls-cli' or 'telnet' to:
                # 1. connect to the server
                # 2. send a POST request with headers and the **start** of the body
                # 3. wait for the server to timeout the connection (~10 seconds from connection)
                #
                # In these cases, we don't need to provide a response

                # TimeoutError could happen in the handler.
                # Do a sanity check to make sure it's actually a socket error
                try:
                    _ = req.body
                except OSError:
                    # we were right, bail out
                    log.warning("dropping timed-out request")
                    return
                else:
                    raise e from e

            # update the session, if needed
            if _session_hash != hash(session):
                self.sessions.set(session.s_id, session)

            # Cors handling
            if self.cors:
                res.headers["Access-Control-Allow-Origin"] = self.cors

            # request timing
            elapsed = time.time() - start
            if elapsed > 1:
                log.warning(f"Response: {res.status_code} ({1000*elapsed:.2f}ms - Slow!)")
            else:
                log.info(f"Response: {res.status_code} ({1000 * elapsed:.2f}ms)")
            return result

        return wrapper

    def close(self):
        log.debug("Closing DPBottle Plugin")
        self.sessions.clear()
        self.g_s.clear()
