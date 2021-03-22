import os

import pytest

from datapane.client import config as c

TEST_SERVER = os.environ.get("DP_TEST_SERVER", "http://localhost:8090")
TEST_TOKEN = os.environ.get("DP_TEST_TOKEN", "")


# use module scope as we enable dp_login using a per-module marker
@pytest.fixture(scope="module")
def dp_login():
    print("dp_login")
    c.set_config(c.Config(server=TEST_SERVER, token=TEST_TOKEN))
    yield
    c.set_config(None)
    print("closing dp_login")
