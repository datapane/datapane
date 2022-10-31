import pytest

from datapane.client import config
from datapane.common import DPMode, _setup_dp_logging, set_dp_mode


@pytest.fixture(autouse=True)
def dp_setup(request, monkeypatch, tmp_path):
    """
    Set up the common environment for each test

    Skip optional setup tasks with::

        @pytest.mark.skip_setup
    """
    # Monkeypatch config file into a tmp dir
    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True)
    monkeypatch.setattr(config, "APP_DIR", config_dir)
    monkeypatch.setattr(config, "CONFIG_PATH", config_dir / config.CONFIG_FILENAME)

    # Init API with full debug logging
    set_dp_mode(DPMode.SCRIPT)
    _setup_dp_logging(verbosity=2)

    # Optional setup
    if "skip_setup" not in request.keywords:
        config.init()
