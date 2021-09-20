"""## Datapane User API

User management functions, including authentication

It's possible to authenticate within Python, however we also provide (and recommend) authenticating
via the CLI, as it's easier to script,

```
$ datapane login --token ...
$ datapane logout
```

"""

import runpy
import shutil
import sys
import time
import typing as t
import webbrowser

import click_spinner
import importlib_resources as ir
import requests
from furl import furl

from datapane import __version__

from .. import config as c
from ..analytics import capture_event
from ..utils import display_msg, success_msg
from .common import _process_res

__all__ = ["login", "logout", "ping", "signup", "hello"]


@capture_event("CLI Login")
def login(
    token: t.Optional[str], server: str = c.DEFAULT_SERVER, env: str = c.DEFAULT_ENV, cli_login: bool = True
) -> str:
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

    config = c.Config(server=server)

    if token is None:
        token = token_connect("/accounts/login/", action="login", server=config.server)

    config.token = token
    username = ping(config=config, cli_login=cli_login)

    # update config with valid values
    config.username = username
    config.save(env=env)
    c.init(config=config)
    return config.username


def logout(env: str = c.DEFAULT_ENV) -> None:
    """
    Logout from Datapane Server, removing local credentials

    Args:
        env: Environment profile to logout from

    ..note:: Can also be ran via CLI as `"datapane logout"`
    """
    success_msg(f"Logged out from {c.config.server}")
    # TODO - remove this assert
    assert c.config._env == env
    c.config.remove()
    c.set_config(None)  # ??
    c.init(config_env=c.DEFAULT_ENV)


def ping(config: t.Optional[c.Config] = None, cli_login: bool = False, verbose: bool = True) -> str:
    """Ping the Datapane Server to check login credentials"""
    # hardcode ping check as used for login/logout logic independent of main API requests
    config = config or c.check_get_config()
    endpoint = "/api/settings/details/"
    f = furl(path=endpoint, origin=config.server)
    headers = {"Authorization": f"Token {config.token}", "Datapane-API-Version": __version__}
    q_params = dict(cli_id=config.session_id) if cli_login else {}
    r = requests.get(str(f), headers=headers, params=q_params)
    username = _process_res(r).username

    if verbose:
        success_msg(f"Connected successfully to {config.server} as {username}")

    return username


def signup(config: t.Optional[c.Config] = None):
    config = config or c.get_config()
    token = token_connect("/accounts/signup/", action="signup", server=config.server)
    login(token, server=config.server)


def hello():
    display_msg(
        "Creating and running `./hello.py` - running this code generates a sample Datapane report. You can edit the script and run it again to change the generated report\n"
    )

    hello_path = ir.files("datapane.resources.templates.report_py") / "hello.py"
    shutil.copyfile(hello_path, "./hello.py")
    runpy.run_path(hello_path, run_name="__datapane__")

    success_msg("Report generated, opening in your browser")


def token_connect(open_url: str, action: str, server: str):
    """
    Create a signup token, and prompt the user to login/signup while polling for completion.
    Then log the user into the CLI with the retrieved API token
    """

    def create_token(s: requests.Session) -> str:
        create_endpoint = furl(path="/api/api-signup-tokens/", origin=server).url
        r = s.post(create_endpoint)
        return _process_res(r).key

    def poll_token(s: requests.Session, endpoint: str) -> t.Optional[str]:
        r = s.get(endpoint)
        return None if r.status_code == 204 else _process_res(r).api_key

    with requests.Session() as s:
        signup_token = create_token(s)
        signup_url = furl(path=open_url, origin=server).add({"signup_token": signup_token}).url

        print(
            f"\nOpening {action} page.. Please complete {action} via this page and return to the terminal\n\nIf the page didn't open, use the link below\n{signup_url}"
        )
        webbrowser.open(url=signup_url, new=2)

        # Declare the endpoint outside the poll_token function to save rebuilding on each poll
        poll_endpoint = furl(path=f"/api/api-signup-tokens/{signup_token}/", origin=server).url
        api_key = None
        try:
            with click_spinner.spinner():
                while api_key is None:
                    r = poll_token(s, poll_endpoint)
                    if r:
                        api_key = r
                    else:
                        time.sleep(5)
                return api_key
        except KeyboardInterrupt:
            sys.exit(1)
