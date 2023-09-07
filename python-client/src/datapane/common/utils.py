import locale
import logging
import mimetypes
import re
import sys
import typing as t
from pathlib import Path

import chardet
import importlib_resources as ir
from chardet.universaldetector import UniversalDetector

from .dp_types import MIME

log = logging.getLogger("datapane")

################################################################################
# CONSTANTS
ON_WINDOWS = sys.platform == "win32"

################################################################################
# MIME-type handling
mimetypes.init(files=[str(ir.files("datapane.resources") / "mime.types")])

# TODO - hardcode as temporary fix until mimetypes double extension issue is sorted
_double_ext_map = {
    ".vl.json": "application/vnd.vegalite.v5+json",
    ".vl2.json": "application/vnd.vegalite.v2+json",
    ".vl3.json": "application/vnd.vegalite.v3+json",
    ".vl4.json": "application/vnd.vegalite.v4+json",
    ".vl5.json": "application/vnd.vegalite.v5+json",
    ".bokeh.json": "application/vnd.bokeh.show+json",
    ".pl.json": "application/vnd.plotly.v1+json",
    ".fl.html": "application/vnd.folium+html",
    ".tbl.html": "application/vnd.datapane.table+html",
    ".tar.gz": "application/x-tgz",
}
double_ext_map: t.Dict[str, MIME] = {k: MIME(v) for k, v in _double_ext_map.items()}


def guess_type(filename: Path) -> MIME:
    ext = "".join(filename.suffixes)
    if ext in double_ext_map.keys():
        return double_ext_map[ext]
    mtype: str
    mtype, _ = mimetypes.guess_type(str(filename))
    return MIME(mtype or "application/octet-stream")


def guess_encoding(fn: str) -> str:
    with open(fn, "rb") as f:
        detector = UniversalDetector()
        for line in f.readlines():
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    return detector.result["encoding"]


def utf_read_text(file: Path) -> str:
    """Encoding-aware text reader
    - handles cases like on Windows where a file is UTF-8, but default locale is windows-1252
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


def dict_drop_empty(xs: t.Optional[t.Dict] = None, none_only: bool = False, **kwargs) -> t.Dict:
    """Return a new dict with the empty/falsey values removed"""
    xs = {**(xs or {}), **kwargs}

    if none_only:
        return {k: v for (k, v) in xs.items() if v is not None}
    else:
        return {k: v for (k, v) in xs.items() if v or isinstance(v, bool)}


def should_compress_mime_type_for_upload(mime_type: str) -> bool:
    # This strategy is based on:
    # - looking at mime type databases used by `mimetypes` module
    # - our custom mime types in double_ext_map
    # - some other online sources that capture real-world usage:
    #   - https://letstalkaboutwebperf.com/en/gzip-brotli-server-config/
    #   - https://github.com/h5bp/server-configs-nginx/blob/main/mime.types
    return any(pattern.search(mime_type) for pattern in _SHOULD_COMPRESS_MIME_TYPE_REGEXPS)


_SHOULD_COMPRESS_MIME_TYPE_REGEXPS = [
    re.compile(p)
    for p in [
        r"^text/",
        r"\+json$",
        r"\+xml$",
        r"\+html$",
        r"^application/json$",
        r"^application/vnd\.pickle\+binary$",
        r"^application/vnd\.apache\.arrow\+binary$",
        r"^application/xml$",
    ]
]
