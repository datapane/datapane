"""
Config subsystem
We use a module-level singleton pattern here, where top-level functions and globals
act like the state for a "Manager" class around the internal Config object
"""
import dataclasses as dc
import typing as t
import uuid
import webbrowser
from pathlib import Path
from typing import Optional

import click
import dacite
import yaml
from furl import furl

from datapane import _IN_DPSERVER, _IN_PYTEST, log

from .utils import InvalidTokenError

APP_NAME = "datapane"
APP_DIR = Path(click.get_app_dir(APP_NAME))
APP_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_ENV = "default"
DEFAULT_SERVER = "https://datapane.com"
DEFAULT_TOKEN = "TOKEN_HERE"


# TODO - wrap into a singleton object that includes callable?
@dc.dataclass
class Config:
    """Global config read from config file"""

    server: str = DEFAULT_SERVER
    token: str = DEFAULT_TOKEN
    username: str = ""
    session_id: str = dc.field(default_factory=lambda: uuid.uuid4().hex)
    analytics: bool = True
    version: int = 1

    _env: t.ClassVar[Optional[str]]
    _path: t.ClassVar[Optional[Path]]

    def __post_init__(self):
        # NOTE - could make env an optional initvar
        self.analytics = self.default_analytics_state(self.server, self.analytics)

    @property
    def is_public(self) -> bool:
        return self.server == DEFAULT_SERVER

    def disable_analytics(self):
        self.analytics = False
        self.save()

    # MANAGER functions
    @classmethod
    def load(cls, env: str = "default") -> "Config":
        """Load config for an environment and set globally"""
        config_f = cls.get_config_file(env)
        if not config_f.exists():
            cls.create_default(env, config_f)

        with config_f.open("r") as f:
            c_yaml = yaml.safe_load(f)

        # load config obj from file
        config = dacite.from_dict(Config, c_yaml)
        config._env = env
        config._path = config_f
        log.debug(f"Loaded client environment from {config._path}")

        # check if stored file is out of date
        config.upgrade_config_format()

        # set to the global state
        set_config(config)
        return config

    @classmethod
    def create_default(cls, env: str, config_f: Path) -> None:
        """Create an default config file"""
        from .analytics import capture_init

        # create default file
        _config = Config()
        _config.save(env)
        log.debug(f"Creating default config file at {config_f}")
        capture_init(_config)

    def save(self, env: t.Optional[str] = None):
        if env:
            self._env = env
            self._path = self.get_config_file(env)

        with self._path.open("w") as f:
            yaml.safe_dump(dc.asdict(self), f)

    def remove(self):
        self._path.unlink()

    @staticmethod
    def get_config_file(env: str) -> Path:
        return APP_DIR / f"{env}.yaml"

    def upgrade_config_format(self):
        """Handles updating the older config format"""
        # migrate older config files
        if self.version == 1:  # self.session_id == "":
            self.analytics = self.default_analytics_state(self.server)
            self.version = 2
            self.save()

            # If the user was already logged in call ping to generate alias on the server
            if self.username:
                from .api import ping

                ping(config=self, cli_login=True)

    @staticmethod
    def default_analytics_state(server: str, prev_val: bool = True) -> bool:
        """Determine the initial state for analytics if not already set"""
        from .api import by_datapane

        # disable is prev disabled or in certain envs
        if prev_val is False or by_datapane or _IN_PYTEST or _IN_DPSERVER:
            return False

        f = furl(server)
        # disable for localhost
        if f.host == "localhost":
            return False
        # disable for non-managed
        if f.host.split(".")[-2] != "datapane":
            return False

        return True


# TODO - create a ConfigMgr singleton object?
config: Optional[Config] = None


################################################################################
# MODULE LEVEL INTERFACE
def init(config_env: str = "default", config: t.Optional[Config] = None) -> Config:
    """
    Init an API config
     - this MUST handle being called multiple times and only from the main-thread
    """
    if get_config() is not None:
        log.debug("Reinitialising client config")

    if config:
        set_config(config)
    else:
        config = Config.load(config_env)

    return config


def check_get_config() -> Config:
    """Attempt to get a config object, reloading if necessary"""
    global config
    if config.token == DEFAULT_TOKEN:
        # try reinit, as may have ran login in another terminal/subprocess
        _config = init(config._env)
        if _config.token == DEFAULT_TOKEN:
            # still don't have a token set for the env, open up the browser
            if not _IN_PYTEST:
                f = furl(path="/home/", origin=_config.server)
                webbrowser.open(url=str(f), new=2)
            raise InvalidTokenError(
                "Please sign-up and login - if you already have then please restart your Jupyter kernel/Python instance to initialize your new token"
            )
        return _config
    return config


def set_config(c: Optional[Config]):
    global config
    config = c


def get_config() -> Config:
    global config
    return config
