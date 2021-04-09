"""## Common objects

Common/shared objects and types used throughout the client API

..note:: This module is not used directly
"""
import atexit
import json
import os
import pprint
import shutil
import time
import typing as t
from contextlib import contextmanager, suppress
from copy import copy
from datetime import timedelta
from pathlib import Path
from tempfile import mkdtemp, mkstemp
from urllib import parse as up

import click
import requests
from furl import furl
from munch import munchify
from packaging.version import Version
from requests import HTTPError, Response  # noqa: F401
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from datapane import _TEST_ENV, __version__
from datapane.client import config as c
from datapane.client.utils import (
    IncompatibleVersionError,
    ReportTooLargeError,
    UnsupportedResourceError,
    failure_msg,
)
from datapane.common import JSON, MIME, NPath, guess_type
from datapane.common.utils import compress_file, log

__all__ = []

################################################################################
# Tmpfile handling
# We create a tmp-dir per Python execution that stores all working files,
# we attempt to delete where possible, but where not, we allow the atexit handler
# to cleanup for us on shutdown
# This tmp-dir needs to be in the cwd rather than /tmp so can be previewed in Jupyter
# To avoid cluttering up the user's cwd, we nest these inside a `dp-cache` intermediate dir
cache_dir = Path("dp-cache").absolute()
cache_dir.mkdir(parents=True, exist_ok=True)

# Remove any old ./dp-tmp-* dirs over 24hrs old which might not have been cleaned up due to unexpected exit
one_day_ago = time.time() - timedelta(days=1).total_seconds()
prev_tmp_dirs = (p for p in cache_dir.glob("dp-tmp-*") if p.is_dir() and p.stat().st_mtime < one_day_ago)
for p in prev_tmp_dirs:
    log.debug(f"Removing stale temp dir {p}")
    shutil.rmtree(p, ignore_errors=True)

# create new dp-tmp for this session, nested inside `dp-cache`
tmp_dir = Path(mkdtemp(prefix="dp-tmp-", dir=cache_dir)).absolute()


class DPTmpFile:
    """
    Generate a tempfile in dp temp dir
    when used as a contextmanager, deleted on removing scope
    otherwise, removed by atexit hook
    """

    def __init__(self, ext: str):
        fd, name = mkstemp(suffix=ext, prefix="dp-tmp-", dir=tmp_dir)
        os.close(fd)
        self.file = Path(name)

    def __enter__(self) -> "DPTmpFile":
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        log.debug(f"Removing {self.name}")
        if self.file.exists():
            self.file.unlink()  # (missing_ok=True)

    @property
    def name(self) -> str:
        return str(self.file)

    @property
    def full_name(self) -> str:
        return str(self.file.absolute())

    @property
    def mime(self) -> MIME:
        return guess_type(self.file)

    def __str__(self) -> str:
        return self.name


@atexit.register
def cleanup_tmp():
    """Ensure we cleanup the tmp_dir on Python VM exit"""
    # log.debug(f"Removing current session DP tmp work dir {tmp_dir}")
    shutil.rmtree(tmp_dir, ignore_errors=True)
    # try remove cache_dir if empty
    with suppress(OSError):
        cache_dir.rmdir()
        # log.debug("Removed empty dp-cache dir")


################################################################################
def check_pip_version() -> None:
    cli_version = Version(__version__)
    url = "https://pypi.org/pypi/datapane/json"
    r = requests.get(url=url)
    r.raise_for_status()
    pip_version = Version(r.json()["info"]["version"])
    log.debug(f"CLI version {cli_version}, latest pip version {pip_version}")

    if pip_version > cli_version:
        error_msg = (
            f"Your client is out-of-date (version {cli_version}) and may be causing errors, "
            + f"please upgrade to version {pip_version} - see https://docs.datapane.com/tut-getting-started#upgrading"
        )
    else:  # no newer pip - perhaps local dev?
        error_msg = f"Your client is out-of-date (version {cli_version}) with the server and may be causing errors"
    raise IncompatibleVersionError(error_msg)


def _process_res(r: Response, empty_ok: bool = False) -> JSON:
    if not r.ok:
        # check if upgrade is required
        if r.status_code == 426:
            check_pip_version()
        elif r.status_code == 401:
            failure_msg(f"Couldn't successfully connect to {c.config.server}, please check your login details")
        else:
            try:
                log.error(pprint.pformat(r.json()))
            except ValueError:
                log.error(pprint.pformat(r.text))
    r.raise_for_status()
    if empty_ok and not r.content:
        r_data = {}
    else:
        r_data = r.json()
    return munchify(r_data) if isinstance(r_data, dict) else r_data


FileList = t.Dict[str, t.List[Path]]


