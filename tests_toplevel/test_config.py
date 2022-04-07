import os
from unittest import mock

import pytest


@pytest.fixture(scope="module")
def mock_click_path(tmp_path_factory):
    """Fixture setups some default mocks to work around config files and analytics"""
    tmp_path = tmp_path_factory.mktemp("click")

    with mock.patch("click.get_app_dir", autospec=True) as gad:
        # patch the config file path and no_analytics
        gad.return_value = str(tmp_path)
        yield tmp_path


@pytest.fixture
def mock_analytics(mock_click_path):
    """Fixture setups some default mocks to work around config files and analytics"""

    with mock.patch("datapane.client.analytics.posthog", autospec=True) as posthog, mock.patch(
        "datapane.client.analytics._NO_ANALYTICS", False
    ), mock.patch("datapane.client.api.user.ping", autospect=True) as ping:
        ping.return_value = "joebloggs@datapane.com"
        yield (posthog, mock_click_path)


def _upgrade_version(mock_analytics, env: str, config: str, identify_calls: int, capture_calls: int):
    # NOTE - we need env as the click mock is global, not function scoped, so all files are in same dir
    (posthog, tmp_path) = mock_analytics
    from datapane.client import config as c

    env_file = tmp_path / f"{env}.yaml"
    env_file.write_text(config)
    _config = c.Config.load(env)
    assert c.config.version == 4
    assert _config.email == "joebloggs@datapane.com"
    assert _config.completed_action
    assert posthog.identify.call_count == identify_calls
    assert posthog.capture.call_count == capture_calls
    # TODO - we really should test the saved yaml also...


def test_upgrade_v0(mock_analytics):
    config_file = """
    server: https://datapane.v0.com
    token: REAL_TOKEN
    """
    _upgrade_version(mock_analytics, "v0", config_file, identify_calls=1, capture_calls=2)


def test_upgrade_v1(mock_analytics):
    config_file = """
    server: https://datapane.v1.com
    token: REAL_TOKEN
    version: 1
    """
    _upgrade_version(mock_analytics, "v1", config_file, identify_calls=1, capture_calls=2)


def test_upgrade_v2(mock_analytics):
    config_file = """
    server: https://datapane.v2.com
    session_id: 2464f9fb68f9450b82e67a26d8c9582b
    token: REAL_TOKEN
    username: 'datapane-test'
    version: 2
    """
    _upgrade_version(mock_analytics, "v2", config_file, identify_calls=1, capture_calls=2)


def test_upgrade_v3(mock_analytics):
    config_file = """
    completed_action: false
    server: https://datapane.v3.com
    session_id: 94cecec23d32433db4c8d9105e8eb9c6
    token: REAL_TOKEN
    username: datapane-test
    version: 3
    """
    _upgrade_version(mock_analytics, "v3", config_file, identify_calls=1, capture_calls=2)


def test_upgrade_v3_completed(mock_analytics):
    config_file = """
    completed_action: true
    server: https://datapane.v3.com
    session_id: 94cecec23d32433db4c8d9105e8eb9c6
    token: REAL_TOKEN
    username: datapane-test
    version: 3
    """
    _upgrade_version(mock_analytics, "v3c", config_file, identify_calls=0, capture_calls=0)


# def test_upgrade_v3_nologin(mock_analytics):
#     config_file = """
#     completed_action: false
#     server: https://datapane.v3.com
#     session_id: 94cecec23d32433db4c8d9105e8eb9c6
#     token: TOKEN_HERE
#     username:
#     version: 3
#     """
#     _upgrade_version(mock_analytics, "v3n", config_file, identify_calls=0, capture_calls=0)


def test_new_config(mock_analytics, monkeypatch):
    # TODO - is there a way to run this within the normal test framework, i.e. perhaps unloading/reloading datapane module so we can
    #  setup our mocks/patches first?

    (posthog, tmp_path) = mock_analytics

    # NOTE - we can't import this until we've set up the mocks, hence the separate test-runner
    from datapane.client import config as c

    # check pre-invariants
    c.init()
    assert c.config.version == 4
    assert c.config.email == ""
    assert not c.config.completed_action
    assert posthog.identify.call_count == 0
    assert posthog.capture.call_count == 0

    # run login event
    import datapane as dp
    from datapane.client import config as c

    email = dp.login(token="REAL_TOKEN")
    assert email == "joebloggs@datapane.com"

    # check config file
    assert c.config.version == 4
    assert c.config.email == "joebloggs@datapane.com"
    assert c.config.completed_action
    session_id = c.config.session_id

    # check analytics
    assert posthog.identify.call_count == 1
    assert posthog.capture.call_count == 2

    # load and check config file
    _config = c.Config.load()
    assert c.config.version == 4
    assert _config.email == "joebloggs@datapane.com"
    assert _config.completed_action
    assert _config.session_id == session_id

    # run additional event
    # depends on fe-components - only run locally
    if "CI" not in os.environ:
        monkeypatch.chdir(tmp_path)
        from tests.client.local.api.test_reports import gen_report_simple

        report = gen_report_simple()
        report.save(path="test_out.html", name="My Wicked Report", author="Datapane Team")
        assert posthog.identify.call_count == 1
        assert posthog.capture.call_count == 3
