# flake8: noqa isort:skip
import os
import sys
from pathlib import Path
from unittest import mock
import subprocess

import pytest

if not (sys.platform == "linux" and sys.version_info.minor >= 7):
    pytest.skip("skipping linux-only 3.7+ tests", allow_module_level=True)

import datapane as dp
from datapane.client.api.runtime import _report
from datapane.client.scripts import build_bundle, DatapaneCfg
from datapane.common.config import RunnerConfig
from datapane.common import SDict, SSDict
from datapane.runner import __main__ as m
from datapane.runner.exec_script import exec_mod
from datapane.runner.typedefs import RunResult

# disabled for now - may re-enable when we support local
# running/rendering with our runner calling into user code
pytestmark = pytest.mark.skipif(
    not (sys.platform == "linux" and sys.version_info.minor >= 7),
    reason="Only supported on Linux/py3.7+",
)


def test_make_env():
    res = m.make_env(os.environ)
    assert "PATH" in res
    assert "PWD" not in res


def test_exec(datadir: Path, monkeypatch, capsys):
    """Test running an isolated code snippet"""
    monkeypatch.chdir(datadir)

    res = exec_mod(Path("sample_module.py"), init_state={"x": 4})
    # print(res)
    assert "x" in res
    assert res["x"] == 4
    assert res["y"] == 4
    assert res["foo"]() == "my_df"
    # run_path makes res static due to sandboxing
    # module is no longer "alive", it's a script that's finished executing
    assert res["y"] != 5
    assert res["__name__"] == "__datapane__"
    (out, err) = capsys.readouterr()
    assert out == "x is 4\nin foo\nmy_df\n5\n"


class MockScript(dp.Script):
    """Use custom mock class to disable constructor but keep other methods"""

    script = ""
    id = "a"
    requirements = ["pytil"]
    pre_commands = ["echo PRE1", "echo PRE2"]
    post_commands = ["echo POST1", "echo POST2"]
    api_version = dp.__version__

    def __init__(self, *a, **kw):
        pass

    @classmethod
    def get(cls, *a, **kw):
        return cls()

    @classmethod
    def by_id(cls, id_or_url: str):
        return cls()


def mock_report_upload(self, **kwargs):
    """Mock creating a report object"""
    report = mock.Mock()
    report.id = "ABC"
    _report.append(report)
    return mock.DEFAULT


@mock.patch("datapane.client.api.Script", new=MockScript)
def _runner(params: SDict, env: SSDict, script: Path, sdist: Path = Path(".")) -> RunResult:
    with mock.patch.object(MockScript, "script", new_callable=mock.PropertyMock) as ep, mock.patch.object(
        MockScript, "download_pkg"
    ) as dp:
        # setup script object
        ep.return_value = script
        dp.return_value = sdist

        # main fn
        x = RunnerConfig(script_id="ZBAmDk1", config=params, env=env)
        res = m.run_api(x)
        return res


# TODO - fix exception handling stacktraces
@mock.patch("datapane.runner.exec_script.setup_script", autospec=True)
@mock.patch("datapane.client.api.Report.upload", autospec=True, side_effect=mock_report_upload)
def test_run_single_script(rc, isc, datadir: Path, monkeypatch, capfd):
    """Test running an isolated code snippet with params
    NOTE - we can simplify by calling exec_script.run directly, doesn't test as much of API however
    """
    monkeypatch.chdir(datadir)
    # monkeypatch.setenv("DATAPANE_ON_DATAPANE", "true")
    monkeypatch.setenv("DATAPANE_BY_DATAPANE", "true")
    monkeypatch.setenv("ENV_VAR", "env value")

    @mock.patch("datapane.runner.exec_script.script_env", autospec=True)
    def f(val: str, script_env):
        # test twice to ensure stateful params are handled correctly
        res = _runner({"p1": val}, {"ENV_VAR": "env_value"}, Path("dp_script.py"))
        # (out, err) = capsys.readouterr()
        (out, err) = capfd.readouterr()
        assert "on datapane" not in out
        assert "by datapane" in out
        # asserts
        isc.assert_called()
        (rc_args, rc_kwargs) = rc.call_args
        assert rc_kwargs["description"] == "Description"
        _r: dp.Report = rc_args[0]
        _blocks = _r.pages[0].blocks[0].blocks
        assert isinstance(_blocks, list)
        assert len(_blocks) == 3
        assert val in _blocks[0].content
        assert res.report_id == "ABC"
        # pre/post commands
        assert "PRE2" in out
        assert "POST2" in out

    f("HELLO")
    f("WORLD")


@mock.patch("datapane.client.api.Report.upload", autospec=True, side_effect=mock_report_upload)
def test_run_bundle(rc, datadir: Path, monkeypatch, capsys):
    monkeypatch.chdir(datadir)
    # monkeypatch.setenv("DATAPANE_ON_DATAPANE", "true")
    monkeypatch.setenv("DATAPANE_BY_DATAPANE", "true")

    # TODO - we should prob use a pre-built sdist here...
    dp_config = DatapaneCfg.create_initial(config_file=Path("dp_test_mod.yaml"))
    with build_bundle(dp_config) as sdist:
        # whl_file = build_bundle(dp_config, sdist, shared_datadir, username="test", version=1)
        try:
            # NOTE - need to pass in all params as we're not setting defaults via dp-server
            res = _runner(
                {"p1": "VAL", "p2": "xyz", "p3": True}, {"ENV_VAR": "env_value"}, dp_config.script, sdist=sdist
            )
        finally:
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "--yes", "pytil"], check=True)
    # asserts
    (out, err) = capsys.readouterr()
    assert "ran script" in out
    assert "p2=xyz" in out
    assert "WORLD" in out
    assert dp.Result.get() == "hello , world!"
    assert res.report_id is None
