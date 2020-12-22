"""
## Datapane Teams API

Datapane Teams includes features to automate your Python workflows and easily build and share data-driven apps and results with your teams.

Generally objects are created on the server via the static methods (rather than the constructor),
and the instance methods and fields are used to access values (e.g. `.name`) and behaviour (e.g. `delete()`) on already existing object.
Objects can be looked up by name using `.get()` and by id using `.by_id()`.

..note:: The objects in this module are available on the Teams Plan
"""

import json
import pickle
import typing as t
from pathlib import Path
from typing import Optional

# TODO - import only during type checking and import future.annotations when dropping py 3.6
import pandas as pd
from furl import furl

from datapane import __version__
from datapane.client.scripts import DatapaneCfg
from datapane.common import JSON, PKL_MIMETYPE, ArrowFormat, NPath, SDict
from datapane.common.datafiles import df_ext_map

from ..utils import DPError
from .common import DPTmpFile, do_download_file
from .dp_object import DPObjectRef, save_df

__all__ = ["Blob", "Variable", "Script", "Schedule"]

__pdoc__ = {
    "Blob.endpoint": False,
    "Script.endpoint": False,
    "Variable.endpoint": False,
    "Schedule.endpoint": False,
    # most script parameters we ignore
    "Script.call": False,
    "Script.upload_pkg": False,
    "Script.download_pkg": False,
    "Script.run": False,
    "Script.local_run": False,
}


class Blob(DPObjectRef):
    """
    Blobs are files that can be uploaded and downloaded for use in your scripts,
    for instance trained models, datasets, and (pickled) Python objects.
    They are generally large, but can be any size.

    Attributes:
        content_type: the blob content-type
        size_bytes: the blob size
        num_rows: number of rows in the file (if a dataframe)
        num_colums: number of colums in the file (if a dataframe)
        cells: number of cells in the file (if a dataframe)

    ..tip:: Use the static methods to create `Blobs` rather than the constructor
    """

    endpoint: str = "/blobs/"

    @classmethod
    def upload_df(cls, df: pd.DataFrame, **kwargs) -> "Blob":
        """
        Create a blob containing the dataframe provided

        Args:
            df: The pandas dataframe to upload as a Blob

        Returns:
            An instance of the created `Blob` object
        """
        with save_df(df) as fn:
            return cls.post_with_files(file=fn.file, **kwargs)

    @classmethod
    def upload_file(cls, fn: NPath, **kwargs) -> "Blob":
        """
        Create a blob containing the contents of the file provided

        Args:
            fn: Path to the file to upload as a Blob

        Returns:
            An instance of the created `Blob` object
        """
        return cls.post_with_files(file=Path(fn), **kwargs)

    @classmethod
    def upload_obj(cls, data: t.Any, as_json: bool = False, **kwargs: JSON) -> "Blob":
        """
        Create a blob containing the contents of the Python object provided,
        the object may be pickled or converted to JSON before storing.

        Args:
            data: Python object to upload as a Blob
            as_json: Convert the data to JSON rather than pickling (optional)

        Returns:
            An instance of the created `Blob` object
        """
        # import here as a very slow module due to nested imports
        from .files import save

        fn = save(data, default_to_json=as_json)
        return cls.post_with_files(file=fn.file, **kwargs)

    def download_df(self) -> pd.DataFrame:
        """
        Download the blob and return it as a Dataframe

        Returns:
            A pandas dataframe generated from the blob
        """
        with DPTmpFile(ArrowFormat.ext) as fn:
            do_download_file(self.gcs_signed_url, fn.name)
            return ArrowFormat.load_file(fn.name)

    def download_file(self, fn: NPath) -> None:
        """
        Download the blob to the file provided

        Args:
            fn: Path representing the location to save the file
        """
        fn = Path(fn)

        def get_export_format() -> str:
            ext = fn.suffix
            if ext not in df_ext_map:
                raise DPError(
                    f"Extension {ext} not valid for exporting table. Must be one of {', '.join(df_ext_map.keys())}"
                )
            return df_ext_map[ext].enum

        # If file is of arrow type, export it. Otherwise use the gcs url directly.
        if self.content_type == ArrowFormat.content_type:
            # TODO - export_url should include the host
            x = furl(self.export_url)
            x.args["export_format"] = get_export_format()
            x.origin = furl(self.url).origin
            download_url = x.url
        else:
            download_url = self.gcs_signed_url
        do_download_file(download_url, fn)

    def download_obj(self) -> t.Any:
        """
        Download the blob and return it as a Python object

        Returns:
            The object created by deserialising the Blob (either via Pickle or JSON decoding)
        """
        with DPTmpFile(".obj") as fn:
            do_download_file(self.gcs_signed_url, fn.name)
            # In the case that the original object was a Python object or bytes-like object,
            # the downloaded obj will be a pickle which needs to be unpickled.
            # Otherwise it's a stringified JSON object (e.g. an Altair plot) that can be returned as JSON.
            if self.content_type == PKL_MIMETYPE:
                with fn.file.open("rb") as fp:
                    return pickle.load(fp)
            else:
                return json.loads(fn.file.read_text())


