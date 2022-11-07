from __future__ import annotations

import dataclasses as dc
import os
from pathlib import Path
from unittest import mock

import pytest

import datapane as dp
from datapane.client import config as c

# Disable automatic c.init() - all tests in this file need to initialise their own configs
pytestmark = [pytest.mark.skip_dp_init]


@dc.dataclass
class Expected:
    """Expected data for tests"""

    # Posthog usage
    identify_calls: int
    capture_calls: int

    # Stored attributes of Config, using different defaults to ensure we're getting loaded values
    server: str = "https://test.datapane.com"
    token: str = "test_token"
    email: str = "test@datapane.com"
    session_id: str = "test_session_id"
    version: int = c.LATEST_VERSION
    completed_action: bool = True


@pytest.fixture
def posthog():
    """Mock analytics, returning a fn to check posthog calls"""
    with mock.patch("datapane.client.analytics.posthog", autospec=True) as posthog, mock.patch(
        "datapane.client.analytics._NO_ANALYTICS", False
    ):
        yield posthog


def strip_indent(multiline: str) -> str:
    """Improve legibility of multi-line test strings by stripping indentation"""
    lines = multiline.lstrip("\n").rstrip("\n ").splitlines()
    indent = len(lines[0]) - len(lines[0].lstrip(" "))
    return "\n".join(line[indent:] for line in lines)


def write_config(raw_config, config_path: Path | None = None):
    """Write the config file"""
    if config_path is None:
        config_path = c.CONFIG_PATH
    config_path.write_text(strip_indent(raw_config))


@pytest.fixture(autouse=True)
def mock_config_defaults():
    """Mock calculated defaults so we can assert against them"""
    with mock.patch("uuid.uuid4", autospec=True) as uuid4, mock.patch(
        "datapane.client.api.user.ping", autospec=True
    ) as ping:
        uuid4.return_value = mock.Mock(hex=Expected.session_id)
        ping.return_value = Expected.email
        yield


def assert_config(posthog, raw_config: str, expected: Expected, config_path: Path | None = None):
    """Write and load a config and assert it is expected"""
    write_config(raw_config, config_path)
    config = c.Config.load()
    assert_config_object(posthog, config, expected=expected)

    # Check the saved config looks correct. ConfigParser writes in order of class attribute definition.
    raw_expected = strip_indent(
        f"""
        [{c.CONFIG_SECTION}]
        server = {expected.server}
        token = {expected.token}
        email = {expected.email}
        session_id = {expected.session_id}
        version = {expected.version}
        completed_action = {expected.completed_action}
        """
    )
    assert c.CONFIG_PATH.read_text().rstrip("\n") == raw_expected

    return config


def assert_config_object(posthog, config: c.Config, expected: Expected):
    """Assert a config object is as expected"""
    assert config.server == expected.server
    assert config.token == expected.token
    assert config.email == expected.email
    assert config.session_id == expected.session_id
    assert config.version == expected.version
    assert config.completed_action == expected.completed_action

    assert posthog.identify.call_count == expected.identify_calls
    assert posthog.capture.call_count == expected.capture_calls


def test_strip_indent():
    """Sanity check before using in tests"""
    assert strip_indent("\n  foo\n  bar\n  baz\n") == "foo\nbar\nbaz"
    assert strip_indent("\n  foo\n    bar\n  baz\n") == "foo\n  bar\nbaz"
    assert strip_indent("\n  foo\n  bar\nbaz\nba\n") == "foo\nbar\nz\n"  # known limitation


def test_load_v0(posthog):
    raw_config = f"""
    server: {Expected.server}
    token: {Expected.token}
    """
    assert_config(
        posthog,
        raw_config,
        Expected(
            identify_calls=1,
            capture_calls=2,
        ),
        config_path=c.LEGACY_CONFIG_PATH,
    )


def test_upgrade_v1(posthog):
    raw_config = f"""
    server: {Expected.server}
    token: {Expected.token}
    version: 1
    """
    assert_config(
        posthog,
        raw_config,
        Expected(
            identify_calls=1,
            capture_calls=2,
        ),
        config_path=c.LEGACY_CONFIG_PATH,
    )


