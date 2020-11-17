# Copyright 2020 StackHut Limited (trading as Datapane)
# SPDX-License-Identifier: Apache-2.0

import argparse
import os
import pwd
import sys
import traceback
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, TextIO, Tuple

from datapane import __version__
from datapane.client import api
from datapane.common import _setup_dp_logging, log
from datapane.common.config import RunnerConfig, decode
from datapane.common.versioning import is_version_compatible

from .exceptions import ModelRunError
from .typedefs import ErrorResult, RunResult


def setup_api(dp_token: str, dp_host: str, debug: bool = False, logs: TextIO = None):
    """Init the Datapane API for automated use"""
    # login, ping, and create the default env file for CMD usage
    api.login(token=dp_token, server=dp_host, cli_login=False)
    # setup input and config, logging, login, etc.
    verbosity = 2 if debug else 0
    _setup_dp_logging(verbosity=verbosity, logs_stream=logs)
    log.debug("Running DP on DP")


def run_api(run_config: RunnerConfig) -> RunResult:
    """Bootstrap the recursive calls into run"""
    script = api.Script.by_id(run_config.script_id)
    # is the script compatible with the client runner/api
    if not is_version_compatible(__version__, script.api_version, raise_exception=False):
        log.warning(
            f"Script developed for an older version of Datapane ({script.api_version}) - "
            + "this run may fail, please update."
        )

    # TODO - we should pull param defaults from script and add in the call
    script.call(**run_config.format())

    # create the RunResult
    script_result = str(api.Result.get()) if api.Result.exists() else None
    report_id = None
    try:
        report = api._report.pop()
        log.debug(f"Returning report id {report.id}")
        report_id = report.id
    except IndexError:
        log.debug("User script didn't generate report - perhaps result / action only")

    return RunResult(report_id=report_id, script_result=script_result)


# ensure we copy PYTHONPATH across
ENV_ALLOWLIST = ("LANG", "PATH", "HOME", "PYTHON_VERSION", "PYTHONPATH")


def make_env(input_env: Mapping[str, str], allowed: Iterable[str] = ENV_ALLOWLIST) -> Dict[str, str]:
    return {k: input_env[k] for k in allowed if k in input_env}


def drop_privileges(out_dir: Path, uid_name: str = "nobody", gid_name: str = "nogroup") -> None:
    """Drop to non-root user if required. TODO - do we still need this??"""
    import grp
    import subprocess

    # from: https://stackoverflow.com/questions/2699907/dropping-root-permissions-in-python
    if os.getuid() != 0:
        return

    try:
        # Get the uid/gid from the name
        running_uid = pwd.getpwnam(uid_name).pw_uid
        running_gid = grp.getgrnam(gid_name).gr_gid

        # chown the output dir
        subprocess.run(["chown", "-R", f"{uid_name}:{gid_name}", str(out_dir)], check=True)

        # Remove group privileges
        os.setgroups([])

        # Try setting the new uid/gid
        os.setgid(running_gid)
        os.setuid(running_uid)

        # Ensure a very conservative umask
        os.umask(0o77)
    except Exception:
        log.warning("Error dropping privileges to non-root user, continuing")


def preexec(out_dir: Path):
    # Currently disabled as unsure how will react with 3rd-party libs, e.g. boto, etc.
    # drop_privileges(out_dir)
    pass


def parse_args(argv: Optional[List[str]] = None) -> Tuple[argparse.Namespace, List[str]]:
    # TODO - min version param
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", default=False, help="Enable debug output")
    parser.add_argument("--config", required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--dp-host", required=True)
    parser.add_argument("--dp-token", required=True)
    parser.add_argument("--server-version")
    return parser.parse_known_args(argv)


def main():
    args, unknown_args = parse_args()

    out_dir: Path = args.out_dir
    preexec(out_dir)
    retcode: int

    with (out_dir / "logs.txt").open("w") as stream_logs, (out_dir / "results.json").open("w") as results_stream:
        try:
            # check cli compatible with server - should never really fail
            if args.server_version:
                is_version_compatible(args.server_version, __version__)

            # read the config files
            # NOTE - we could supply config also by env-var or already write k8s volume in the future
            run_config = decode(args.config, compressed=True)
            setup_api(args.dp_token, args.dp_host, args.debug, stream_logs)
            res = run_api(run_config)
        except ModelRunError as e:
            ErrorResult(error=e.error, error_detail=e.details).to_json(results_stream)
            retcode = 103  # NOTE - all user errors return 103
        except Exception:
            log.exception("Unhandled Exception in Model Runner")
            # we could send traceback as details, but not useful to end user
            ErrorResult(error="Unhandled Exception", debug=traceback.format_exc()).to_json(results_stream)
            retcode = 104
        else:
            res.to_json(results_stream)
            retcode = 0

    sys.exit(retcode)


if __name__ == "__main__":
    main()
