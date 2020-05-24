import json
import os
import pickle
import pprint
import time
import typing as t
from pathlib import Path
from typing import Optional, Type
from urllib import parse as up

# TODO - import only during type checking and import future.annotations when dropping py 3.6
import pandas as pd
import requests
import validators as v
from munch import Munch

from datapane import __version__
from datapane.client.scripts import DatapaneCfg
from datapane.common import JSON, PKL_MIMETYPE, URL, NPath, SDict, log
from datapane.common.datafiles import ArrowFormat, df_ext_map
from datapane.common.df_processor import process_df, to_df
from datapane.common.utils import compress_file, guess_type

from .common import DPTmpFile, Resource, _download_file

U = t.TypeVar("U", bound="BEObjectRef")


class BEObjectRef:
    endpoint: str
    res: Resource

    _url: URL = "<local resource>"
    _dto: t.Optional[Munch] = None

    list_fields: t.List[str] = ["name", "web_url", "versions"]

    @property
    def dto(self) -> t.Optional[Munch]:
        return self._dto

    @dto.setter
    def dto(self, dto: Munch):
        self._dto = dto
        # self.url = dto.id

    @dto.deleter
    def dto(self):
        pass

    @property
    def has_dto(self) -> bool:
        return self.dto is not None

    @property
    def url(self) -> URL:
        return self._url

    @url.setter
    def url(self, id_or_url: URL):
        # build a url to the resource on the api server
        _id: str
        id_or_url = str(id_or_url)
        if self.endpoint in id_or_url:
            url = id_or_url
            if not url.startswith("http"):
                url = f"https://{url}"
            if not v.url(url):
                raise AssertionError(f"{url} is not a valid object ref")
            x: up.SplitResult = up.urlsplit(url)
            _id = list(filter(None, x.path.split("/")))[-1]
        else:
            _id = id_or_url

        rel_obj_url = up.urljoin(self.endpoint, f"{_id}/")
        self.res = Resource(endpoint=rel_obj_url)
        self._url = self.res.url

    def __init__(self, dto: Optional[JSON] = None):
        # Save a server-round trip if we alread have the DTO
        if dto:
            self.dto = dto
            self.url = dto.id

    @classmethod
    def get(
        cls: Type[U], name: str, owner: Optional[str] = None, version: Optional[str] = None
    ) -> U:
        res = Resource(f"{cls.endpoint}/lookup/").get(name=name, owner=owner, version=version)
        return cls(res)

    @classmethod
    def by_id(cls: Type[U], id_or_url: str) -> U:
        x = cls()
        x.url = id_or_url
        x.refresh()
        return x

    @classmethod
    def post_with_file(cls: Type[U], file: Path, **kwargs) -> JSON:
        # get signed url
        upload_name = f"{int(time.time())}-{file.name}"
        upload_url = Resource("/generate-upload-url/").post(import_path=upload_name)
        # post text to blob store
        # TODO - we should disable compression where unneeded, e.g. .gz, .zip, .png, etc
        with compress_file(str(file)) as fn_gz, Path(fn_gz).expanduser().open("rb") as fp:
            log.info(f"Uploading {file}")
            headers = {"Content-Encoding": "gzip", "Content-Type": guess_type(file)}
            requests.put(upload_url, data=fp, headers=headers).raise_for_status()
        return cls.post(import_path=upload_name, **kwargs)

    @classmethod
    def post(cls: Type[U], **kwargs) -> JSON:
        """post object to api"""
        return Resource(cls.endpoint).post(**kwargs)

    def __getattr__(self, attr):
        if self.has_dto and not attr.startswith("__"):
            log.debug(f"Proxying '{attr}' lookup to DTO")
            return getattr(self._dto, attr)
        # Default behaviour
        return self.__getattribute__(attr)

    def __str__(self) -> str:
        return self.url

    def __repr__(self) -> str:
        return pprint.pformat(self._dto.toDict()) if self.has_dto else self.__str__()

    # helper functions
    def refresh(self):
        """Update the local representation of the object"""
        self.dto = self.res.get()
        log.debug(f"Refreshed {self.url}")

    def delete(self):
        self.res.delete()
        log.debug(f"Deleted object {self.url}")

    def update(self, **kwargs):
        self.res.patch(**kwargs)
        self.refresh()
        log.debug(f"Updated object {self.url}")

    @classmethod
    def list(cls) -> t.Iterable[SDict]:
        """Return a list of the resources """
        endpoint: t.Optional[str] = cls.endpoint

        while endpoint:
            r = Resource(endpoint=endpoint)
            items = r.get()
            # filter the items, ordering as needed
            for x in items.results:
                yield {k: x[k] for k in cls.list_fields if k in x}
            endpoint = items.next if items.next else None


