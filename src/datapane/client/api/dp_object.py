"""## Base classes

The base classes used by all Datapane objects stored on the Datapane Server
and accessible by the client API

..note:: This module is not used directly
"""
import json
import os
import pprint
import typing as t
from pathlib import Path
from typing import Optional, Type
from urllib import parse as up

import pandas as pd
import validators as v
from munch import Munch
from requests import HTTPError

from datapane import log
from datapane.client import DPError
from datapane.common import JSON, URL, ArrowFormat, SDict
from datapane.common.df_processor import to_df

from . import Resource
from .common import DPTmpFile, FileList

__all__ = ["DPObjectRef"]

U = t.TypeVar("U", bound="DPObjectRef")


class DPObjectRef:
    """Abstract class used to reference core Datapane server objects - not used directly."""

    endpoint: str
    res: Resource

    _url: URL = "<local resource>"
    _dto: t.Optional[Munch] = None

    list_fields: t.List[str] = ["name", "web_url", "group"]

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
                raise DPError(f"{url} is not a valid object ref")
            x: up.SplitResult = up.urlsplit(url)
            _id = list(filter(None, x.path.split("/")))[-1]
        else:
            _id = id_or_url

        rel_obj_url = up.urljoin(self.endpoint, f"{_id}/")
        self.res = Resource(endpoint=rel_obj_url)
        self._url = self.res.url

    def __init__(self, dto: Optional[JSON] = None):
        # Save a server-round trip if we already have the DTO
        if dto:
            self.dto = dto
            self.url = dto.id

    @classmethod
    def get(cls: Type[U], name: str, owner: Optional[str] = None) -> U:
        """
        Lookup and retrieve an object from the Datapane Server by its name

        Args:
            name: The name of the object, e.g. 'my-blob-3` or `fred/my-blob-3`
            owner: The owner of the object, e.g. `fred` (can be provided with the name as shown above)

        Returns:
            The object if found
        """
        lookup_value = name.split("/", maxsplit=1)
        if len(lookup_value) == 2:
            owner, name = lookup_value
        try:
            res = Resource(f"{cls.endpoint}/lookup/").get(name=name, owner=owner)
        except HTTPError as e:
            lookup_str = f"{owner}/{name}" if owner else name
            log.error(
                f"Couldn't find '{lookup_str}', are you sure it exists? If error occurs within a script please try updating the code to include the script's owner in name - e.g. 'owner/{name}'."
            )
            raise e
        return cls(dto=res)

    @classmethod
    def by_id(cls: Type[U], id_or_url: str) -> U:
        """
        Lookup and retrieve an object from the Datapane Server by its id

        Args:
            id_or_url: The `id`, or full URL that represents the object

        Returns:
            The object if found
        """
        x = cls()
        x.url = id_or_url
        x.refresh()
        return x

    @classmethod
    def post_with_files(cls: Type[U], files: FileList = None, file: t.Optional[Path] = None, **kwargs) -> U:
        # TODO - move into UploadedFileMixin ?
        if file:
            # wrap up a single file into a FileList
            files: FileList = dict(uploaded_file=[file])

        res = Resource(cls.endpoint).post_files(files, **kwargs)
        return cls(res)

    @classmethod
    def post(cls: Type[U], **kwargs) -> U:
        res = Resource(cls.endpoint).post(**kwargs)
        return cls(res)

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

    # user-facing helper functions
    def refresh(self):
        """Refresh the object with the latest data from the Datapane Server"""
        self.dto = self.res.get()
        log.debug(f"Refreshed {self.url}")

    def delete(self):
        """Delete the object on the server"""
        self.res.delete()
        log.debug(f"Deleted object {self.url}")

    def update(self, **kwargs):
        # filter None values
        kwargs = {k: v for (k, v) in kwargs.items() if v is not None}
        self.res.patch(**kwargs)
        self.refresh()
        log.debug(f"Updated object {self.url}")

    @classmethod
    def list(cls) -> t.Iterable[SDict]:
        """
        Returns: A list of the Datapane objects of this type that are owned by the user
        """
        endpoint: t.Optional[str] = cls.endpoint

        def process_field(v):
            if isinstance(v, dict):
                return json.dumps(v, indent=True)
            return v

        while endpoint:
            r = Resource(endpoint=endpoint)
            items = r.get()
            # filter the items, ordering as needed
            for x in items.results:
                yield {k: process_field(x[k]) for k in cls.list_fields if k in x}
            endpoint = items.next if items.next else None


# NOTE - this has been inlined into Blobs for now
# class ExportableObjectMixin:
#    """Used by both Assets and Blobs to abstract over uploading/downloading and exporting"""


def save_df(df: pd.DataFrame) -> DPTmpFile:
    """Export a df for uploading"""
    fn = DPTmpFile(ArrowFormat.ext)

    # create a copy of the df to process
    df = to_df(df)
    if df.size == 0:
        raise DPError("Empty DataFrame provided")

    # process_df called in Arrow.save_file
    # process_df(df)
    ArrowFormat.save_file(fn.name, df)
    log.debug(f"Saved df to {fn} ({os.path.getsize(fn.file)} bytes)")
    return fn
