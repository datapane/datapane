import dataclasses as dc
from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager, Dict, Optional

import click
import dacite
from ruamel.yaml import YAML

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
analytics: False
"""


def get_config_file(env: str = DEFAULT_ENV) -> Path:
    return APP_DIR / f"{env}.yaml"


@dc.dataclass(frozen=True)
class Config:
    """Global config read from config file"""

    # TODO - hardcode to datapane.com for now
    server: str
    token: str
    analytics: bool = False


# TODO - wrap into a singleton object that includes callable?
config: Optional[Config] = None


def set_config(c: Config):
    global config
    config = c


def get_config() -> Config:
    global config
    return config


@contextmanager
def update_config(config_env: str) -> ContextManager[Dict]:
    """Update config file without losing comments"""
    config_f = get_config_file(config_env)
    yaml = YAML()

    with config_f.open("r") as inp:
        code = yaml.load(inp)

    yield code

    with config_f.open("w") as f:
        yaml.dump(code, f)


def load_from_envfile(config_env: str) -> Path:
    """Init the cmd-line env"""
    config_f = get_config_file(config_env)
    yaml = YAML()

    if not config_f.exists():
        config_f.write_text(get_default_config())

    with config_f.open("r") as f:
        c_yaml = yaml.load(f)

    # load config obj from file
    c_obj = dacite.from_dict(Config, c_yaml)
    # log.debug(f"Read config as {c_obj}")
    set_config(c_obj)

    return config_f
