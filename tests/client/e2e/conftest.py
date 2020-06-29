import os

import pytest

from datapane.client import api
from datapane.client import config as c

TEST_SERVER = os.environ.get("DP_TEST_SERVER", "http://localhost:8090")
TEST_TOKEN = os.environ.get("DP_TEST_TOKEN", "")


@pytest.fixture(scope="session")
def dp_login():
    test_config = c.Config(server=TEST_SERVER, token=TEST_TOKEN, analytics=True)
    api.init(config=test_config, verbosity=2)
