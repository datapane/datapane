"""
Config subsystem
We use a module-level singleton pattern here, where top-level functions and globals
act like the state for a "Manager" class around the internal Config object
"""
import configparser
import dataclasses as dc
import typing as t
import uuid
from contextlib import suppress
from os import getenv
from pathlib import Path
from typing import Optional

import click

from datapane import _IN_PYTEST, log

from .exceptions import InvalidTokenError

APP_NAME = "datapane"
APP_DIR = Path(getenv("DATAPANE_APP_DIR", click.get_app_dir(APP_NAME)))
APP_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILENAME = "config.ini"
LEGACY_CONFIG_FILENAME = "default.yaml"
CONFIG_PATH = Path(getenv("DATAPANE_CONFIG", APP_DIR / CONFIG_FILENAME))
LEGACY_CONFIG_PATH = APP_DIR / LEGACY_CONFIG_FILENAME
CONFIG_SECTION = "default"
PAST_DEFAULT_SERVER = "https://datapane.com"
DEFAULT_SERVER = "https://cloud.datapane.com"
DEFAULT_TOKEN = "TOKEN_HERE"
LATEST_VERSION = 6


# TODO - wrap into a singleton object that includes callable?
@dc.dataclass
class Config:
    """
    Global config read from config file

    Versioning
    - for b/c from before versioning config file, we set version to 1 if doesn't exist
    - else we set it to latest version for a new config via post_init hook
    - only on loading a config file do we run the upgrade function
    """

    server: str = DEFAULT_SERVER
    token: str = DEFAULT_TOKEN
    email: str = ""
    session_id: str = dc.field(default_factory=lambda: uuid.uuid4().hex)
    version: int = 1  # for b/c if version doesn't exist in file, set to latest in post_init hook
    completed_action: bool = False  # only active on first action

    from_file: dc.InitVar[bool] = False

    def __post_init__(self, from_file: bool):
        self.server = self.server.rstrip("/")  # server should be a valid origin
        if not from_file:
            # set to latest if generating config file
            self.version = LATEST_VERSION

    @property
    def is_public(self) -> bool:
        return self.server == DEFAULT_SERVER

    @property
    def is_org(self) -> bool:
        return not self.is_public

    @property
    def is_authenticated(self) -> bool:
        return self.token != DEFAULT_TOKEN  # or bool(self.email)

    @property
    def is_anonymous(self) -> bool:
        return not self.is_authenticated

    # MANAGER functions
    @classmethod
    def load(cls) -> "Config":
        """Load config for an environment and set globally"""
        # Read config file
        cls.ensure_config_file()
        parser = configparser.ConfigParser()
        parser.read(CONFIG_PATH)
        if CONFIG_SECTION not in parser:
            log.error(f"Config file at {CONFIG_PATH} does not contain a {CONFIG_SECTION} section")
            raise ValueError(f"Config file does not contain a {CONFIG_SECTION} section")

        # Process config into a new dataclass
        raw_conf: configparser.SectionProxy = parser[CONFIG_SECTION]
        kwargs: t.Dict[str, t.Any] = {
            "from_file": True,
        }
        for field in dc.fields(cls):
            if field.name in raw_conf:
                if field.type is bool:
                    value = raw_conf[field.name].lower() == "true"
                else:
                    value = field.type(raw_conf[field.name])
                kwargs[field.name] = value

        config: Config = Config(**kwargs)
        log.debug(f"Loaded client environment from {CONFIG_PATH}")

        # check if stored file is out of date
        config.upgrade_config_format()

        # set to the global state
        set_config(config)
        return config

    @classmethod
    def create_default(cls) -> None:
        """Create an default config file"""
        # create default file
        _config = Config()
        _config.save()
        log.info(f"Created config file at {CONFIG_PATH}")

    def save(self):
        data = dc.asdict(self)
        parser = configparser.ConfigParser()
        parser[CONFIG_SECTION] = data
        with CONFIG_PATH.open("w") as file:
            parser.write(file)

    def remove(self):
        CONFIG_PATH.unlink()

    @classmethod
    def ensure_config_file(cls) -> None:
        """
        Ensure the config file exists at CONFIG_PATH
        """
        if CONFIG_PATH.exists():
            return

        # Look for YAML from Version 5 and earlier
        yaml_path = LEGACY_CONFIG_PATH
        if yaml_path.exists():
            # Migrate
            log.info(f"Found legacy config file at {yaml_path}")
            CONFIG_PATH.write_text(f"[{CONFIG_SECTION}]\n" + yaml_path.read_text())
            yaml_path.unlink()
            log.info(f"Successfully migrated to {CONFIG_PATH}")

        else:
            # Neither exist - create new
            cls.create_default()

    def upgrade_config_format(self):
        """Handles updating the older config format
        - we default to the oldest version with default values, and upgrade here
        """
        # this isn't tied to a particular config version
        if self.server == PAST_DEFAULT_SERVER:
            self.server = DEFAULT_SERVER

        # migrate older config files
        if self.version in (1, 2, 3):
            # If token exists check still valid and can login, use to get server props
            if self.token and self.token != DEFAULT_TOKEN:
                from .api.user import ping

                with suppress(Exception):
                    # get the email for v4 of spec
                    self.email = ping(config=self, cli_login=True, verbose=False)

                # if not self.completed_action:
                #     # we could be on older version, but with a valid token
                #     # but haven't completed an action, so force it
                #     from .analytics import capture
                #
                #     capture("CLI Login", config=self, with_token=True)

            self.version = LATEST_VERSION
            self.save()
        elif self.version in (4, 5):
            self.version = LATEST_VERSION
            self.save()  # trigger removal of _env & _pass from file


# TODO - create a ConfigMgr singleton object?
config: Optional[Config] = None


################################################################################
# MODULE LEVEL INTERFACE
def init(config: t.Optional[Config] = None) -> Config:
    """
    Init an API config
     - this MUST handle being called multiple times and only from the main-thread
    """
    if globals().get("config") is not None:
        log.debug("Reinitialising client config")

    if config:
        set_config(config)
    else:
        config = Config.load()

    return config


def check_get_config() -> Config:
    """Attempt to get a config object, reloading if necessary
    - used when we need a valid API token, e.g. when performing a network action"""
    config = get_config()
    if config.token == DEFAULT_TOKEN:
        # try reinit, as may have ran login in another terminal/subprocess
        _config = init()
        if _config.token == DEFAULT_TOKEN:
            # still don't have a token set, open up the browser and wait for login
            if not _IN_PYTEST:
                from datapane.client.api import signup

                signup()
                _config = init()
                return _config
            raise InvalidTokenError(
                "Please sign-up and login - if you already have then please restart your Jupyter kernel/Python instance to initialize your new token"
            )

        return _config
    return config


def set_config(c: Optional[Config]):
    global config
    config = c


def get_config() -> Config:
    """Get the current config object, doesn't attempt to re-init the API token"""
    global config
    if config is None:
        raise RuntimeError("Config must be initialised before it can be used")

    return config
