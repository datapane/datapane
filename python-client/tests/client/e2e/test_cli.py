from pathlib import Path

import pytest
from click.testing import CliRunner

from datapane.client.commands import cli

from ..local.test_cli import handle_res
from .common import gen_name
from .conftest import TEST_SERVER, TEST_TOKEN


@pytest.fixture()
def runner():
    # NOTE - this will overwrite the default config profile and logging conf - not an issue on CI
    _runner = CliRunner()
    result = _runner.invoke(cli, ["-vv", "login", "--token", TEST_TOKEN, "--server", TEST_SERVER])
    handle_res(result)
    assert "Connected successfully" in result.output
    return _runner


def test_auth(runner: CliRunner):
    # ping
    result = runner.invoke(cli, ["-vv", "ping"])
    handle_res(result)
    assert "Connected successfully" in result.output

    # log out
    result = runner.invoke(cli, ["-vv", "logout"])
    handle_res(result)
    assert "Logged out" in result.output


@pytest.mark.skip("LeagacyApp tests disabled")
@pytest.mark.org
@pytest.mark.timeout(5 * 60)  # allow 5m
def test_cli_app(runner: CliRunner, tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    r = runner.invoke(cli, ["-vv", "app", "init"])
    handle_res(r)
    app_name = gen_name()
    r = runner.invoke(cli, ["-vv", "app", "deploy", "--name", app_name])
    handle_res(r)

    if "Uploaded" in r.output:
        r = runner.invoke(cli, ["-vv", "app", "run", app_name, "--wait"])
        handle_res(r)

        r = runner.invoke(cli, ["-vv", "app", "delete", app_name])
        handle_res(r)
