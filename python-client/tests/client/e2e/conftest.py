import os

import pytest

from datapane.client import config as c

TEST_SERVER = os.environ.get("DP_TEST_SERVER", "http://localhost:8090")
TEST_TOKEN = os.environ.get("DP_TEST_TOKEN", "")


@pytest.fixture()
def dp_login():
    """
    Set the config to log the user into the test server.

    Function scope so it's run each test, but autouse=False so it is run after dp_setup
    creates the config dir for that test
    """
    c.set_config(c.Config(server=TEST_SERVER, token=TEST_TOKEN))
    yield
    c.set_config(None)
