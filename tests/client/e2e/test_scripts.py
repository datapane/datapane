# flake8: noqa isort:skip
import tarfile
import time
from pathlib import Path

import pytest

import datapane as dp
from datapane.client import scripts as sc
from datapane.client.api import HTTPError

from .common import deletable, gen_name

pytestmark = pytest.mark.usefixtures("dp_login")


@pytest.mark.org
def test_script_basic(shared_datadir: Path, monkeypatch):
    """Deploying and running a basic report-generating script"""
    monkeypatch.chdir(shared_datadir)
    # upload
    name = gen_name()
    dp_cfg = sc.DatapaneCfg.create_initial()
    with sc.build_bundle(dp_cfg) as sdist:
        s = dp.Script.upload_pkg(sdist, dp_cfg, name=name)

    with deletable(s):
        # are fields added?
        assert s.name == name

        # download and check the import was as expected
        assert s.script == dp_cfg.script.name
        sdist_file = s.download_pkg()
        # look into files
        tar = tarfile.open(sdist_file)
        assert "dp_script.py" in tar.getnames()

        ########################################################################
        # Test running
        # no need to test obj lookup (covered by other tests)
        # basic report gen
        params = dict(p1="A")

        run = s.run(parameters=params)
        while not run.is_complete():
            time.sleep(2)
            run.refresh()
        assert run.status == "SUCCESS"

        with deletable(dp.Report.by_id(run.report)) as report:
            assert report.web_url

        ########################################################################
        # Test scheduling
        cron1 = "00 00 * * SUN"
        cron2 = "00 00 * * SAT"

        # create schedule, update, and delete - we don't run atm
        with deletable(dp.Schedule.create(s, cron1, params)) as s1:
            assert s1.cron == cron1
            s1.update(cron=cron2)
            assert s1.cron == cron2


@pytest.mark.org
def test_script_complex(shared_datadir: Path, monkeypatch):
    """Deploy and run a complex script with no report and multiple params"""
    monkeypatch.chdir(shared_datadir)
    # upload
    dp_cfg = sc.DatapaneCfg.create_initial(config_file=Path("dp_test_mod.yaml"))

    with sc.build_bundle(dp_cfg) as sdist:
        s = dp.Script.upload_pkg(sdist, dp_cfg)

    with deletable(s):
        assert "datapane-demos" in s.repo
        assert len(s.requirements) == 1
        assert "pytil" in s.requirements

        # attempt run with missing required param `p2`
        with pytest.raises(HTTPError) as _:
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
        assert "SAMPLE OUTPUT" in run.output


@pytest.mark.org
def test_script_complex_report(shared_datadir: Path, monkeypatch):
    """
    Deploy and run a complex script that generates a complex report
    NOTE - this doesn't test the FE rendering
    """
    monkeypatch.chdir(shared_datadir)
    # upload
    dp_cfg = sc.DatapaneCfg.create_initial(config_file=Path("dp_complex_report.yaml"))

    with sc.build_bundle(dp_cfg) as sdist:
        s = dp.Script.upload_pkg(sdist, dp_cfg)

    with deletable(s):
        run = s.run()
        # poll until complete
        while not run.is_complete():
            time.sleep(2)
            run.refresh()

        assert run.status == "SUCCESS"
        report = dp.Report.by_id(run.report)
        assert report.num_blocks == 11


@pytest.mark.org
def test_run_linked_script():
    """Test running a code snippet calling other ones"""
    ...
