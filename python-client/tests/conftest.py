# ruff: noqa: E402
# We need to modify environment variables before importing Datapane

import os

os.environ["DP_TEST_ENV"] = "true"

import pytest

from datapane import DPMode, set_dp_mode
from datapane.client import config
from datapane.client.utils import _setup_dp_logging


@pytest.fixture(autouse=True)
def dp_setup(request, monkeypatch, tmp_path):
    """
    Set up the common environment and clean default config for each test.

    Skip optional init tasks with::

        @pytest.mark.skip_init

    When writing fixtures which need to change the config (eg dp_login) see docs:
    https://docs.pytest.org/en/stable/reference/fixtures.html#fixture-instantiation-order
    """

    # Init API with full debug logging
    set_dp_mode(DPMode.SCRIPT)
    _setup_dp_logging(verbosity=2)

    # Optional init steps
    if "skip_dp_init" not in request.keywords:
        config.init()