def test_upgrade_v2(posthog):
    raw_config = f"""
    server: {Expected.server}
    session_id: {Expected.session_id}
    token: {Expected.token}
    username: 'datapane-test'
    version: 2
    """
    assert_config(
        posthog,
        raw_config,
        Expected(
            identify_calls=1,
            capture_calls=2,
        ),
        config_path=c.LEGACY_CONFIG_PATH,
    )


def test_upgrade_v3(posthog):
    raw_config = f"""
    completed_action: false
    server: {Expected.server}
    session_id: {Expected.session_id}
    token: {Expected.token}
    username: datapane-test
    version: 3
    """
    assert_config(
        posthog,
        raw_config,
        Expected(
            identify_calls=1,
            capture_calls=2,
        ),
        config_path=c.LEGACY_CONFIG_PATH,
    )


def test_upgrade_v3_completed(posthog):
    raw_config = f"""
    completed_action: true
    server: {Expected.server}
    session_id: {Expected.session_id}
    token: {Expected.token}
    username: datapane-test
    version: 3
    """
    assert_config(
        posthog,
        raw_config,
        Expected(
            identify_calls=0,
            capture_calls=0,
        ),
        config_path=c.LEGACY_CONFIG_PATH,
    )


def test_upgrade_v4(posthog):
    raw_config = f"""
    _env: null
    _path: null
    completed_action: true
    email: {Expected.email}
    server: {Expected.server}
    session_id: {Expected.session_id}
    token: {Expected.token}
    version: 4
    """
    assert_config(
        posthog,
        raw_config,
        Expected(
            identify_calls=0,
            capture_calls=0,
        ),
        config_path=c.LEGACY_CONFIG_PATH,
    )


raw_config_v5 = f"""
# server API address
server: {Expected.server}
# API token - copy and paste from https://server/settings/
token: {Expected.token}
email: {Expected.email}
session_id: {Expected.session_id}
version: 5
completed_action: false
"""


def test_load_v5(posthog):
    assert_config(
        posthog,
        raw_config_v5,
        Expected(
            identify_calls=0,
            capture_calls=0,
            completed_action=False,
        ),
        config_path=c.LEGACY_CONFIG_PATH,
    )


def test_load_legacy_yaml__replaces_with_ini():
    """
    Check the default.yaml is cleanly migrated to config.ini
    """
    write_config(raw_config_v5, config_path=c.LEGACY_CONFIG_PATH)
    c.Config.load()
    assert not c.LEGACY_CONFIG_PATH.exists()
    assert c.CONFIG_PATH.exists()

    # Check the ini looks right
    raw = c.CONFIG_PATH.read_text()
    assert raw.startswith(f"[{c.CONFIG_SECTION}]\n")


raw_config_v6 = f"""
[{c.CONFIG_SECTION}]
server = {Expected.server}
token = {Expected.token}
email = {Expected.email}
session_id = {Expected.session_id}
version = 6
completed_action = False
"""


def test_load_v6(posthog):
    assert_config(posthog, raw_config_v6, Expected(identify_calls=0, capture_calls=0, completed_action=False))


def test_new_config__pre_invariants(posthog):
    c.init()
    config = c.config
    assert isinstance(config, c.Config)
    assert_config_object(
        posthog,
        config,
        Expected(
            identify_calls=0,
            capture_calls=0,
            server=c.DEFAULT_SERVER,
            token=c.DEFAULT_TOKEN,
            email="",
            completed_action=False,
        ),
    )


def test_new_config__login_event(posthog):
    c.init()
    email = dp.login(token=Expected.token)
    assert email == Expected.email
    assert isinstance(c.config, c.Config)
    assert_config_object(
        posthog,
        c.config,
        expected=Expected(identify_calls=1, capture_calls=2, server=c.DEFAULT_SERVER),
    )

    config = c.Config.load()
    assert_config_object(posthog, config, expected=Expected(identify_calls=1, capture_calls=2, server=c.DEFAULT_SERVER))


@pytest.mark.skipif("CI" in os.environ, reason="depends on fe-components - only run locally")
def test_new_config__additional_event(posthog, monkeypatch, tmp_path):
    # Log in
    test_new_config__login_event(posthog)

    monkeypatch.chdir(tmp_path)
    from tests.client.local.api.test_reports import gen_report_simple

    report = gen_report_simple()
    report.save(path="test_out.html", name="My Wicked Report", author="Datapane Team")
    assert posthog.identify.call_count == 1
    assert posthog.capture.call_count == 3
