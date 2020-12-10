import dataclasses as dc
import typing as t
import webbrowser
from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager, Dict, Optional

import click
import dacite
from furl import furl
from ruamel.yaml import YAML

from datapane import log

from .utils import InvalidTokenError

APP_NAME = "datapane"
APP_DIR = Path(click.get_app_dir(APP_NAME))
APP_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_ENV = "default"
DEFAULT_SERVER = "https://datapane.com"
DEFAULT_TOKEN = "TOKEN_HERE"


def get_default_config() -> str:
    return f"""\
# server API address
server: {DEFAULT_SERVER}
# API token - copy and paste from https://server/settings/
token: {DEFAULT_TOKEN}
# analytics - set to true to send usage and error reporting
analytics: false
"""


def get_config_file(env: str = DEFAULT_ENV) -> Path:
    config_f = APP_DIR / f"{env}.yaml"
    if not config_f.exists():
        config_f.write_text(get_default_config())
        log.debug(f"Creating default config file at {config_f}")
    return config_f


@dc.dataclass(frozen=True)
class Config:
    """Global config read from config file"""

    # TODO - hardcode to datapane.com for now
    server: str
    token: str
    analytics: bool = False


# TODO - wrap into a singleton object that includes callable?
config: Optional[Config] = None
last_config_env: Optional[str] = None


def set_config(c: Optional[Config]):
    global config
    config = c


def get_config() -> Config:
    global config
    return config


def check_get_config() -> Config:
    """Attempt to get a config object, reloading if necessary"""
    global config
    if config and config.token == DEFAULT_TOKEN:
        # try reinit, as may have ran login in another terminal/subprocess
        global last_config_env
        init(last_config_env)
        if config.token == DEFAULT_TOKEN:
            # still don't have a token set for the env, open up the browser
            f = furl(path="/home/", origin=config.server)
            webbrowser.open(url=str(f), new=2)
            raise InvalidTokenError(
                "Please sign-up and login - if you already have then please restart your Jupyter kernel/Python instance to initialize your new token"
            )
    return config


@contextmanager
def update_config(config_env: str) -> ContextManager[Dict]:
    """Update config file without losing comments and reinit in-memory config"""
    config_f = get_config_file(config_env)
    yaml = YAML()

    with config_f.open("r") as f:
        code = yaml.load(f)

    yield code

    with config_f.open("w") as f:
        yaml.dump(code, f)

    # reinit if already in process
    init(config_env=config_env)


def load_from_envfile(config_env: str) -> Path:
    """Init the cmd-line env"""
    global last_config_env
    last_config_env = config_env

    config_f = get_config_file(config_env)
    yaml = YAML()

    with config_f.open("r") as f:
        c_yaml = yaml.load(f)

    # load config obj from file
    c_obj = dacite.from_dict(Config, c_yaml)
    # log.debug(f"Read config as {c_obj}")
    set_config(c_obj)

    return config_f


def init(config_env: str = "default", config: t.Optional[Config] = None):
    """Init an API config - this MUST handle being called multiple times"""
    if get_config() is not None:
        log.debug("Reinitialising client config")

    if config:
        set_config(config)
    else:
        config_f = load_from_envfile(config_env)
        log.debug(f"Loaded client environment from {config_f}")
