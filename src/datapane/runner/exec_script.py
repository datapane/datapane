import ast
import builtins
import compileall
import importlib
import os
import runpy
import shutil
import subprocess
import sys
import tarfile
import typing as t
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from types import FrameType
from typing import List, Optional

import datapane.client.api as api
from datapane.common import SDict, log

from .exceptions import CodeError, CodeRaisedError, CodeSyntaxError

ENVIRON_CONFIG = {
    "banned_builtins": {"compile", "exec", "eval"},
    "default_environment": [],
}
RUN_NAME = "__datapane__"  # <datapane> ??


def run(script: api.Script, user_config: SDict) -> SDict:
    """Run a datapane python script/module"""
    api._reset_runtime(params=user_config)

    # use the script id for unique, isolated dir per script
    env_dir = Path(script.id)
    setup_script(script, env_dir)

    with script_env(env_dir):
        # script_name = str(script.script) ## <module> ?
        try:
            # run script in unpacked dir wrapped around pre/post-commands
            run_commands(script.pre_commands)
            res_scope = exec_mod(script.script)
            run_commands(script.post_commands)
            return res_scope
        except SyntaxError:
            raise CodeSyntaxError.from_exception()
        except Exception:
            raise CodeRaisedError.from_exception(partial(filter_frame_by_filename, "<module>"))


# OBSOLETE
# def run(run_config: RunnerConfig) -> List[api.ReportBlock]:
#     """Snippet - run a python function embedded within in the snippet config field"""
#     code = run_config.code
#     user_config: SDict = Munch.fromDict(run_config.format())
#     # call to_df locally
#     # convert to dfs if needed
#     # dp._snippet_init(config=user_config)
#
#     # NOTE(MG): currently just exec the script - do we need to load it as a module via importlib?
#     try:
#         # pass in 'snippet_name' explicitly as we depend on it below.
#         init_state: SDict = {"params": user_config, "parameters": user_config, "on_datapane": True}
#         res_scope = exec_user_script(code, init_state, snippet_name=USER_CODE_NAME)
#
#         # call render function/extract report var
#         if "render" in res_scope:
#             report = res_scope["render"]()
#         elif "report" in res_scope:
#             report = res_scope["report"]
#         else:
#             log.warning("report variable nor render function found in script")
#             report = []
#         return report
#     except SyntaxError:
#         raise CodeSyntaxError.from_exception()
#     except Exception:
#         raise CodeRaisedError.from_exception(partial(filter_frame_by_filename, USER_CODE_NAME))


################################################################################
# internal
def in_venv() -> bool:
    return hasattr(sys, "real_prefix") or sys.base_prefix != sys.prefix


@contextmanager
def script_env(env_dir: Path) -> t.ContextManager[None]:
    """
    Change the local dir and add to site-path so relative files and imports work
    TODO
        - this is NOT thread-safe - unlikely we can run multiple concurrent scripts atm
        - this doesn't save env's as a call-stack directly - however handled implictly via Python stack anyway
    """
    cwd = os.getcwd()
    log.debug(f"[cd] {cwd} -> {env_dir}")
    if not env_dir.exists():
        env_dir.mkdir(parents=True)

    full_env_dir = str(env_dir.resolve())
    sys.path.insert(0, full_env_dir)
    os.chdir(full_env_dir)
    try:
        yield
    finally:
        try:
            sys.path.remove(full_env_dir)
        except ValueError as e:
            raise CodeError("sys.path not as expected - was it modified?") from e
        os.chdir(cwd)
        log.debug(f"[cd] {cwd} <- {env_dir}")
        # shutil.rmtree(env_dir, ignore_errors=True)


def run_commands(cmds: List[str]) -> None:
    if cmds:
        _cmds = "\n".join(cmds)
        subprocess.run(args=_cmds, check=True, shell=True)
        if "pip" in _cmds:
            importlib.invalidate_caches()  # ensure new packages are detected


def setup_script(s: api.Script, env_dir: Path):
    """Setup the script - unpack & install deps"""
    # TODO - add local cache check here
    if env_dir.exists():
        log.debug("Package already exists, not redownloading")
        return None

    # download and unpack bundle locally into env_dir
    sdist = s.download_pkg()
    assert tarfile.is_tarfile(sdist), "Invalid sdist file"
    shutil.unpack_archive(sdist, extract_dir=env_dir, format="gztar")
    sdist.unlink()
    comp_r = compileall.compile_dir(env_dir, force=True, workers=1, quiet=1)
    if not comp_r:
        log.warning("Compiling script bundle failed - errors may occur")

    # install deps
    if s.requirements:
        pip_args = [sys.executable, "-m", "pip", "install"]
        if os.getuid() != 0 and not in_venv():
            # we're a normal/non-root user outside a venv
            pip_args.append("--user")
        pip_args.extend(s.requirements)
        log.debug(f"Calling pip as '{pip_args}'")
        subprocess.run(args=pip_args, check=True)
        importlib.invalidate_caches()  # ensure new packages are detected

    log.info(f"Successfully installed bundle for script {s.id}")


def exec_mod(script_path: Path, init_state: Optional[SDict] = None) -> SDict:
    # a = ast.parse(script, snippet_name, "exec")
    # ast_validation(a)
    init_state = init_state or dict()
    globalscope = {
        # "df": single_input,
        # "params": Munch(config),
        # "__builtins__": override_builtins(__import__)
    }
    globalscope.update(init_state)

    # we're using run_py rather than run_module to ensure same env as running on user's machine locally
    # we have a script, not a module - must follow script semantics
    res_scope = runpy.run_path(str(script_path), init_globals=globalscope, run_name=RUN_NAME)
    return res_scope


def ast_validation(node):
    for n in ast.walk(node):
        # TODO: implement check for import statements
        if isinstance(n, ast.Import):
            pass
        if isinstance(n, ast.ImportFrom):
            pass


class OverriddenBuiltins(dict):
    def __getitem__(self, name):
        if name in ENVIRON_CONFIG["banned_builtins"]:
            raise RuntimeError("Illegal builtin {}".format(name))
        return super().__getitem__(name)


def override_builtins(importer):
    b = OverriddenBuiltins(builtins.__dict__)
    b["__import__"] = importer
    return b


def importer(name, *x, **y):
    rootpkg = name.split(".")[0]
    if rootpkg not in ("runner",):  # TODO: module check
        return builtins.__import__(name, *x, **y)
    raise ImportError("Cannot import banned module")


def filter_frame_by_filename(filename: str, frame: FrameType) -> bool:
    return frame.f_code.co_filename == filename
