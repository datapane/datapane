import datetime
import gzip
import io
import os
import shutil
import subprocess
import time
import typing as t
from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory, mkstemp

from .dp_types import NPath, log
from .utils import ON_WINDOWS


@contextmanager
def log_command(command: str) -> t.Generator[None, None, None]:
    """Log an internal process"""
    log.info(f"Starting {command}")
    yield
    log.info(f"Finished {command}")


@contextmanager
def create_temp_file(
    suffix: str, prefix: str = "datapane-temp-", mode: str = "w+b"
) -> t.Generator[NamedTemporaryFile, None, None]:
    """Creates a NamedTemporaryFile that doesn't disappear on .close()"""
    temp_file = NamedTemporaryFile(suffix=suffix, prefix=prefix, mode=mode, delete=False)
    try:
        yield temp_file
    finally:
        os.unlink(temp_file.name)


@contextmanager
def temp_fname(suffix: str, prefix: str = "datapane-temp-", keep: bool = False) -> t.Generator[str, None, None]:
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
def unix_compress_file(f_name: NPath, level: int = 6) -> t.Generator[str, None, None]:
    """(UNIX only) Return path to a compressed version of the input filename"""
    subprocess.run(["gzip", "-kf", f"-{level}", f_name], check=True)
    f_name_gz = f"{f_name}.gz"
    try:
        yield f_name_gz
    finally:
        os.unlink(f_name_gz)


@contextmanager
def unix_decompress_file(f_name: NPath) -> t.Generator[str, None, None]:
    """(UNIX only) Return path to a compressed version of the input filename"""
    subprocess.run(["gunzip", "-kf", f_name], check=True)
    f_name_gz = f"{f_name}.gz"
    try:
        yield f_name_gz
    finally:
        os.unlink(f_name_gz)


@contextmanager
def compress_file(f_name: NPath, level: int = 6) -> t.Generator[str, None, None]:
    """(X-Plat) Return path to a compressed version of the input filename"""
    f_name_gz = f"{f_name}.gz"
    with open(f_name, "rb") as f_in, gzip.open(f_name_gz, "wb", compresslevel=level) as f_out:
        shutil.copyfileobj(f_in, f_out)
    try:
        yield f_name_gz
    finally:
        # NOTE - disable on windows temporarily
        if not ON_WINDOWS:
            os.unlink(f_name_gz)


def inmemory_compress(content: t.BinaryIO) -> t.BinaryIO:
    """(x-plat) Memory-based gzip compression"""
    content.seek(0)
    zbuf = io.BytesIO()
    with gzip.GzipFile(mode="wb", fileobj=zbuf, mtime=0.0) as zfile:
        zfile.write(content.read())
    zbuf.seek(0)
    return zbuf


@contextmanager
def temp_workdir() -> t.Generator[str, None, None]:
    """Set working dir to a tempdir for duration of context"""
    with TemporaryDirectory() as tmp_dir:
        curdir = os.getcwd()
        os.chdir(tmp_dir)
        try:
            yield None
        finally:
            os.chdir(curdir)


@contextmanager
def pushd(directory: NPath, pre_create: bool = False, post_remove: bool = False) -> t.Generator[None, None, None]:
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


def get_filesize(filename: Path) -> int:
    return filename.stat().st_size


def walk_path(path: Path) -> t.Iterable[Path]:
    for p in path.rglob("*"):
        if not p.is_dir():
            yield p


def unixtime() -> int:
    return int(time.time())


def timestamp(x: t.Optional[datetime.datetime] = None) -> str:
    """Return ISO timestamp for a datetime"""
    x = x or datetime.datetime.utcnow()
    return f'{x.isoformat(timespec="seconds")}{"" if x.tzinfo else "Z"}'
