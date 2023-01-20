"""## Datapane User API

User management functions, including authentication

It's possible to authenticate within Python, however we also provide (and recommend) authenticating
via the CLI, as it's easier to automate.

```
$ datapane login --token ...
$ datapane logout
```

"""
import os
import runpy
import shutil
import sys
import time
import typing as t
import warnings
from pathlib import Path

import click_spinner
import importlib_resources as ir
import requests
from dulwich import client, errors, porcelain
from furl import furl
from munch import Munch

from datapane import __version__
from datapane.client.environment import environment
from datapane.common import URL
from datapane.common.utils import pushd

from .. import DPError
from .. import config as c
from ..analytics import capture, capture_event
from ..utils import display_msg, failure_msg, open_in_browser, success_msg
from .common import _process_res

__all__ = ["login", "signup", "logout", "ping", "hello_world", "template"]


def signup(server: str = c.DEFAULT_SERVER):
    """Signup and link your account to the Datapane CLI automatically"""
    token = token_connect(server=server, action="signup")
    # login and re-init against the signed-up server
    login(token, server=server)


def login(
    token: t.Optional[str] = None, server: str = c.DEFAULT_SERVER, env: t.Optional[str] = None, cli_login: bool = True
) -> str:
    """
    Login to the specified Datapane Server, storing the token within a config-file called `env` for future use

    Args:
        token: Token to use when logging in
        server: Datapane Server to connect to (default: Datapane Community at https://datapane.com/)
        cli_login: Toggle if this login is occuring via the CLI (optional)

    Returns:
        the email for the logged in user

    ..note:: Can also be ran via CLI as `"datapane login"`
    """
    # TODO: 0.16: Remove deprecated argument
    if env is not None:
        warnings.warn("The env argument for login() is deprecated and will be removed in 0.16", FutureWarning)

    config = c.Config(server=server)

    token_type = "cli"
    if token is None:
        # get via api-first mechanism instead
        token = token_connect(server=config.server)
        if token:
            token_type = "api"

    config.token = token
    # check token is valid, throws exception and error msg to user if not
    email = ping(config=config, cli_login=cli_login)

    # update config with valid values
    config.email = email
    config.save()
    c.init(config=config)
    capture("CLI Login", token_type=token_type)
    return config.email


def logout(env: t.Optional[str] = None) -> None:
    """
    Logout from Datapane Server, removing local credentials

    ..note:: Can also be ran via CLI as `"datapane logout"`
    """
    # TODO: 0.16: Remove deprecated argument
    if env is not None:
        warnings.warn("The env argument for logout() is deprecated and will be removed in 0.16", FutureWarning)

    if c.config is None:
        failure_msg("Not logged in", do_exit=True)
        return

    success_msg(f"Logged out from {c.config.server}")
    c.config.remove()
    c.set_config(None)  # ??
    c.init()


def ping(config: t.Optional[c.Config] = None, cli_login: bool = False, verbose: bool = True) -> str:
    """Ping the Datapane Server to check login credentials"""
    # hardcode ping check as used for login/logout logic independent of main API requests
    config = config or c.check_get_config()
    endpoint = "/api/settings/details/"
    f = furl(path=endpoint, origin=config.server)
    headers = {"Authorization": f"Token {config.token}", "Datapane-API-Version": __version__}
    q_params = dict(cli_id=config.session_id) if cli_login else {}
    r = requests.get(str(f), headers=headers, params=q_params)
    response: Munch = _process_res(r)
    email = response.email

    if verbose:
        success_msg(f"Connected successfully to {config.server} as {email}")

    return email


def _run_script(script: Path):
    """Run the template script and copy it locally to cwd"""
    script_path = ir.files("datapane.resources.templates.hello") / script
    shutil.copyfile(str(script_path), script_path.name)
    runpy.run_path(str(script_path), run_name="__datapane__")


def _run_template(template_path: Path):
    """Run the template script"""
    # Use template_path as cwd to support relative paths in template script
    with pushd(template_path):
        # Try to run the template script.
        try:
            runpy.run_path(
                "template.py",
                run_name="__datapane__",
            )
        # Notify the user of missing packages that are required by the template
        except ModuleNotFoundError as e:
            raise DPError(f"Please install the following packages to run this template\n{e.name}") from e


