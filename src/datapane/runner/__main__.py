import argparse
import os
import pwd
import sys
import traceback
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, TextIO, Tuple

import datapane.client.api.common
from datapane import __version__
from datapane.client import api
from datapane.client import config as c
from datapane.common import log
from datapane.common.config import RunnerConfig, decode
from datapane.common.versioning import version_check

from .exceptions import ModelRunError
from .typedefs import ErrorResult, RunResult


def setup_api(dp_host: str, dp_token: str, debug: bool = False, logs: TextIO = None):
    """Init the Datapane API for automated use"""
    # setup input and config
    # login, etc.
    config = c.Config(server=dp_host, token=dp_token, analytics=False)
    # datapane.init(stream_logs, verbose=args.debug)
    api.init(config=config, debug=debug, logs_stream=logs)
    # check can login/ping
    r = datapane.client.api.common.check_login()
    log.debug(f"Running DP on DP as {r.username}")


def run_api(run_config: RunnerConfig) -> RunResult:
    """Bootstrap the recursive calls into run"""
    script = api.Script.by_id(run_config.script_id)
    # is the script compatible with the client runner/api
    version_check(__version__, script.api_version)

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
ENV_WHITELIST = ("LANG", "PATH", "HOME", "PYTHON_VERSION", "PYTHONPATH")
USER_USER = "usercode"


def make_env(
    input_env: Mapping[str, str], allowed: Iterable[str] = ENV_WHITELIST
) -> Dict[str, str]:

    return {k: input_env[k] for k in allowed if k in input_env}


# TODO - do we still need this??
def drop_privileges(uid_name="nobody", gid_name="nogroup"):
    import grp

    # from: https://stackoverflow.com/questions/2699907/dropping-root-permissions-in-python
    if os.getuid() != 0:
        return

    # Get the uid/gid from the name
    running_uid = pwd.getpwnam(uid_name).pw_uid
    running_gid = grp.getgrnam(gid_name).gr_gid

    # Remove group privileges
    os.setgroups([])

    # Try setting the new uid/gid
    os.setgid(running_gid)
    os.setuid(running_uid)

    # Ensure a very conservative umask
    os.umask(0o77)


def preexec():
    # NOTE - do we still need this??
    drop_privileges(USER_USER, USER_USER)


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
    preexec()
    retcode: int

    with (out_dir / "logs.txt").open("w") as stream_logs, (out_dir / "results.json").open(
        "w"
    ) as results_stream:
        try:
            # check cli compatible with server
            if args.server_version:
                version_check(args.server_version, __version__)

            # read the config files
            # NOTE - we could supply config also by env-var or already write k8s volume in the future
            run_config = decode(args.config, compressed=True)
            setup_api(args.dp_host, args.dp_token, args.debug, stream_logs)
            res = run_api(run_config)
        except ModelRunError as e:
            ErrorResult(error=e.error, error_detail=e.details).to_json(results_stream)
            retcode = 103  # NOTE - all user errors return 103
        except Exception:
            log.exception("Unhandled Exception in Model Runner")
            # we could send traceback as details, but not useful to end user
            ErrorResult(error="Unhandled Exception", debug=traceback.format_exc()).to_json(
                results_stream
            )
            retcode = 104
        else:
            res.to_json(results_stream)
            retcode = 0

    sys.exit(retcode)


if __name__ == "__main__":
    main()
