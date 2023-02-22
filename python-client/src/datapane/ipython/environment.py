from __future__ import annotations

import io
import json
import os
import sys
import typing as t
from functools import cached_property
from pathlib import Path

from datapane.client import log
from datapane.client.exceptions import DPClientError

from .exceptions import NotebookException

if t.TYPE_CHECKING:
    from IPython.core.interactiveshell import InteractiveShell

__all__ = ("get_environment",)


_env = None


def get_environment() -> PythonEnvironment:
    """Returns the current IPython environment"""
    global _env
    if _env is None:
        _env = _get_environment()
        log.info("Detected IPython environment: %s", _env.name)
    return _env


def _get_ipython() -> t.Optional[InteractiveShell]:
    try:
        return get_ipython()  # type: ignore
    except NameError:
        from IPython import get_ipython

        return get_ipython()


def is_zqm_interactive_shell() -> bool:
    """Check if we are running in a ZMQ interactive shell"""
    return _get_ipython().__class__.__name__ == "ZMQInteractiveShell"


def is_terminal_interactive_shell() -> bool:
    """Check if we are running in a terminal interactive shell"""
    return _get_ipython().__class__.__name__ == "TerminalInteractiveShell"


def get_ipython_user_ns() -> dict:
    return _get_ipython().user_ns


def _get_environment() -> PythonEnvironment:
    """Determines the current IPython environment and returns an instance of the appropriate class"""

    # TODO: change this to be a list, and put the logic in a `.supported()` method
    if "google.colab" in sys.modules:
        return ColabEnvironment()
    elif {"CODESPACES", "JUPYTERLAB_PATH", "VSCODE_CWD"}.issubset(set(os.environ)):
        return CodespacesVSCodeJupyterEnvironment()
    elif {"CODESPACES", "JUPYTERLAB_PATH", "JPY_PARENT_PID"}.issubset(set(os.environ)):
        return CodespacesJupyterLabEnvironment()
    elif is_zqm_interactive_shell() and "PAPERMILL_OUTPUT_PATH" in get_ipython_user_ns():
        return PapermillEnvironment()
    elif is_zqm_interactive_shell() and "VSCODE_PID" in os.environ:
        return VSCodeJupyterEnvironment()
    elif is_zqm_interactive_shell() and {"JPY_SESSION_NAME", "JPY_PARENT_PID"}.issubset(set(os.environ)):
        return JupyterLabEnvironment()
    elif is_zqm_interactive_shell() and "JPY_PARENT_PID" in os.environ:
        return JupyterNotebookEnvironment()
    elif is_zqm_interactive_shell():
        return UnsupportedNotebookEnvironment()
    elif "PYCHARM_HOSTED" in os.environ:
        return PyCharmEnvironment()
    elif "VSCODE_PID" in os.environ:
        return VSCodeEnvironment()
    elif is_terminal_interactive_shell():
        return IPythonTerminalEnvironment()
    else:
        return UnrecognizedEnvironment()


class PythonEnvironment:
    name: str = "Python Environment"
    can_open_links_from_python: bool = True
    is_notebook_environment: bool = False
    support_rich_display: bool = True
    supports_ipywidgets: bool = False

    get_ipython = staticmethod(_get_ipython)

    def get_notebook_json(self) -> dict:
        try:
            path = self._get_notebook_path()
            with open(path, encoding="utf-8") as f:
                notebook_json = json.load(f)
        except FileNotFoundError:
            raise DPClientError(
                "Notebook not found. This command must be executed from within a Jupyter notebook environment."
            )
        return notebook_json

    def _get_notebook_path(self) -> Path:
        """Get the path to the current notebook"""
        raise FileNotFoundError("Could not discover notebook path")


class UnrecognizedEnvironment(PythonEnvironment):
    name = "Unrecognized Environment"
    is_notebook_environment = False
    can_open_links_from_python = False


class IPythonTerminalEnvironment(PythonEnvironment):
    name = "IPython Terminal Environment"


class IPythonZMQEnvironment(IPythonTerminalEnvironment):
    name = "IPython ZMQ Environment"
    is_notebook_environment = True

    def _get_notebook_path(self) -> Path:
        # added in ipykernel v6.21
        # https://github.com/ipython/ipykernel/pull/1078
        user_ns = get_ipython_user_ns()

        # If it's an actual path, it'll always be absolute
        if (path := user_ns.get("__session__", None)) and path.startswith("/"):
            return Path(path)

        return super()._get_notebook_path()


