"""
## Datapane Teams API

Datapane Teams includes features to automate your Python workflows and easily build and share data-driven apps and results with your teams.

Generally objects are created on the server via the static methods (rather than the constructor),
and the instance methods and fields are used to access values (e.g. `.name`) and behaviour (e.g. `delete()`) on already existing object.
Objects can be looked up by name using `.get()` and by id using `.by_id()`.

..note:: The objects in this module are available on the Starter and Pro Teams Plans
"""
from __future__ import annotations

import json
import pickle
import typing as t
from pathlib import Path
from typing import Optional

from datapane import __version__
from datapane.client.apps import DatapaneCfg
from datapane.common import JSON, PKL_MIMETYPE, ArrowFormat, NPath, SDict, SSDict
from datapane.common.datafiles import DFFormatterCls, df_ext_map

from ..utils import DPError
from .common import DPTmpFile, do_download_file
from .dp_object import DPObjectRef, save_df

if t.TYPE_CHECKING:
    import pandas as pd

__all__ = ["File", "Environment", "App", "Schedule"]

__pdoc__ = {
    "File.endpoint": False,
    "App.endpoint": False,
    "Environment.endpoint": False,
    "Schedule.endpoint": False,
    # most app parameters we ignore
    "App.call": False,
    "App.upload_pkg": False,
    "App.download_pkg": False,
    "App.run": False,
    "App.local_run": False,
}


class File(DPObjectRef):
    """
    Files are files that can be uploaded and downloaded for use in your apps,
    for instance trained models, datasets, and (pickled) Python objects.
    They are generally large, but can be any size.

    Attributes:
        content_type: the file content-type
        size_bytes: the file size
        num_rows: number of rows in the file (if a dataframe)
        num_colums: number of colums in the file (if a dataframe)
        cells: number of cells in the file (if a dataframe)

    ..tip:: Use the static methods to create `Files` rather than the constructor
    """

    endpoint: str = "/files/"

    @classmethod
    def upload_df(cls, df: pd.DataFrame, **kwargs) -> File:
        """
        Create a file containing the dataframe provided

        Args:
            df: The pandas dataframe to upload as a File

        Returns:
            An instance of the created `File` object
        """
        with save_df(df) as fn:
            return cls.post_with_files(file=fn.file, **kwargs)

    @classmethod
    def upload_file(cls, fn: NPath, **kwargs) -> File:
        """
        Create a file containing the contents of the file provided

        Args:
            fn: Path to the file to upload as a File

        Returns:
            An instance of the created `File` object
        """
        return cls.post_with_files(file=Path(fn), **kwargs)

    @classmethod
    def upload_obj(cls, data: t.Any, **kwargs: JSON) -> File:
        """
        Create a file containing the contents of the Python object provided,
        the object may be pickled or converted to JSON before storing.

        Args:
            data: Python object to upload as a File

        Returns:
            An instance of the created `File` object
        """
        # import here as a very slow module due to nested imports
        from .files import save

        fn = save(data)
        return cls.post_with_files(file=fn.file, **kwargs)

    def download_df(self) -> pd.DataFrame:
        """
        Download the file and return it as a Dataframe

        Returns:
            A pandas dataframe generated from the file
        """
        with DPTmpFile(ArrowFormat.ext) as fn:
            do_download_file(self.data_url, fn.name)
            return ArrowFormat.load_file(fn.name)

    def download_file(self, fn: NPath) -> None:
        """
        Download the file to the file provided

        Args:
            fn: Path representing the location to save the file
        """
        fn = Path(fn)

        def get_export_format() -> DFFormatterCls:
            ext = fn.suffix
            if ext not in df_ext_map:
                raise DPError(
                    f"Extension {ext} not valid for exporting table. Must be one of {', '.join(df_ext_map.keys())}"
                )
            return df_ext_map[ext]

        # If file is of arrow type, export it. Otherwise download the url directly.
        if self.content_type == ArrowFormat.content_type:
            # download as a arrow->df, then export on the client
            df = self.download_df()
            fmt = get_export_format()
            fmt.save_file(str(fn), df)
        else:
            do_download_file(self.data_url, fn)

    def download_obj(self) -> t.Any:
        """
        Download the file and return it as a Python object

        Returns:
            The object created by deserialising the File (either via Pickle or JSON decoding)
        """
        with DPTmpFile(".obj") as fn:
            do_download_file(self.data_url, fn.name)
            # In the case that the original object was a Python object or bytes-like object,
            # the downloaded obj will be a pickle which needs to be unpickled.
            # Otherwise it's a stringified JSON object (e.g. an Altair plot) that can be returned as JSON.
            if self.content_type == PKL_MIMETYPE:
                with fn.file.open("rb") as fp:
                    return pickle.load(fp)
            else:
                return json.loads(fn.file.read_text())


