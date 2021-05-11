"""## Datapane User API

User management functions, including authentication

It's possible to authenticate within Python, however we also provide (and recommend) authenticating
via the CLI, as it's easier to script,

```
$ datapane login --token ...
$ datapane logout
```

"""

import typing as t
import uuid

import requests
from furl import furl

from datapane import __version__

from .. import config as c
from ..analytics import capture_event
from ..utils import success_msg
from .common import _process_res

__all__ = ["login", "logout"]


@capture_event("CLI Login")
def login(token: str, server: str = c.DEFAULT_SERVER, env: str = c.DEFAULT_ENV, cli_login: bool = True) -> str:
    """
    Login to the specified Datapane Server, storing the token within a config-file called `env` for future use

    Args:
        token: Token to use when logging in
        server: Datapane Server to connect to (default: Datapane Community at https://datapane.com/)
        env: The environment profile to store these login details to (default: `default`)
        cli_login: Toggle if this login is occuring via the CLI (optional)

    Returns:
        the username for the logged in user

    ..note:: Can also be ran via CLI as `"datapane login"`
    """
    old_config = c.get_config()
    session_id = old_config.session_id if token == old_config.token else uuid.uuid4().hex
    config = c.Config(server=server, token=token, session_id=session_id)

    username = ping(config=config, cli_login=cli_login)

    # update config with valid values
    with c.update_config(env) as x:
        x["server"] = server
        x["token"] = token
        x["username"] = username
        x["session_id"] = session_id

        # disable analytics(if enabled) on non datapane servers
        x["analytics"] = c.default_analytics_state(server, old_config.analytics)
    return username


def logout(env: str = c.DEFAULT_ENV) -> None:
    """
    Logout from Datapane Server, removing local credentials

    Args:
        env: Environment profile to logout from

    ..note:: Can also be ran via CLI as `"datapane logout"`
    """
    success_msg(f"Logged out from {c.config.server}")
    c.get_config_file(env=env, reset=True)
    c.init(config_env=env)


def ping(config: t.Optional[c.Config] = None, cli_login: bool = False) -> str:
    """Ping the Datapane Server to check login credentials"""
    # hardcode ping check as used for login/logout logic independent of main API requests
    config = config or c.check_get_config()
    endpoint = "/api/settings/details/"
    f = furl(path=endpoint, origin=config.server)
    headers = dict(Authorization=f"Token {config.token}", Datapane_API_Version=__version__)
    q_params = dict(cli_id=config.session_id) if cli_login else {}
    r = requests.get(str(f), headers=headers, params=q_params)
    username = _process_res(r).username

    success_msg(f"Connected successfully to {config.server} as {username}")

    return username
