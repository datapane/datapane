from pathlib import Path

from click.testing import CliRunner, Result

from datapane.client.commands import cli
from datapane.client.utils import process_cmd_param_vals

# TODO
#  - add tests for other commands
#  - add fixture to handle login
#  - use proper test user


def handle_res(r: Result):
    if r.exception:
        print(r.output)
        raise r.exception
    assert r.exit_code == 0


def test_report_init(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    runner = CliRunner()
    result = runner.invoke(cli, ["-vv", "report", "init"])
    handle_res(result)


def test_script_init(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    runner = CliRunner()
    result = runner.invoke(cli, ["-vv", "script", "init"])
    handle_res(result)


def test_cli_params():
    p1 = ("w=hello", "x=1", "y=3.2", "z=true")
    expected1 = {"w": "hello", "x": 1, "y": 3.2, "z": True}
    assert process_cmd_param_vals(p1) == expected1