# TODO - make generic and return a dataclass from server?
#  - we can just use Munch and proxying for now, and type later if/when needed
#  - look at using types.DynamicClassAttribute
class Resource:
    endpoint: str
    url: str
    # keep session as classvar to share across all DP accesses - however will be
    # tied to current instance config
    session = requests.Session()
    timeout = None if _TEST_ENV else (6.10, 54)

    def __init__(self, endpoint: str):
        self.endpoint = endpoint.split("/api", maxsplit=1)[-1]
        config = c.check_get_config()
        self.url = up.urljoin(config.server, f"api{self.endpoint}")
        # check if access to the resource is allowed
        self._check_endpoint(self.url)
        self.session.headers.update(Authorization=f"Token {config.token}", Datapane_API_Version=__version__)

    def _check_endpoint(self, url: str):
        # raise exception if unavailable object is being accessed on the basic instance
        basic_endpoints = ["files", "oembed", "reports", "settings", "users"]
        url = furl(url)
        url_parts = url.path.segments
        if (
            url.host in ["datapane.com"]  # , "localhost"] - we want to access OrgSolo locally
            and url_parts[0] == "api"
            and url_parts[1] not in basic_endpoints
        ):
            raise UnsupportedResourceError(f"{url_parts[1].title()} are part of Datapane Cloud.")

    def post(self, params: t.Dict = None, **data: JSON) -> JSON:
        params = params or dict()
        r = self.session.post(self.url, json=data, params=params, timeout=self.timeout)
        return _process_res(r)

    def post_files(self, files: FileList, **data: JSON) -> JSON:
        # upload files using custom json-data protocol
        # build the fields
        file_header = {"Content-Encoding": "gzip"}

        def mk_file_fields(field_name: str, f: Path):
            # compress the file, in-place
            # TODO - disable compression where unneeded, e.g. .gz, .zip, .png, etc
            with compress_file(f) as f_gz:
                return (
                    field_name,
                    (f.name, open(f_gz, "rb"), guess_type(f), file_header),
                )

        fields = [mk_file_fields(k, x) for (k, v) in files.items() for x in v]
        fields.append(("json_data", json.dumps(data)))

        e = MultipartEncoder(fields=fields)
        extra_headers = {"Content-Type": f"{e.content_type}; dp-files=True"}
        if e.len > 25 * 1e6:  # 25 MB
            raise ReportTooLargeError(
                "Report and attachments over 25MB after compression - please reduce the size of your charts/plots"
            )
        elif e.len > 1e6:  # 1 MB
            log.debug("Using upload monitor")
            fill_char = click.style("=", fg="yellow")
            with click.progressbar(
                length=e.len,
                width=0,
                show_eta=True,
                label="Uploading files",
                fill_char=fill_char,
            ) as bar:

                def f(m: MultipartEncoderMonitor):
                    # update every 100KB
                    m.buf_bytes_read += m.bytes_read - m.prev_bytes_read
                    m.prev_bytes_read = m.bytes_read
                    if m.buf_bytes_read >= 1e5:
                        # print(f"{m.buf_bytes_read=}, {m.prev_bytes_read=}")
                        bar.update(m.buf_bytes_read)
                        m.buf_bytes_read = 0

                m = MultipartEncoderMonitor(e, callback=f)
                m.buf_bytes_read = 0
                m.prev_bytes_read = 0
                r = self.session.post(self.url, data=m, headers=extra_headers, timeout=self.timeout)
        else:
            r = self.session.post(self.url, data=e, headers=extra_headers, timeout=self.timeout)
        return _process_res(r)

    def get(self, **params) -> JSON:
        r = self.session.get(self.url, params=params, timeout=self.timeout)
        return _process_res(r)

    def patch(self, params: t.Dict = None, **data: JSON) -> JSON:
        params = params or dict()
        r = self.session.patch(self.url, json=data, params=params, timeout=self.timeout)
        return _process_res(r)

    def delete(self) -> None:
        r = self.session.delete(self.url, timeout=self.timeout)
        _process_res(r, empty_ok=True)

    @contextmanager
    def nest_endpoint(self, endpoint: str) -> t.ContextManager["Resource"]:
        """Returns a context manager allowing recursive nesting in endpoints"""
        a = copy(self)
        a.url = up.urljoin(a.url, endpoint)
        log.debug(f"Nesting endpoint {endpoint}")
        yield a
        log.debug(f"Unnesting endpoint {endpoint}")


def do_download_file(download_url: t.Union[str, furl], fn: t.Optional[NPath] = None) -> NPath:
    """Download a file to `cwd`, using `fn` if provided, else Content-Disposition, else tmpfile"""
    if isinstance(download_url, str):
        download_url: furl = furl(download_url)

    if download_url.host is None:
        # assume the url is relative to the dp server
        download_url.origin = c.config.server

    with requests.get(str(download_url.url), stream=True) as r:
        r.raise_for_status()
        x = r.headers.get("Content-Disposition")
        if not fn:
            if x and "filename" in x:
                # 'attachment; filename="datapane-test_test_dp_1588192318-1588192318-py3-none-any.whl"'
                y = x.split("filename=", maxsplit=1)[1].strip('"')
                fn = str(Path.cwd() / y)
            else:
                f, fn = mkstemp()
                os.close(f)
        with open(fn, "wb") as f:
            # shutil.copyfileobj(r.raw, f)
            for chunk in r.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                f.write(chunk)
    return fn
