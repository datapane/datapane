from pathlib import Path

from click.testing import CliRunner, Result

from datapane import __version__
from datapane.client.commands import cli, process_cmd_param_vals
from datapane.common.utils import pushd

# TODO
#  - add tests for other commands
#  - add fixture to handle login
#  - use proper test user


def handle_res(r: Result):
    if r.exception:
        print(r.output)
        raise r.exception
    assert r.exit_code == 0


def test_version():
    assert __version__ == "0.0.1"


def test_init(tmp_path: Path):
    runner = CliRunner()

    with pushd(tmp_path):
        result = runner.invoke(cli, ["--debug", "script", "init"])

    handle_res(result)


def test_cli_params():
    p1 = ("w=hello", "x=1", "y=3.2", "z=true")
    expected1 = {"w": "hello", "x": 1, "y": 3.2, "z": True}
    assert process_cmd_param_vals(p1) == expected1