class Environment(DPObjectRef):
    """
    Environments are used to set environment variables and an optional docker image for running your apps

    ..tip:: Use the static methods to create `Environment` rather than the constructor

    Attributes:
        name: Name of the environment
        environment: Key-value pair of environment variables
        docker_image: docker_image to be used with apps.
        project: Project name (optional and only applicable for organisations)
    """

    endpoint: str = "/environments/"
    list_fields = ["name", "project"]

    @classmethod
    def create(
        cls,
        name: str,
        environment: Optional[dict] = None,
        docker_image: Optional[str] = None,
        project: Optional[str] = None,
    ) -> Environment:
        """
        Create a shareable Datapane Environment with provided `name`, `environment` and `docker_image`

        Args:
            name: Name of the environment
            environment: Key-value pair of environment variables
            docker_image: docker_image to be used with apps.
            project: Project name (optional and only applicable for organisations)

        Returns:
            An instance of the created `Environment` object
        """
        assert environment or docker_image, "environment or docker image must be set"
        return cls.post(name=name, environment=environment, docker_image=docker_image, project=project)


class App(DPObjectRef):
    """
    Apps allow users to build, deploy, and automate data-driven Python workflows and apps
    to their cloud that can be customised and run by other users.

    ..tip:: We recommend using either the Web UI or CLI, e.g. `datapane app deploy / run / ...` to work with apps rather than using the low-level API
    """

    endpoint: str = "/apps/"

    @classmethod
    def upload_pkg(cls, sdist: Path, dp_cfg: DatapaneCfg, **kwargs) -> App:
        # TODO - use DPTmpFile
        # merge all the params for the API-call
        kwargs["api_version"] = __version__
        new_kwargs = {**dp_cfg.to_dict(), **kwargs}
        return cls.post_with_files(file=sdist, **new_kwargs)

    def download_pkg(self) -> Path:
        fn = do_download_file(self.data_url)
        return Path(fn)

    def call(self, env: SSDict, **params):
        """Download, install, and call the app with the provided params"""
        # NOTE - use __call__??
        # TODO - move exec_script here?
        # TODO - call should handle param defaults
        from datapane.runner.exec_script import run

        run(self, params, env)

    def run(self, parameters=None, cache=True) -> Run:
        """(remote) run the given app (cloning if needed?)"""
        parameters = parameters or dict()
        return Run.post(app=self.url, parameter_vals=parameters, cache=cache)

    def local_run(self, parameters=None) -> Run:
        """(local) run the given app"""
        # NOTE -is there a use-case for this?
        raise NotImplementedError()


class Run(DPObjectRef):
    """
    Runs represent the running of a app, indicating their status, output, errors, etc.

    ..tip:: We recommend using either the Web UI or CLI, e.g. `datapane app run / ...` to work with runs rather than the low-level API
    """

    endpoint: str = "/runs/"

    def is_complete(self) -> bool:
        """Return true if the run has finished"""
        return self.status in ["SUCCESS", "ERROR", "CANCELLED"]


class Schedule(DPObjectRef):
    """
    Runs represent the running of a app, indicating their status, output, errors, etc.

    ..tip:: We recommend using the CLI, e.g. `datapane schedule create / ...` to work with schedules rather than the low-level API
    """

    endpoint: str = "/schedules/"
    list_fields = ["id", "app", "cron", "parameter_vals"]

    @classmethod
    def create(cls, app: App, cron: str, parameters: SDict) -> Schedule:
        return cls.post(app=app.url, cron=cron, parameter_vals=parameters)

    def update(self, cron: str = None, parameters: SDict = None) -> None:
        super().update(cron=cron, parameter_vals=parameters)
