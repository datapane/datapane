import os

import pytest

from datapane.client import config as c

TEST_SERVER = os.environ.get("DP_TEST_SERVER", "http://localhost:8090")
TEST_TOKEN = os.environ.get("DP_TEST_TOKEN", "")


# Function scope so it's run each fixture, but autouse=False so it's run after dp_setup
@pytest.fixture()
def dp_login():
    print("dp_login")
    c.set_config(c.Config(server=TEST_SERVER, token=TEST_TOKEN))
    yield
    c.set_config(None)
    print("closing dp_login")
