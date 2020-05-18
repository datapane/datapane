# flake8: noqa isort:skip
import tarfile
import time
from typing import Optional
from pathlib import Path

import pytest

import datapane as dp
from datapane.client import api
from datapane.common import scripts as sc

from .common import gen_name

pytestmark = pytest.mark.usefixtures("dp_login")


def test_script_basic(shared_datadir: Path, monkeypatch):
    """Deploying and running a basic report-generating script"""
    monkeypatch.chdir(shared_datadir)
    s: Optional[dp.Script] = None
    report: Optional[dp.Report] = None
    try:

        # upload
        name = gen_name()
        dp_cfg = sc.DatapaneCfg.create_initial()
        with sc.build_bundle(dp_cfg) as sdist:
            s = dp.Script.upload_pkg(sdist, dp_cfg, name=name)

        # are fields added?
        assert s.name == name

        # download and check the import was as expected
        assert s.script == dp_cfg.script.name
        sdist_file = s.download_pkg()
        # look into files
        tar = tarfile.open(sdist_file)
        assert "dp_script.py" in tar.getnames()

        # no need to test obj lookup (covered by other tests)
        # basic report gen
        run = s.run(parameters=dict(p1="A"))
        while not run.is_complete():
            time.sleep(2)
            run.refresh()
        assert run.status == "SUCCESS"
        report = dp.Report.get(id_or_url=run.report)
        assert report.web_url
    finally:
        if report:
            report.delete()
        if s:
            s.delete()
            with pytest.raises(api.HTTPError) as _:
                _ = dp.Script(s.name)


def test_script_complex(shared_datadir: Path, monkeypatch):
    """Deploy and run a complex script with no report and multiple params"""
    monkeypatch.chdir(shared_datadir)
    s: Optional[dp.Script] = None
    try:
        # upload
        dp_cfg = sc.DatapaneCfg.create_initial(config_file=Path("dp_test_mod.yaml"))

        with sc.build_bundle(dp_cfg) as sdist:
            s = dp.Script.upload_pkg(sdist, dp_cfg)

        assert "datapane-demos" in s.repo
        assert len(s.requirements) == 1
        assert "pytil" in s.requirements

        # attempt run with missing required param `p2`
        with pytest.raises(api.HTTPError) as _:
            _ = s.run(parameters=dict(p1="A"))

        run = s.run(parameters=dict(p1="A", p2=1))
        assert run.script == s.url
        assert "p2" in run.parameter_vals
        assert run.status == "QUEUED"

        # poll until complete
        while not run.is_complete():
            time.sleep(2)
            run.refresh()

        # TODO - look for `on_datapane` in stdout
        assert run.status == "SUCCESS"
        assert run.report is None
        assert run.result == "hello , world!"
    finally:
        if s:
            s.delete()
            with pytest.raises(api.HTTPError) as _:
                _ = dp.Script(s.name)


def test_run_linked_script():
    """Test running a code snippet calling other ones"""
    ...
