"""
Boddle testing framework for mocking Bottle requests
Initiall vendored from https://github.com/keredson/boddle/blob/74413e4c5b39a37ea1694fab07b459ccd2998390/boddle.py
"""
import io
import json
import typing as t
from base64 import b64encode
from urllib.parse import urlencode, urlparse

from datapane._vendor import bottle


class boddle:
    def __init__(
        self,
        params: t.Optional[t.Union[t.Mapping, t.Sequence]] = None,
        path: t.Optional[str] = None,
        method: t.Optional[str] = None,
        headers: t.Optional[t.Dict] = None,
        json_data: t.Any = None,
        url: t.Optional[bytes] = None,
        body: t.Optional[t.Union[str, t.BinaryIO]] = None,
        query: t.Optional[t.Dict] = None,
        auth: t.Optional[t.Tuple[str, str]] = None,
        **extras,
    ):
        """
        Args:
            params: Populates request.params. Takes a dict or list of pairs. Useful for both POST and GET params
            path: The path component of the url. Populates `request.path`, which always has a preceeding /
            method: POST, GET, etc. Bottle will uppercase the value
            headers: Any HTTP headers
            json_data: Anything serialisable by `json.dumps()` and sets the content-type accordingly
            url: The full URL, protocol, domain, port, path, etc. Will be parsed until its urlparts before populating request.url
            body: The raw body of the request. Takes either a str or a file-like object. strs will be converted into file-like objects. Populated request.body
            query: Populates request.query
            auth: Tuple of (user, pass) for HTTP Basic Auth
            **extras: additional values attached to the request object
        """

        environ = {}
        self.extras = extras
        self.extra_orig = {}
        self.orig_app_reader = bottle.BaseRequest.app

        if auth is not None:
            user, password = auth
            auth_phrase = b64encode(f"{user}:{password}".encode()).decode("ascii")
            environ["HTTP_AUTHORIZATION"] = f"Basic {auth_phrase}"

        if params:
            self._set_payload(environ, urlencode(params))

        if path:
            environ["PATH_INFO"] = path.lstrip("/")

        if method:
            environ["REQUEST_METHOD"] = method

        for k, v in (headers or {}).items():
            k = k.replace("-", "_").upper()
            environ["HTTP_" + k] = v

        if json_data:
            environ["CONTENT_TYPE"] = "application/json"
            self._set_payload(environ, json.dumps(json_data))

        if body:
            if isinstance(body, str):
                body = io.BytesIO(body.encode())
            body.seek(0)
            environ["CONTENT_LENGTH"] = str(body.tell())
            environ["wsgi.input"] = body

        if url:
            o = urlparse(url)
            environ["wsgi.url_scheme"] = o.scheme
            environ["HTTP_HOST"] = o.netloc
            environ["PATH_INFO"] = o.path.lstrip(b"/")

        if query:
            environ["QUERY_STRING"] = urlencode(query)

        self.environ = environ

    def _set_payload(self, environ: t.Dict, payload: str):
        payload_b = payload.encode()
        environ["CONTENT_LENGTH"] = str(len(payload_b))
        environ["wsgi.input"] = io.BytesIO(payload_b)

    def __enter__(self):
        self.orig = bottle.request.environ
        bottle.request.environ = self.environ
        for k, v in self.extras.items():
            if hasattr(bottle.request, k):
                self.extra_orig[k] = getattr(bottle.request, k)
            setattr(bottle.request, k, v)
        setattr(bottle.BaseRequest, "app", True)

    def __exit__(self, exc_type, exc_value, traceback):
        bottle.request.environ = self.orig
        for k, v in self.extras.items():
            if k in self.extra_orig:
                setattr(bottle.request, k, self.extra_orig[k])
            else:
                try:
                    delattr(bottle.request, k)
                except AttributeError:
                    pass
        setattr(bottle.BaseRequest, "app", self.orig_app_reader)
