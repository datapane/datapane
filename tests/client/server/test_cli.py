from pathlib import Path

import pytest
from click.testing import CliRunner

from datapane.client.commands import cli

from ..local.test_cli import handle_res
from .conftest import TEST_SERVER, TEST_TOKEN


@pytest.fixture()
def runner():
    _runner = CliRunner()
    result = _runner.invoke(
        cli, ["--debug", "login", "--token", TEST_TOKEN, "--server", TEST_SERVER]
    )
    handle_res(result)
    assert "Logged in" in result.output
    return _runner


def test_auth(runner: CliRunner):
    # ping
    result = runner.invoke(cli, ["--debug", "ping"])
    handle_res(result)
    assert "Connected to" in result.output

    # log out
    result = runner.invoke(cli, ["--debug", "logout"])
    handle_res(result)
    assert "Logged out" in result.output


def test_cli_script(runner: CliRunner, tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    r = runner.invoke(cli, ["--debug", "script", "init"])
    handle_res(r)
    script_name = "test_script"
    r = runner.invoke(cli, ["--debug", "script", "deploy", script_name])
    handle_res(r)

    if "Uploaded" in r.output:
        r = runner.invoke(cli, ["--debug", "script", "run", script_name, "--wait"])
        handle_res(r)

        r = runner.invoke(cli, ["--debug", "script", "delete", script_name])
        handle_res(r)
