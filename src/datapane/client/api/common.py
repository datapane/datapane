import atexit
import os
import pprint
import shutil
import typing as t
from contextlib import contextmanager
from copy import copy
from pathlib import Path
from tempfile import mkdtemp, mkstemp
from urllib import parse as up

import requests
from munch import munchify
from packaging.version import Version
from requests import HTTPError, Response  # noqa: F401

from datapane import __version__
from datapane.client import config as c
from datapane.common import JSON, NPath, SDict
from datapane.common.utils import log, setup_logging

################################################################################
# Tmpfile handling
# We create a tmp-dir per Python execution that stores all working files,
# we attempt to delete where possible, but where not, we allow the atexit handler
# to cleanup for us on shutdown
# This tmp-dir needs to be in the cwd rather than /tmp so can be previewed in Jupyter

# Temporary directory name
tmp_dir = Path(mkdtemp(prefix="dp-tmp-", dir=".")).absolute()


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

    def __str__(self):
        return str(self.file)


@atexit.register
def cleanup_tmp():
    """Ensure we cleanup the tmp_dir on Python VM exit"""
    # log.debug(f"Removing DP tmp work dir {tmp_dir}")
    shutil.rmtree(tmp_dir, ignore_errors=True)


################################################################################
def init(
    config_env: str = "default",
    config: t.Optional[c.Config] = None,
    debug: bool = False,
    logs_stream: t.Optional[t.TextIO] = None,
):
    """Init the API - this MUST handle being called multiple times"""
    if c.get_config() is not None:
        log.debug("Already init")

    if config:
        c.set_config(config)
    else:
        config_f = c.load_from_envfile(config_env)
        log.debug(f"Loaded environment from {config_f}")

    setup_logging(verbose_mode=debug, logs_stream=logs_stream)


class IncompatibleVersionException(Exception):
    ...


def check_pip_version() -> None:
    cli_version = Version(__version__)
    url = "https://pypi.org/pypi/datapane/json"
    r = requests.get(url=url)
    r.raise_for_status()
    pip_version = Version(r.json()["info"]["version"])
    log.debug(f"CLI version {cli_version}, latest pip version {pip_version}")
    if pip_version > cli_version:
        raise IncompatibleVersionException(
            f"Your client is out-of-date (version {cli_version}) and may be causing errors, please upgrade to {pip_version}"
            f' using pip ("pip3 install --upgrade [--user] datapane")'
        )


# TODO - make generic and return a dataclass from server?
#  - we can just use Munch and proxying for now, and type later if/when needed
#  - look at using types.DynamicClassAttribute
class Resource:
    # TODO - this should probably hold a requests session object
    endpoint: str
    headers: t.Dict
    url: str

    def __init__(self, endpoint: str, config: t.Optional[c.Config] = None):
        self.endpoint = endpoint.split("/api", maxsplit=1)[-1]
        self.config = config or c.config
        self.url = up.urljoin(self.config.server, f"api{self.endpoint}")
        self.headers = dict(
            Authorization=f"Token {self.config.token}", Datapane_API_Version=__version__
        )

    def _process_res(self, r: Response) -> JSON:
        if not r.ok:
            # check if upgrade is required
            if r.status_code == 426:
                check_pip_version()
            else:
                try:
                    log.error(pprint.pformat(r.json()))
                except ValueError:
                    log.error(pprint.pformat(r.text))
        r.raise_for_status()
        r_data = r.json()
        return munchify(r_data) if isinstance(r_data, dict) else r_data

    def post(self, params: t.Dict = None, **data: JSON) -> JSON:
        params = params or dict()
        # headers = {**self.headers, **{"Content-Type": "application/json"}}
        # json_data = json.dumps(data, default=lambda x: str(x))
        r = requests.post(self.url, json=data, params=params, headers=self.headers)
        return self._process_res(r)

    def get(self, **data) -> JSON:
        r = requests.get(self.url, data, headers=self.headers)
        return self._process_res(r)

    def patch(self, **data: JSON) -> JSON:
        r = requests.patch(self.url, data, headers=self.headers)
        return self._process_res(r)

    def delete(self) -> None:
        r: Response = requests.delete(self.url, headers=self.headers)
        r.raise_for_status()

    @contextmanager
    def nest_endpoint(self, endpoint: str) -> t.ContextManager["Resource"]:
        """Returns a context manager allowing recursive nesting in endpoints"""
        a = copy(self)
        a.url = up.urljoin(a.url, endpoint)
        log.debug(f"Nesting endpoint {endpoint}")
        yield a
        log.debug(f"Unnesting endpoint {endpoint}")


def _download_file(download_url: str, fn: t.Optional[NPath] = None) -> NPath:
    """Download a file to cwd, using fn if provided, else content-disposition, else tmpfile"""
    with requests.get(download_url, stream=True) as r:
        x = r.headers.get("Content-Disposition")
        if not fn:
            if x and "filename" in x:
                # 'attachment; filename="datapane_test_test_dp_1588192318-1588192318-py3-none-any.whl"'
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


def check_login(config=None) -> SDict:
    r = Resource(endpoint="/settings/details/", config=config).get()
    log.debug(f"Connected successfully to DP Server as {r.username}")
    return t.cast(SDict, r)
