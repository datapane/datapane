"""Setup/remove all the test objects for cypress"""
import argparse
import json
import os
import pickle
from contextlib import suppress
from pathlib import Path

import datapane as dp
from datapane.client import config as c
from datapane.client.commands import gen_name

# login to server
c.set_config(c.Config(server=os.environ["DP_TEST_SERVER"], token=os.environ["DP_TEST_TOKEN"]))


def setup(file: Path, test_org: bool):
    """Create the cypress test objects"""
    print("Building test reports / apps")

    # demo reports
    style_report = dp.builtins.build_demo_report()
    style_report.upload(name="CYPRESS-STYLE-REPORT", description="DESCRIPTION")

    dp_objs = {"styleReportURL": style_report.web_url}

    # add a basic file
    if test_org:
        # file
        obj = {"foo": "bar"}
        obj_file = dp.File.upload_obj(data=pickle.dumps(obj), name=gen_name())
        # record obj urls
        dp_objs.update({"fileURL": obj_file.web_url})

    # write to tmp file for cypress tests to pick up
    file.write_text(json.dumps(dp_objs))


def teardown(file: Path, test_org: bool):
    """Delete the cypress test objects"""
    print("Deleting test reports / apps")
    # read the urls from stdin
    dp_objs: dict = json.loads(file.read_text())

    # delete the objects, ignoring errors
    with suppress(Exception):
        dp.App.by_id(dp_objs["styleReportURL"]).delete()
    if test_org:
        with suppress(Exception):
            dp.File.by_id(dp_objs["fileURL"]).delete()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup system for cypress tests")
    parser.add_argument("--teardown", action="store_true")
    parser.add_argument("--org", action="store_true")
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    teardown(args.file, args.org) if args.teardown else setup(args.file, args.org)
