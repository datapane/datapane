"""## Common objects

Common/shared objects and types used throughout the client API

..note:: This module is not used directly
"""
import atexit
import os
import shutil
import time
from datetime import timedelta
from pathlib import Path
from tempfile import gettempdir, mkdtemp, mkstemp

from typing_extensions import Self

from datapane.client import log
from datapane.common import MIME, guess_type

################################################################################
# Tmpfile handling
# We create a tmp-dir per Python execution that stores all working files,
# we attempt to delete where possible, but where not, we allow the atexit handler
# to cleanup for us on shutdown
cache_dir = Path(gettempdir())

# Remove any old dp-tmp-* dirs over 24hrs old which might not have been cleaned up due to unexpected exit
one_day_ago = time.time() - timedelta(days=1).total_seconds()
prev_tmp_dirs = (p for p in cache_dir.glob("dp-tmp-*") if p.is_dir() and p.stat().st_mtime < one_day_ago)
for p in prev_tmp_dirs:
    log.debug(f"Removing stale temp dir {p}")
    shutil.rmtree(p, ignore_errors=True)

# create new dp-tmp for this session
tmp_dir = Path(mkdtemp(prefix="dp-tmp-", dir=cache_dir)).absolute()


class DPTmpFile:
    """
    Generate a tempfile in dp temp dir
    when used as a contextmanager, deleted on removing scope
    otherwise, removed by atexit hook
    """

    def __init__(self, ext: str):
        fd, name = mkstemp(suffix=ext, prefix="dp-tmp-", dir=tmp_dir)
        os.close(fd)
        self.file = Path(name)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):  # noqa: ANN001
        log.debug(f"Removing {self.name}")
        if self.file.exists():
            self.file.unlink()  # (missing_ok=True)

    @property
    def name(self) -> str:
        return str(self.file)

    @property
    def full_name(self) -> str:
        return str(self.file.absolute())

    @property
    def mime(self) -> MIME:
        return guess_type(self.file)

    def __str__(self) -> str:
        return self.name


@atexit.register
def cleanup_tmp():
    """Ensure we cleanup the tmp_dir on Python VM exit"""
    # breaks tests
    # log.debug(f"Removing current session DP tmp work dir {tmp_dir}")
    shutil.rmtree(tmp_dir, ignore_errors=True)