def _download_template(url: URL):
    """Download the template from a repository url, and delete the .git directory

    Returns:
        The path of the cloned template repository
    """

    url = _check_repo_url(url)

    # Check if target directory already exists.
    # This check is identical to the target check in `dulwich.porcelain.clone`:
    # https://github.com/jelmer/dulwich/blob/78e6ae0960d79060d4ff19f0aa5dc4b32296116d/dulwich/porcelain.py#L439-L441
    target = url.rstrip("/").split("/")[-1]
    target_dir_exists = os.path.exists(target)

    # Avoid overwriting user's data
    if target_dir_exists:
        raise DPError(f"Directory {target} already exists.")

    # Shallowest clone of the template repo
    template_repo = porcelain.clone(url, target=target, depth=1)

    # Remove .git directory
    shutil.rmtree(template_repo.controldir())

    return template_repo.path


def _check_repo_url(url: URL):
    """Check if the template repository exists. Supports first or third-party templates.

    Returns:
        The absolute uri of the template repository.
    """
    # Check if remote is a git repo
    try:
        porcelain.ls_remote(url)
    except (errors.NotGitRepository, client.HTTPUnauthorized):
        # A check for special characters (: and /) to avoid unknowns
        # e.g., unintended repo download/execution
        special_chars = [":", "/"]
        if any(special_char in url for special_char in special_chars):
            raise DPError(f"{url} is not a valid template repository.")

        try:
            # Try appending the supplied url to the datapane organization
            full_url = f"https://github.com/datapane/{url}"
            # Check if remote is a first-party datapane repo
            # that has been located with a relative path.
            porcelain.ls_remote(full_url)
        except (errors.NotGitRepository, client.HTTPUnauthorized) as e:
            raise DPError(f"{url} is not a valid template repository.") from e
        else:
            # Update the URL with absolute URI
            url = URL(full_url)
    return url


@capture_event("CLI Hello World")
def hello_world():
    """Create and run an example report, and open in the browser"""
    display_msg(
        "Creating and running `./hello.py` - running this code generates a sample Datapane report. You can edit the script and run it again to change the generated report.\n"
    )

    _run_script("hello.py")

    display_msg(
        "\nWe’d also love to invite you to join our Discord {chat_url:l}, suggest a feature {nolt_url:l}, and be part of our open source community {github_url:l}.",
        chat_url="https://chat.datapane.com",
        nolt_url="https://datapane.nolt.io",
        github_url="https://github.com/datapane/datapane",
    )


@capture_event("CLI Template")
def template(url: URL, execute: bool):
    """Retrieve and run a template report, and open in the browser"""
    display_msg(f"Retrieving{' and running ' if execute else ' '}the template at `{url}`.\n")

    template_path = _download_template(url)

    if execute:
        _run_template(template_path)

    display_msg(
        f"\nYou can edit `template.py` and run it from the new {template_path} directory to change the generated report."
    )

    display_msg(
        "\nWe’d also love to invite you to join our Discord {chat_url:l}, suggest a feature {nolt_url:l}, and be part of our open source community {github_url:l}.",
        chat_url="https://chat.datapane.com",
        nolt_url="https://datapane.nolt.io",
        github_url="https://github.com/datapane/datapane",
    )


def token_connect(server: str, action: str = "login") -> t.Optional[str]:
    """
    Creates a login token, and prompts the user to login while polling for completion.
    Then log the user into the CLI with the retrieved API token.
    """

    def create_token(s: requests.Session) -> str:
        create_endpoint = furl(path="/api/api-login-tokens/", origin=server).url
        req = s.post(create_endpoint)
        res: Munch = _process_res(req)
        return res.key

    def poll_token(s: requests.Session, endpoint: str) -> t.Optional[str]:
        r: requests.Response = s.get(endpoint)
        if r.status_code == 204:
            return None
        else:
            processed_res: Munch = _process_res(r)
            return processed_res.api_key

    with requests.Session() as s:
        login_token = create_token(s)
        url = (
            furl(path="/accounts/api-login-token-accept", origin=server)
            .add({"login_token": login_token, "action": action, "jupyter": environment.is_notebook_environment})
            .url
        )

        display_msg(f"Opening {action} page.. please login or create an account via this page to proceed.")
        display_msg("If the page didn't open, use the link {login_url:l}", login_url=url)

        open_in_browser(url)

        # Declare the endpoint outside the poll_token function to save rebuilding on each poll
        poll_endpoint = furl(path=f"/api/api-login-tokens/{login_token}/", origin=server).url
        api_key = None
        try:
            # NOTE mypy flags this usage as incorrect but is fine according to the docs
            with click_spinner.spinner():  # type: ignore
                while api_key is None:
                    r = poll_token(s, poll_endpoint)
                    if r:
                        api_key = r
                    else:
                        time.sleep(5)
                # NOTE mypy thinks this unreachable but it is...
                return api_key
        except KeyboardInterrupt:
            sys.exit(1)
