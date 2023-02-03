"""
## Datapane Teams API

Datapane Teams includes features to automate your Python workflows and easily build and share data-driven apps and results with your teams.

Generally objects are created on the server via the static methods (rather than the constructor),
and the instance methods and fields are used to access values (e.g. `.name`) and behaviour (e.g. `delete()`) on already existing object.
Objects can be looked up by name using `.get()` and by id using `.by_id()`.
"""
from __future__ import annotations

import typing as t
from contextlib import ExitStack
from pathlib import Path
from typing import Optional

from datapane import __version__
from datapane.cloud_api.common import DPTmpFile, do_download_file
from datapane.cloud_api.dp_object import DPObjectRef
from datapane.common import NPath, SDict, SList, SSDict
from datapane.common.utils import dict_drop_empty
from datapane.legacy_apps import DatapaneCfg

if t.TYPE_CHECKING:
    pass

__all__ = ["Environment", "Schedule"]

__pdoc__ = {
    "File.endpoint": False,
    "LegacyApp.endpoint": False,
    "Environment.endpoint": False,
    "Schedule.endpoint": False,
    # most app parameters we ignore
    "LegacyApp.call": False,
    "LegacyApp.upload_pkg": False,
    "LegacyApp.download_pkg": False,
    "LegacyApp.run": False,
    "LegacyApp.local_run": False,
}


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
        overwrite: bool = False,
    ) -> Environment:
        """
        Create a shareable Datapane Environment with provided `name`, `environment` and `docker_image`

        Args:
            name: Name of the environment
            environment: Key-value pair of environment variables
            docker_image: docker_image to be used with apps.
            project: Project name (optional and only applicable for organisations)
            overwrite: Overwrite an existing environment

        Returns:
            An instance of the created `Environment` object
        """
        assert environment or docker_image, "environment or docker image must be set"

        opt_fields = dict_drop_empty(
            none_only=True,
            environment=environment,
            docker_image=docker_image,
            project=project,
        )

        return cls.post(name=name, overwrite=overwrite, **opt_fields)


def get_app_file_params(params: t.List[SDict]) -> t.List[str]:
    """
    Returns the list of App param names that are of type `file`
    """
    return [p["name"] for p in params if p["type"] == "file"]


class LegacyApp(DPObjectRef):
    """
    Apps allow users to build, deploy, and automate data-driven Python workflows and apps
    to their cloud that can be customised and run by other users.

    ..tip:: We recommend using either the Web UI or CLI, e.g. `datapane app deploy / run / ...` to work with apps rather than using the low-level API
    """

    endpoint: str = "/apps/"

    @classmethod
    def upload_pkg(cls, sdist: Path, dp_cfg: DatapaneCfg, overwrite: bool = False, **kwargs) -> LegacyApp:
        # TODO - use DPTmpFile
        # merge all the params for the API-call
        merged_args = {**dp_cfg.to_dict(), **kwargs}
        opt_params = dict_drop_empty(none_only=True, api_version=__version__, **merged_args)
        return cls.post_with_files(file=sdist, overwrite=overwrite, **opt_params)

    def download_pkg(self) -> Path:
        fn = do_download_file(self.data_url)
        return Path(fn)

    def call(self, env: SSDict, **params):
        """Download, install, and call the app with the provided params"""
        # NOTE - use __call__??
        # TODO - move exec_script here?
        # TODO - call should handle param defaults
        from datapane.client.api.common import do_download_file
        from datapane.runner.exec_script import run

        with ExitStack() as stack:
            # get uploaded file params
            file_fieldnames: SList = get_app_file_params(self.parameters)
            user_file_params: SDict = {k: v for k, v in params.items() if k in file_fieldnames}

            # download each file into appropriate field
            for name, fn_remote in user_file_params.items():
                if fn_remote:
                    extension = f".{fn_remote.split('.')[-1]}"
                    fn_tmp: DPTmpFile = stack.enter_context(DPTmpFile(extension))
                    fn_downloaded: NPath = do_download_file(fn_remote, fn_tmp.full_name)
                    params[name] = Path(fn_downloaded)
                else:
                    params[name] = None

            run(self, params, env)

    def run(self, parameters: t.Dict[str, t.Any] = None, cache: bool = True) -> Run:
        """(remote) run the given app (cloning if needed?)"""
        parameters = parameters or dict()
        return Run.post(app=self.url, parameter_vals=parameters, cache=cache)

    def local_run(self, parameters=None) -> Run:  # noqa: ANN001
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
    def create(cls, app: LegacyApp, cron: str, parameters: SDict) -> Schedule:
        return cls.post(app=app.url, cron=cron, parameter_vals=parameters)

    # NOTE - mypy doesn't like this method because the signature is different from super type
    # potentially we may need to change it
    def update(self, cron: str = None, parameters: SDict = None) -> None:  # type: ignore
        opt_params = dict_drop_empty(cron=cron, parameter_vals=parameters)
        super().update(**opt_params)
