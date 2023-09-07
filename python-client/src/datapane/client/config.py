"""
Config subsystem
We use a module-level singleton pattern here, where top-level functions and globals
act like the state for a "Manager" class around the internal Config object
"""
import typing as t
from typing import Optional

from .utils import log


class Config:
    @property
    def is_public(self) -> bool:
        return True

    @property
    def is_org(self) -> bool:
        return not self.is_public

    @property
    def is_authenticated(self) -> bool:
        return False

    @property
    def is_anonymous(self) -> bool:
        return True


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
        config = Config()

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
