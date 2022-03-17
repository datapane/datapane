from pathlib import Path
from typing import Optional

import pytest

import datapane as dp
import datapane.client.config as c
from datapane.client.utils import InvalidTokenError

from .conftest import TEST_SERVER, TEST_TOKEN


def test_auth():
    """Test API-based auth"""
    TEST_ENV = "test_env"

    fp: Optional[Path] = None
    try:
        dp.init(config_env=TEST_ENV)

        config = c.get_config()
        fp = config._path

        # check the config env file can't login and is the default
        assert config.token == c.DEFAULT_TOKEN
        with pytest.raises(InvalidTokenError):
            dp.ping()

        # login
        email = dp.login(token=TEST_TOKEN, server=TEST_SERVER, env=TEST_ENV, cli_login=False)
        assert email == "test@datapane.com"
        # logout
        dp.logout(env=TEST_ENV)

        # check we've remove the config env file
        assert not fp.exists()

    finally:
        if fp and fp.exists():
            fp.unlink()
