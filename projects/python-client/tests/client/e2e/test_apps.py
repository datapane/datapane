import tarfile
import time
from pathlib import Path

import pytest

import datapane as dp
from datapane.client import apps as sc
from datapane.client.api import HTTPError

from .common import check_name, deletable, gen_name

# pytestmark = pytest.mark.usefixtures("dp_login")
pytestmark = pytest.mark.skip("LeagacyApp tests disabled")

# TODO: FIX TEST TO USE ENVIRONMENT VALUE FROM ENVIRONMENT OBJECT


@pytest.mark.org
@pytest.mark.timeout(5 * 60)  # allow 5m
def test_app_basic(shared_datadir: Path, monkeypatch):
    """Deploying and running a basic report-generating app"""
    monkeypatch.chdir(shared_datadir)
    # upload
    name = gen_name("app")
    dp_cfg = sc.DatapaneCfg.create_initial()
    env_name = gen_name("env")
    with deletable(dp.Environment.create(name=env_name, environment={"ENV_VAR": "env_value"}, overwrite=True)):
        with sc.build_bundle(dp_cfg) as sdist:
            s = dp.LegacyApp.upload_pkg(sdist, dp_cfg, name=name, environment=env_name)

        with deletable(s):
            # are fields added?
            check_name(s, name)

            # download and check the import was as expected
            assert s.script == dp_cfg.script.name
            sdist_file = s.download_pkg()
            # look into files
            tar = tarfile.open(sdist_file)
            assert dp_cfg.script.name in tar.getnames()

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

            with deletable(dp.App.by_id(run.report)) as report:
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
@pytest.mark.timeout(5 * 60)  # allow 5m
def test_app_complex(shared_datadir: Path, monkeypatch):
    """Deploy and run a complex app with no report and multiple params"""
    monkeypatch.chdir(shared_datadir)
    # upload
    dp_cfg = sc.DatapaneCfg.create_initial(config_file=Path("dp_test_mod.yaml"))
    env_name = "ENV"

    with deletable(dp.Environment.create(name=env_name, environment={"ENV_VAR": "env_value"}, overwrite=True)):
        with sc.build_bundle(dp_cfg) as sdist:
            s = dp.LegacyApp.upload_pkg(sdist, dp_cfg, environment=env_name)

        with deletable(s):
            assert "datapane-demos" in s.source_url
            assert len(s.requirements) == 1
            assert "pytil" in s.requirements

            # attempt run with missing required param `p2`
            with pytest.raises(HTTPError) as _:
                _ = s.run(parameters=dict(p1="A"))

            run = s.run(parameters=dict(p1="A", p2=1))
            assert run.app == s.url
            assert "p2" in run.parameter_vals
            assert run.status == "RUNNING"

            # poll until complete
            while not run.is_complete():
                time.sleep(2)
                run.refresh()

            # TODO - look for `on_datapane` in stdout
            assert run.status == "SUCCESS"
            assert run.report is None
            assert run.result == "hello , world!"
            assert "SAMPLE OUTPUT" in run.output
            assert "ENV_VAR=env_value" in run.output
            assert "p2=1" in run.output


# TODO: Fix this test after adding dp.Media block to report
@pytest.mark.org
@pytest.mark.timeout(5 * 60)  # allow 5m
def test_app_complex_report(shared_datadir: Path, monkeypatch):
    """
    Deploy and run a complex app that generates a complex report
    NOTE - this doesn't test the FE rendering
    """
    monkeypatch.chdir(shared_datadir)
    # upload
    dp_cfg = sc.DatapaneCfg.create_initial(config_file=Path("dp_complex_report.yaml"))
    env_name = "ENV"
    with deletable(dp.Environment.create(name=env_name, environment={"ENV_VAR": "env_value"}, overwrite=True)):
        with sc.build_bundle(dp_cfg) as sdist:
            s = dp.LegacyApp.upload_pkg(sdist, dp_cfg, environment=env_name, overwrite=True)

        with deletable(s):
            run = s.run()
            # poll until complete
            while not run.is_complete():
                time.sleep(2)
                run.refresh()

            assert run.status == "SUCCESS"
            report = dp.App.by_id(run.report)
            assert report.num_blocks == 11


@pytest.mark.org
def test_run_linked_app():
    """Test running a code snippet calling other ones"""
    pass
