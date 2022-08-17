"""Setup/remove all the test objects for cypress"""
import argparse
import json
import os
import pickle
import sys
from contextlib import suppress
from pathlib import Path

import datapane as dp
from datapane.client import apps as sc
from datapane.client import config as c
from datapane.client.commands import gen_name
from datapane.common.utils import pushd

# login to server
c.set_config(c.Config(server=os.environ["DP_TEST_SERVER"], token=os.environ["DP_TEST_TOKEN"]))


def setup(test_org: bool):
    """Create the cypress test objects"""
    print("Building test reports / apps")

    # demo reports
    style_report = dp.builtins.build_demo_report()
    style_report.upload(name="CYPRESS-STYLE-REPORT", description="DESCRIPTION")

    dp_objs = {"styleReportURL": style_report.web_url}

    def get_test_app(name: str) -> dp.App:
        with pushd(Path(".") / "tests" / "cypress_test_app"):
            dp_cfg = sc.DatapaneCfg.create_initial(config_file=Path(f"{name}.yaml"), script=Path(f"{name}.py"))
            with sc.build_bundle(dp_cfg) as sdist:
                app = dp.App.upload_pkg(sdist, dp_cfg, name=gen_name())
        return app

    # add a basic app and file
    if test_org:
        # apps
        params_app = get_test_app("dp_test_cypress")
        no_params_app = get_test_app("dp_test_cypress_noparams")
        # file
        obj = {"foo": "bar"}
        obj_file = dp.File.upload_obj(data=pickle.dumps(obj), name=gen_name())
        # record obj urls
        dp_objs.update(
            {"paramsAppURL": params_app.web_url, "noParamsAppURL": no_params_app.web_url, "fileURL": obj_file.web_url}
        )

    # write to stderr for cypress tests to pick up
    print(json.dumps(dp_objs), flush=True, file=sys.stderr)


def teardown(test_org: bool):
    """Delete the cypress test objects"""
    print("Deleting test reports / apps")
    # read the urls from stdin
    dp_objs: dict = json.load(sys.stdin)

    # delete the objects, ignoring errors
    with suppress(Exception):
        dp.Report.by_id(dp_objs["styleReportURL"]).delete()
    if test_org:
        with suppress(Exception):
            dp.App.by_id(dp_objs["paramsAppURL"]).delete()
        with suppress(Exception):
            dp.App.by_id(dp_objs["noParamsAppURL"]).delete()
        with suppress(Exception):
            dp.File.by_id(dp_objs["fileURL"]).delete()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup system for cypress tests")
    parser.add_argument("--teardown", action="store_true")
    parser.add_argument("--org", action="store_true")
    args = parser.parse_args()
    teardown(args.org) if args.teardown else setup(args.org)
