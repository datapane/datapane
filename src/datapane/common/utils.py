import gzip
import logging
import mimetypes
import os
import shutil
import subprocess
import sys
import time
import typing as t
from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory, mkstemp

import importlib_resources as ir
from colorlog import ColoredFormatter

from .dp_types import MIME, NPath

mimetypes.init(files=[ir.files("datapane.resources") / "mime.types"])

# TODO - hardcode as temporary fix until mimetypes double extension issue is sorted
double_ext_map = {
    ".vl.json": "application/vnd.vegalite.v3+json",
    ".vl2.json": "application/vnd.vegalite.v2+json",
    ".vl3.json": "application/vnd.vegalite.v3+json",
    ".bokeh.json": "application/vnd.bokeh.show+json",
    ".tar.gz": "application/x-tgz",
}

################################################################################
# Logging
logging.getLogger().disabled = True  # disable the root logger
# export the default application logger at INFO level
log: logging.Logger = logging.getLogger("datapane")
if log.level == logging.NOTSET:
    log.setLevel(logging.INFO)
get_logger: t.Callable[..., logging.Logger] = log.getChild


def setup_logging(verbose_mode: bool, logs_stream: t.TextIO = None) -> None:
    """Call to configure logging outside of django for scripts / tasks"""
    global log
    log.propagate = False
    log.setLevel(logging.DEBUG if verbose_mode else logging.INFO)
    log_formatter = ColoredFormatter(
        "%(blue)s%(asctime)s%(reset)s [%(log_color)s%(levelname)-5s%(reset)s] %(message)s",
        datefmt="%H:%M:%S",
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={},
        style="%",
    )

    log.handlers.clear()

    # file output
    # fileHandler = logging.FileHandler(LOGFILE, mode='w')
    # fileHandler.setFormatter(log_formatter)
    # log.addHandler(fileHandler)

    # console
    console_handler = logging.StreamHandler(stream=logs_stream or sys.stdout)
    console_handler.setFormatter(log_formatter)
    log.addHandler(console_handler)


@contextmanager
def log_command(command: str) -> t.ContextManager[None]:
    """Log an internal process"""
    log.info(f"Starting {command}")
    yield
    log.info(f"Finished {command}")


@contextmanager
def create_temp_file(
    suffix: str, prefix: str = "datapane-temp-", mode: str = "w+b"
) -> t.ContextManager[NamedTemporaryFile]:
    """Creates a NamedTemporaryFile that doesn't disappear on .close()"""
    temp_file = NamedTemporaryFile(suffix=suffix, prefix=prefix, mode=mode, delete=False)
    try:
        yield temp_file
    finally:
        os.unlink(temp_file.name)


@contextmanager
def temp_fname(
    suffix: str, prefix: str = "datapane-temp-", keep: bool = False
) -> t.ContextManager[str]:
    """Wrapper to generate a temporary filename only that is deleted on leaving context"""
    # TODO - return Path
    (in_f, in_f_name) = mkstemp(suffix=suffix, prefix=prefix)
    try:
        os.close(in_f)
        yield in_f_name
    finally:
        if os.path.exists(in_f_name) and not keep:
            os.unlink(in_f_name)


@contextmanager
def unix_compress_file(f_name: NPath, level: int = 6) -> t.ContextManager[str]:
    """(UNIX only) Return path to a compressed version of the input filename"""
    subprocess.run(["gzip", "-kf", f"-{level}", f_name], check=True)
    f_name_gz = f"{f_name}.gz"
    try:
        yield f_name_gz
    finally:
        os.unlink(f_name_gz)


@contextmanager
def compress_file(f_name: NPath, level: int = 6) -> t.ContextManager[str]:
    """(X-Plat) Return path to a compressed version of the input filename"""
    f_name_gz = f"{f_name}.gz"
    with open(f_name, "rb") as f_in:
        with gzip.open(f_name_gz, "wb", compresslevel=level) as f_out:
            shutil.copyfileobj(f_in, f_out)
    try:
        yield f_name_gz
    finally:
        os.unlink(f_name_gz)


@contextmanager
def temp_workdir() -> t.ContextManager[None]:
    """Set working dir to a tempdir for duration of context"""
    with TemporaryDirectory() as tmp_dir:
        curdir = os.getcwd()
        os.chdir(tmp_dir)
        try:
            yield None
        finally:
            os.chdir(curdir)


@contextmanager
def pushd(
    directory: NPath, pre_create: bool = False, post_remove: bool = False
) -> t.ContextManager[None]:
    """Switch dir and push it onto the (call-)stack"""
    directory = Path(directory)
    cwd = os.getcwd()
    log.debug(f"[cd] {cwd} -> {directory}")
    if not directory.exists() and pre_create:
        Path(directory).mkdir(parents=True)
    os.chdir(directory)
    try:
        yield
    finally:
        log.debug(f"[cd] {cwd} <- {directory}")
        os.chdir(cwd)
        if post_remove:
            shutil.rmtree(directory, ignore_errors=True)


def unixtime() -> int:
    return int(time.time())


def get_filesize(filename: Path) -> int:
    return filename.stat().st_size


def guess_type(filename: Path) -> MIME:
    ext = "".join(filename.suffixes)
    if ext in double_ext_map.keys():
        return double_ext_map[ext]
    mtype, _ = mimetypes.guess_type(str(filename))
    return mtype or "application/octet-stream"


def walk_path(path: Path) -> t.Iterable[Path]:
    for p in path.rglob("*"):
        if not p.is_dir():
            yield p
