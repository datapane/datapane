from __future__ import annotations

import io
import json
import os
import sys
from pathlib import Path

from datapane.client.exceptions import NotebookException
from datapane.common import DPError


def is_zqm_interactive_shell() -> bool:
    """Check if we are running in a ZMQ interactive shell"""
    try:
        from IPython import get_ipython

        return bool(get_ipython().__class__.__name__ == "ZMQInteractiveShell")
    except NameError:
        return False


def is_terminal_interactive_shell() -> bool:
    """Check if we are running in a terminal interactive shell"""
    try:
        from IPython import get_ipython

        return bool(get_ipython().__class__.__name__ == "TerminalInteractiveShell")
    except NameError:
        return False


def get_environment() -> PythonEnvironment:
    """Determines the current IPython environment and returns an instance of the appropriate class"""
    if "google.colab" in sys.modules:
        return ColabEnvironment()
    elif {"CODESPACES", "JUPYTERLAB_PATH", "VSCODE_CWD"}.issubset(set(os.environ)):
        return CodespacesVSCodeJupyterEnvironment()
    elif {"CODESPACES", "JUPYTERLAB_PATH", "JPY_PARENT_PID"}.issubset(set(os.environ)):
        return CodespacesJupyterLabEnvironment()
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

    def get_notebook_json(self) -> dict:
        raise DPError("The current notebook environment is not supported.")


class IPythonZQMEnvironment(PythonEnvironment):
    name = "IPython ZQM Environment"
    is_notebook_environment = True


class IPythonTerminalEnvironment(PythonEnvironment):
    name = "IPython Terminal Environment"
    is_notebook_environment = False


class UnrecognizedEnvironment(PythonEnvironment):
    name = "Unrecognized Environment"
    is_notebook_environment = False
    can_open_links_from_python = False


class PyCharmEnvironment(PythonEnvironment):
    name = "PyCharm Environment"


class VSCodeEnvironment(PythonEnvironment):
    name = "VSCode Environment"


class UnsupportedNotebookEnvironment(IPythonZQMEnvironment):
    name = "Unsupported Notebook Environment"


class JupyterLabEnvironment(IPythonZQMEnvironment):
    name = "JupyterLab Environment"

    def get_notebook_json(self) -> dict:
        """Get the JSON for the current Jupyter notebook"""
        import ipynbname

        try:
            nb_path = ipynbname.path()
            with open(nb_path, encoding="utf-8") as f:
                notebook_json = json.load(f)
        except IndexError:
            raise DPError("Environment not supported.")
        except FileNotFoundError as e:
            raise DPError(
                "Notebook not found. This command must be executed from within a Jupyter notebook environment."
            ) from e

        return notebook_json


class JupyterNotebookEnvironment(JupyterLabEnvironment):
    name = "Jupyter Notebook Environment"


class VSCodeJupyterEnvironment(IPythonZQMEnvironment):
    name = "VSCode Jupyter Environment"

    def get_notebook_json(self) -> dict:
        """Get the JSON for the current VSCode notebook"""
        from IPython import get_ipython

        ip = get_ipython()

        if "__vsc_ipynb_file__" in ip.user_ns:
            nb_path = ip.user_ns["__vsc_ipynb_file__"]
        else:
            import ipynbname

            try:
                nb_path = ipynbname.path()

                # VSCode path name in sesssion is suffixed with -jvsc-[identifier]
                nb_path = Path(str(nb_path).split("-jvsc-")[0] + ".ipynb")
            except Exception as e:
                raise DPError("Environment not supported.") from e

        try:
            with open(nb_path, encoding="utf-8") as f:
                notebook_json = json.load(f)

        except FileNotFoundError as e:
            raise DPError(
                "Notebook not found. This command must be executed from within a notebook environment."
            ) from e

        return notebook_json


class ColabEnvironment(IPythonZQMEnvironment):
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


environment = get_environment()
