import pytest
from click.testing import CliRunner

from datapane.client.commands import cli

from ..local.test_cli import handle_res
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
