import datetime
import gzip
import locale
import logging
import logging.config
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

import chardet
import importlib_resources as ir
from chardet.universaldetector import UniversalDetector

from .dp_types import MIME, DPError, DPMode, NPath, get_dp_mode

mimetypes.init(files=[ir.files("datapane.resources") / "mime.types"])

# TODO - hardcode as temporary fix until mimetypes double extension issue is sorted
_double_ext_map = {
    ".vl.json": "application/vnd.vegalite.v4+json",
    ".vl2.json": "application/vnd.vegalite.v2+json",
    ".vl3.json": "application/vnd.vegalite.v3+json",
    ".vl4.json": "application/vnd.vegalite.v4+json",
    ".bokeh.json": "application/vnd.bokeh.show+json",
    ".pl.json": "application/vnd.plotly.v1+json",
    ".fl.html": "application/vnd.folium+html",
    ".tbl.html": "application/vnd.datapane.table+html",
    ".tar.gz": "application/x-tgz",
}
double_ext_map: t.Dict[str, MIME] = {k: MIME(v) for k, v in _double_ext_map.items()}

ON_WINDOWS = sys.platform == "win32"

################################################################################
# CONSTANTS
DEFAULT_CSS_HEADER = """:root {
    --dp-accent-color: #4E46E5;
    --dp-bg-color: #FFF;
    --dp-text-align: justify;
    --dp-font-family: Inter var, ui-sans-serif, system-ui;
}"""

DEFAULT_HTML_HEADER = f"""<style type="text/css">
{DEFAULT_CSS_HEADER}
</style>"""

################################################################################
# Logging
# export the application logger at WARNING level by default
log: logging.Logger = logging.getLogger("datapane")
if log.level == logging.NOTSET:
    log.setLevel(logging.WARNING)


_have_setup_logging: bool = False


def _setup_dp_logging(verbosity: int = 0, logs_stream: t.TextIO = None) -> None:
    global _have_setup_logging

    log_level = "WARNING"
    if verbosity == 1:
        log_level = "INFO"
    elif verbosity > 1:
        log_level = "DEBUG"

    # don't configure global logging config when running as a library
    if get_dp_mode() == DPMode.LIBRARY:
        log.warning("Configuring datapane logging in library mode")
        # return None

    # TODO - only allow setting once?
    if _have_setup_logging:
        log.warning(f"Reconfiguring datapane logger when running as {get_dp_mode().name}")
        # raise AssertionError("Attempting to reconfigure datapane logger")
        return None

    # initial setup via dict-config
    _have_setup_logging = True
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "colored": {
                "()": "colorlog.ColoredFormatter",
                "format": "[%(blue)s%(asctime)s%(reset)s] [%(log_color)s%(levelname)-5s%(reset)s] %(message)s",
                "datefmt": "%H:%M:%S",
                "reset": True,
                "log_colors": {
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                },
                "style": "%",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "colored",
                "stream": logs_stream or sys.stderr,
            }
        },
        "loggers": {"datapane": {"level": log_level, "propagate": True}},
        # only show INFO for anything else
        "root": {"handlers": ["console"], "level": "INFO"},
    }
    logging.config.dictConfig(log_config)


def enable_logging():
    """Enable logging for debug purposes"""
    _setup_dp_logging(verbosity=2)


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
def temp_fname(suffix: str, prefix: str = "datapane-temp-", keep: bool = False) -> t.ContextManager[str]:
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
def unix_decompress_file(f_name: NPath) -> t.ContextManager[str]:
    """(UNIX only) Return path to a compressed version of the input filename"""
    subprocess.run(["gunzip", "-kf", f_name], check=True)
    f_name_gz = f"{f_name}.gz"
    try:
        yield f_name_gz
    finally:
        os.unlink(f_name_gz)


@contextmanager
def compress_file(f_name: NPath, level: int = 6) -> t.ContextManager[str]:
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
def pushd(directory: NPath, pre_create: bool = False, post_remove: bool = False) -> t.ContextManager[None]:
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
    mtype: str
    mtype, _ = mimetypes.guess_type(str(filename))
    return MIME(mtype or "application/octet-stream")


def walk_path(path: Path) -> t.Iterable[Path]:
    for p in path.rglob("*"):
        if not p.is_dir():
            yield p


def guess_encoding(fn: str) -> str:
    with open(fn, "rb") as f:
        detector = UniversalDetector()
        for line in f.readlines():
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    return detector.result["encoding"]


def timestamp(x: t.Optional[datetime.datetime] = None) -> str:
    x = x or datetime.datetime.utcnow()
    return f'{x.isoformat(timespec="seconds")}{"" if x.tzinfo else "Z"}'


def dict_drop_empty(xs: t.Dict, none_only: bool = False) -> t.Dict:
    """Return a new dict with the empty/falsey values removed"""
    if none_only:
        return {k: v for (k, v) in xs.items() if v is not None}
    else:
        return {k: v for (k, v) in xs.items() if v or isinstance(v, bool)}


def process_notebook(input_file: Path, output_file: Path):
    """
    Strips the output of the jupyter notebook provided as input and also removes cells tagged as "exclude".
    input_file: file object or path of jupyter notebook that needs to be processed
    output_file: path of the output file
    """
    import nbconvert
    from packaging.version import parse as parse_version

    # check available nbconvert version and raise error if it is not >=6.0.0
    if parse_version(nbconvert.__version__) < parse_version("6.0.0"):
        raise DPError("Source file upload only works with nbconvert >= 6.0.0. Run pip install 'nbconvert>=6.0.0'")

    from nbconvert import NotebookExporter
    from nbconvert.preprocessors import ClearOutputPreprocessor, TagRemovePreprocessor
    from nbconvert.preprocessors.sanitize import SanitizeHTML
    from traitlets.config import Config

    if input_file.suffix != ".ipynb":
        raise DPError("Source file should be a jupyter notebook.")

    # Setup config
    c = Config()
    # Configure tag removal preprocessors
    c.TagRemovePreprocessor.remove_cell_tags = ("exclude",)
    exporter = NotebookExporter(config=c)
    exporter.register_preprocessor(ClearOutputPreprocessor(config=c), True)
    exporter.register_preprocessor(TagRemovePreprocessor(config=c), True)
    exporter.register_preprocessor(SanitizeHTML(config=c), True)
    # Run exporter
    output, _ = exporter.from_filename(input_file)
    # write output to file
    Path(output_file).write_text(output)


def utf_read_text(file: Path) -> str:
    """Encoding-aware text reader
    - handles cases like on windows where a file is UTF-8, but default locale is windows-1252
    """
    if ON_WINDOWS:
        f_bytes = file.read_bytes()
        f_enc: str = chardet.detect(f_bytes)["encoding"]
        # NOTE - can just special case utf-8 files here?
        def_enc = locale.getpreferredencoding()
        log.debug(f"Default encoding is {def_enc}, file encoded as {f_enc}")
        if def_enc.upper() != f_enc.upper():
            log.warning(f"Text file {file} encoded as {f_enc}, auto-converting")
        return f_bytes.decode(encoding=f_enc)
    else:
        # for linux/macOS assume utf-8
        return file.read_text()
