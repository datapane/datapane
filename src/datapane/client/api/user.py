import typing as t

import requests
from furl import furl

from datapane import __version__

from .. import config as c
from ..utils import success_msg
from .common import _process_res


def login(
    token: str, server: str = c.DEFAULT_SERVER, env: str = c.DEFAULT_ENV, cli_login: bool = True
) -> None:
    """Login to datapane server, storing the token under env for future use"""
    config = c.Config(server=server, token=token)
    ping(config=config, cli_login=cli_login)

    # update config with valid values
    with c.update_config(env) as x:
        x["server"] = server
        x["token"] = token


def logout(env: str = c.DEFAULT_ENV) -> None:
    with c.update_config(env) as x:
        server = x["server"]
        x["server"] = c.DEFAULT_SERVER
        x["token"] = c.DEFAULT_TOKEN
    success_msg(f"Logged out from {server}")


def ping(config: t.Optional[c.Config] = None, cli_login: bool = False) -> None:
    # hardcode ping check as used for login/logout logic independent of main API requests
    config = config or c.check_get_config()
    endpoint = "/api/settings/details/"
    f = furl(path=endpoint, origin=config.server)
    headers = dict(Authorization=f"Token {config.token}", Datapane_API_Version=__version__)
    r = requests.get(str(f), headers=headers, params=dict(cli_login=cli_login))

    res = _process_res(r)
    success_msg(f"Connected successfully to {config.server} as {res.username}")
