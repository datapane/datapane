import pytest

import datapane as dp
import datapane.client.config as c
from datapane.client.utils import InvalidTokenError

from .conftest import TEST_SERVER, TEST_TOKEN


def test_auth():
    """Test API-based auth"""
    config = c.get_config()

    # check the config env file can't login and is the default
    assert config.token == c.DEFAULT_TOKEN
    with pytest.raises(InvalidTokenError):
        dp.ping()

    # login
    email = dp.login(token=TEST_TOKEN, server=TEST_SERVER, cli_login=False)
    assert email == "test@datapane.com"

    # Check the config is correct
    config = c.get_config()
    assert config.token == TEST_TOKEN
    assert config.email == "test@datapane.com"

    # logout
    dp.logout()

    # check the config env file doesn't have
    config = c.get_config()
    assert config.token == c.DEFAULT_TOKEN
    assert config.email == ""