class Variable(DPObjectRef):
    """
    User Variables represent secure pieces of data, such as tokens, database connection strings, etc. that are needed inside your scripts

    ..tip:: Use the static methods to create `Variables` rather than the constructor

    Attributes:
        name: Name of the variable
        value: Value of the variable
    """

    endpoint: str = "/uservariables/"
    list_fields = ["name"]

    @classmethod
    def create(cls, name: str, value: str, visibility: Optional[str] = "ORG") -> "Variable":
        """
        Create a shareable Datapane User Variable with provided `name` and `value`

        Args:
            name: Name of the variable
            value: Value of the variable
            visibility: one of `"PUBLIC"`, `"ORG"`, or `"PRIVATE"` (optional)

        Returns:
            An instance of the created `Variable` object
        """
        return cls.post(name=name, value=value, visibility=visibility)


class Script(DPObjectRef):
    """
    Scripts allow users to build, deploy, and automate data-driven Python workflows and apps
    to their cloud that can be customised and run by other users.

    ..tip:: We recommend using either the Web UI or CLI, e.g. `datapane script deploy / run / ...` to work with scripts rather than using the low-level API
    """

    endpoint: str = "/scripts/"

    @classmethod
    def upload_pkg(cls, sdist: Path, dp_cfg: DatapaneCfg, **kwargs) -> "Script":
        # TODO - use DPTmpFile
        # merge all the params for the API-call
        kwargs["api_version"] = __version__
        new_kwargs = {**dp_cfg.to_dict(), **kwargs}
        return cls.post_with_files(file=sdist, **new_kwargs)

    def download_pkg(self) -> Path:
        fn = do_download_file(self.gcs_signed_url)
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
        return Run.post(script=self.url, parameter_vals=parameters, cache=cache)

    def local_run(self, parameters=None) -> "Run":
        """(local) run the given script"""
        # NOTE -is there a use-case for this?
        raise NotImplementedError()


class Run(DPObjectRef):
    """
    Runs represent the running of a script, indicating their status, output, errors, etc.

    ..tip:: We recommend using either the Web UI or CLI, e.g. `datapane script run / ...` to work with runs rather than the low-level API
    """

    endpoint: str = "/runs/"

    def is_complete(self) -> bool:
        """Return true if the run has finished"""
        return self.status in ["SUCCESS", "ERROR", "CANCELLED"]


class Schedule(DPObjectRef):
    """
    Runs represent the running of a script, indicating their status, output, errors, etc.

    ..tip:: We recommend using the CLI, e.g. `datapane schedule create / ...` to work with schedules rather than the low-level API
    """

    endpoint: str = "/schedules/"
    list_fields = ["id", "script", "cron", "parameter_vals"]

    @classmethod
    def create(cls, script: Script, cron: str, parameters: SDict) -> "Schedule":
        return cls.post(script=script.url, cron=cron, parameter_vals=parameters)

    def update(self, cron: str = None, parameters: SDict = None) -> None:
        super().update(cron=cron, parameter_vals=parameters)