class ExportableObjectMixin:
    """Used by both Assets and Blobs to abstract over uploading/downloading and exporting"""

    def download_df(self) -> pd.DataFrame:
        with DPTmpFile(ArrowFormat.ext) as fn:
            _download_file(self.gcs_signed_url, fn.name)
            return ArrowFormat.load_file(fn.name)

    def download_file(self, fn: NPath):
        fn = Path(fn)

        def get_export_format() -> str:
            ext = fn.suffix
            if ext not in df_ext_map:
                raise ValueError(
                    f"Extension {ext} not valid for exporting table. Must be one of {', '.join(df_ext_map.keys())}"
                )
            return df_ext_map[ext].enum

        # If file is of arrow type, export it. Otherwise use the gcs url directly.
        if self.content_type == ArrowFormat.content_type:
            with self.res.nest_endpoint(
                endpoint=f"export/?export_format={get_export_format()}"
            ) as nest_res:
                download_url = nest_res.get()
        else:
            download_url = self.gcs_signed_url
        _download_file(download_url, fn)

    def download_obj(self) -> t.Any:
        with DPTmpFile(".obj") as fn:
            _download_file(self.gcs_signed_url, fn.name)
            # In the case that the original object was a Python object or bytes-like object,
            # the downloaded obj will be a pickle which needs to be unpickled.
            # Otherwise it's a stringified JSON object (e.g. an Altair plot) that can be returned as JSON.
            if self.content_type == PKL_MIMETYPE:
                with fn.file.open("rb") as fp:
                    return pickle.load(fp)
            else:
                return json.loads(fn.file.read_text())

    @staticmethod
    def _save_df(df: pd.DataFrame) -> DPTmpFile:
        fn = DPTmpFile(ArrowFormat.ext)
        df = to_df(df)
        process_df(df)
        ArrowFormat.save_file(fn.name, df)
        log.debug(f"Saved df to {fn} ({os.path.getsize(fn.file)} bytes)")
        return fn

    @classmethod
    def _save_obj(cls, data: t.Any, is_json: bool) -> DPTmpFile:
        # import here as a very slow module due to nested imports
        from ..files import save

        fn = save(data, default_to_json=is_json)
        log.debug(f"Saved object to {fn} ({os.path.getsize(fn.file)} bytes)")
        return fn


class Blob(BEObjectRef, ExportableObjectMixin):
    endpoint: str = "/blobs/"

    @classmethod
    def upload_df(cls, df: pd.DataFrame, **kwargs) -> "Blob":
        with cls._save_df(df) as fn:
            return cls(cls.post_with_file(fn.file, **kwargs))

    @classmethod
    def upload_file(cls, fn: NPath, **kwargs) -> "Blob":
        return cls(cls.post_with_file(Path(fn), **kwargs))

    @classmethod
    def upload_obj(cls, data: t.Any, is_json: bool = False, **kwargs: JSON) -> "Blob":
        with cls._save_obj(data, is_json) as fn:
            return cls(cls.post_with_file(fn.file, **kwargs))


class Script(BEObjectRef):
    endpoint: str = "/scripts/"

    @classmethod
    def upload_pkg(cls, sdist: Path, dp_cfg: DatapaneCfg, **kwargs) -> "Script":
        # merge all the params for the API-call
        kwargs["api_version"] = __version__
        new_kwargs = {**dp_cfg.to_dict(), **kwargs}
        return cls(cls.post_with_file(sdist, **new_kwargs))

    def download_pkg(self) -> Path:
        fn = _download_file(self.gcs_signed_url)
        return Path(fn)

    def call(self, **params):
        """Download, install, and call the script with the provided params"""
        # NOTE - use __call__??
        # TODO - move exec_script here?
        # TODO - call should handle param defaults
        from datapane.runner.exec_script import run

        run(self, params)

    def run(self, parameters=None, cache=True) -> "Run":
        """(remote) run the given app (cloning if needed?)"""
        parameters = parameters or dict()
        return Run(Run.post(script=self.url, parameter_vals=parameters, cache=cache))

    def local_run(self, parameters=None) -> "Run":
        """(local) run the given script"""
        # NOTE -is there a use-case for this?
        raise NotImplementedError()


class Run(BEObjectRef):
    endpoint: str = "/runs/"

    def is_complete(self) -> bool:
        """Return true if the run has finished"""
        return self.status in ["SUCCESS", "ERROR", "CANCELLED"]


class Variable(BEObjectRef):
    endpoint: str = "/uservariables/"
    list_fields = ["name", "versions"]

    @classmethod
    def add(cls, name: str, value: str, visibility: str = "PRIVATE") -> "Variable":
        return cls(cls.post(name=name, value=value, visibility=visibility))