class UnsupportedNotebookEnvironment(IPythonZMQEnvironment):
    name = "Unsupported Notebook Environment"


class PyCharmEnvironment(PythonEnvironment):
    name = "PyCharm Environment"
    support_rich_display = False


class VSCodeEnvironment(PythonEnvironment):
    name = "VSCode Environment"


class JupyterEnvironment(IPythonZMQEnvironment):
    name = "Jupyter Environment"
    supports_ipywidgets = True

    def _get_notebook_path(self):
        """Get the path for the current Jupyter notebook"""

        # ipynbname plays with the session API, so see if ipykernel gave us a better option
        try:
            return super()._get_notebook_path()
        except FileNotFoundError as e:
            import ipynbname

            try:
                return ipynbname.path()
            except IndexError:
                raise e


class JupyterLabEnvironment(JupyterEnvironment):
    name = "JupyterLab Environment"


class JupyterNotebookEnvironment(JupyterEnvironment):
    name = "Jupyter Notebook Environment"


class VSCodeJupyterEnvironment(JupyterEnvironment):
    name = "VSCode Jupyter Environment"

    # Attempting to use IPyWidgetsControllerUI from within VSCode Jupyter extension
    # seems extremely flakey:
    # - server often fails to start or stop
    # - once it has failed once, it can require restarting VSCode to fix things.
    # So it's better to fall back to something that seems to work better.
    #
    supports_ipywidgets = False

    def _get_notebook_path(self) -> Path:
        user_ns = get_ipython_user_ns()
        if vsc_path := user_ns.get("__vsc_ipynb_file__", None):
            return Path(vsc_path)

        # VSCode path name in sesssion may be suffixed with -jvsc-[identifier]
        # https://github.com/microsoft/vscode-jupyter/blob/113c3e54ac1d3cb81ab6473d1a5fa4a20cce4755/src/kernels/helpers.ts#L149-L168
        sessioned_nb_path = super()._get_notebook_path()
        suffix = sessioned_nb_path.suffix
        sans_suffix = sessioned_nb_path.with_suffix("")
        nb_path = Path(str(sans_suffix).split("-jvsc-")[0]).with_suffix(suffix)
        return nb_path


class ColabEnvironment(IPythonZMQEnvironment):
    name = "Google Colab Environment"

    def get_notebook_json(self) -> dict:
        """Get the JSON for the current Colab notebook"""
        import ipynbname
        from google.colab import auth
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseDownload

        # Get the notebook's Google Drive file_id
        file_id = ipynbname.name().replace("fileId=", "")

        try:
            auth.authenticate_user()
        except Exception as e:
            raise NotebookException(
                "Google Drive authentication failed. Please allow this notebook to access your Google Drive."
            ) from e

        drive_service = build("drive", "v3")

        request = drive_service.files().get_media(fileId=file_id)
        downloaded = io.BytesIO()
        downloader = MediaIoBaseDownload(downloaded, request)
        done = False
        while done is False:
            # _ is a placeholder for a progress object that we ignore.
            # (Our file is small, so we skip reporting progress.)
            _, done = downloader.next_chunk()

        downloaded.seek(0)
        notebook_json = json.loads(downloaded.read().decode("utf-8"))

        return notebook_json


class CodespacesVSCodeJupyterEnvironment(VSCodeJupyterEnvironment):
    name = "Codespaces VSCode Jupyter Environment"


class CodespacesJupyterLabEnvironment(JupyterLabEnvironment):
    name = "Codespaces JupyterLab Environment"
    can_open_links_from_python = False


class PapermillEnvironment(IPythonZMQEnvironment):
    name = "Papermill Environment"

    def _get_notebook_path(self) -> Path:
        user_ns = get_ipython_user_ns()
        if path := user_ns.get("PAPERMILL_OUTPUT_PATH", None):
            return Path(path)
        return super()._get_notebook_path()

    @cached_property
    def support_rich_display(self) -> bool:  # type: ignore[override]
        return get_ipython_user_ns().get("DP_SERVER_RUNNER", False)
