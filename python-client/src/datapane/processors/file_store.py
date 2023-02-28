from __future__ import annotations

import abc
import datetime
import gzip
import hashlib
import io
import tempfile
import typing as t
from pathlib import Path
from shutil import copyfileobj

from typing_extensions import Self

from datapane._vendor import base64io
from datapane.common import guess_type

SERVED_REPORT_ASSETS_DIR = "assets"
GZIP_MTIME = datetime.datetime(year=2000, month=1, day=1).timestamp()


class FileEntry:
    file: t.IO
    _ext: str
    _dir_path: t.Optional[Path]

    # post-freeze
    frozen: bool = False
    mime: str
    hash: str
    size: int
    wrapped: t.BinaryIO

    def __init__(self, ext: str, mime: t.Optional[str] = None, dir_path: t.Optional[Path] = None):
        self.mime = mime or guess_type(Path(f"tmp{ext}"))
        self._ext = ext
        self._dir_path = dir_path

    @abc.abstractmethod
    def freeze(self) -> None:
        """Must be called after writing / adding to store
        # TODO - add to contextmanager??
        """

    @property
    @abc.abstractmethod
    def src(self) -> str:
        pass

    def as_dict(self) -> dict:
        assert self.frozen
        return dict(src=self.src, hash=self.hash, size=self.size, mime=self.mime)

    def __eq__(self, other: FileEntry) -> bool:
        if self.hash:
            return self.hash == other.hash
        raise NotImplementedError()


class NullWriter(io.BytesIO):
    def write(self, s):
        pass

    def writelines(self, *a, **kw) -> None:
        pass


class DummyFileEntry(FileEntry):
    """File entry that discards all data - for internal use"""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.file = NullWriter()

    def freeze(self):
        self.size = 0
        self.hash = "abcdef"
        self.frozen = True

    def src(self) -> str:
        return "/dev/null"


class B64FileEntry(FileEntry):
    """Memory-based b64 file"""

    # requires b64io is bytes only and wraps to a bytes file only
    file: base64io.Base64IO
    wrapped: io.BytesIO
    contents: bytes

    def __init__(self, ext: str, mime: t.Optional[str] = None, *a, **kw):
        super().__init__(ext, mime, *a, **kw)
        self.wrapped = io.BytesIO()
        self.file = base64io.Base64IO(self.wrapped)

    def freeze(self) -> None:
        if not self.frozen:
            self.frozen = True
            # get a reference to the buffer to splice later
            self.file.close()
            self.file.flush()
            self.contents = self.wrapped.getvalue()
            # calc other properties
            self.hash = hashlib.sha256(self.contents).hexdigest()[:10]
            self.size = self.wrapped.tell()

    @property
    def src(self) -> str:
        return f"data:{self.mime};base64,{self.contents.decode('ascii')}"


class GzipTmpFileEntry(FileEntry):
    """Gzipped file, by default stored in /tmp"""

    # both file and wapper files are bytes-only
    file: gzip.GzipFile
    # TODO - this could actually be an in-memory file...
    wrapped: tempfile.NamedTemporaryFile
    has_output_dir: bool = False

    # Do we need DPTmpFile here, or just use namedtempfile??
    def __init__(self, ext: str, mime: t.Optional[str] = None, dir_path: t.Optional[Path] = None):
        super().__init__(ext, mime, dir_path)

        if dir_path:
            # create as a permanent file within the given dir
            self.has_output_dir = True
            self.wrapped = tempfile.NamedTemporaryFile("w+b", suffix=ext, prefix="dp-", dir=dir_path, delete=False)
        else:
            self.wrapped = tempfile.NamedTemporaryFile("w+b", suffix=ext, prefix="dp-")

        self.file = gzip.GzipFile(fileobj=self.wrapped, mode="w+b", mtime=GZIP_MTIME)

    def calc_hash(self, f: t.IO) -> str:
        f.seek(0)
        file_hash = hashlib.sha256()
        while chunk := f.read(8192):
            file_hash.update(chunk)
        return file_hash.hexdigest()[:10]

    @property
    def src(self) -> str:
        if self.has_output_dir:
            return f"/{SERVED_REPORT_ASSETS_DIR}/{Path(self.wrapped.name).name}"
        else:
            return "NYI"

    def freeze(self) -> None:
        if not self.frozen:
            self.frozen = True
            self.file.flush()
            self.file.close()
            self.wrapped.flush()
            # size will be the compressed size...
            self.size = self.wrapped.tell()
            self.hash = self.calc_hash(self.wrapped)


class FileStore:
    # TODO - make this a CAS (index by object hash itself?)
    # NOTE - currently we pass dir_path via the FileStore, could move into the file themselves?
    def __init__(self, fw_klass: t.Type[FileEntry], assets_dir: t.Optional[Path] = None):
        super().__init__()
        self.fw_klass = fw_klass
        self.files: t.List[FileEntry] = []
        self.dir_path = assets_dir

    def __add__(self, other: FileStore) -> Self:
        # TODO - ensure factory is the same for both
        self.files.extend(other.files)
        return self

    @property
    def store_count(self) -> int:
        return len(self.files)

    @property
    def file_list(self) -> t.List[t.BinaryIO]:
        return [f.wrapped for f in self.files]

    def get_file(self, ext: str, mime: str) -> FileEntry:
        return self.fw_klass(ext, mime, self.dir_path)

    def add_file(self, fw: FileEntry) -> None:
        fw.freeze()
        self.files.append(fw)

    def load_file(self, path: Path) -> FileEntry:
        """load a file into the store (makes a copy)"""
        # TODO - ideally lazily-link a path to the store (rather than copy it in)
        ext = "".join(path.suffixes)
        dest_obj = self.fw_klass(ext=ext, dir_path=self.dir_path)
        with path.open("rb") as src_obj:
            copyfileobj(src_obj, dest_obj.file)
        self.add_file(dest_obj)
        return dest_obj

    def as_dict(self) -> dict:
        """Build a json structure suitable for embedding in a html file, json-rpc response, etc."""
        x: FileEntry  # noqa: F842
        return {x.hash: x.as_dict() for x in self.files}

    def get_entry(self, hash: str) -> t.Optional[FileEntry]:
        # TODO - change self.files to a dict[hash, FileEntry]?
        return next((f for f in self.files if f.hash == hash), None)
