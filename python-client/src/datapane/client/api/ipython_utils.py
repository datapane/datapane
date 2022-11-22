"""
Datapane helper functions to improve the Datapane UX in IPython notebooks
"""
from __future__ import annotations

import io
import json
import os
import sys
import typing
from contextlib import suppress
from pathlib import Path

from datapane.client import DPError
from datapane.client.analytics import capture_event
from datapane.client.utils import display_msg, is_jupyter

if typing.TYPE_CHECKING:
    from .report.blocks import BaseElement


class NotebookException(Exception):
    """Exception raised when a Notebook to Datapane conversion fails."""

    def _render_traceback_(self):
        display_msg(
            f"""**Conversion failed**

{str(self)}"""
        )


class NotebookParityException(NotebookException):
    """Exception raised when IPython output cache is not in sync with the saved notebook"""


class BlocksNotFoundException(NotebookException):
    """Exception raised when no blocks are found during conversion"""


def block_to_iframe(block: BaseElement) -> str:
    """Convert a Block to HTML, placed within an iFrame"""
    from .report.core import App

    app = App(block)
    block_html_string = app.stringify(template_name="ipython_template.html")

    return block_html_string


def read_notebook_json(path: Path) -> dict:
    """Read a notebook IPYNB file"""
    with open(path, encoding="utf-8") as f:
        notebook_json = json.load(f)

    return notebook_json


def get_jupyter_notebook_json() -> dict:
    """Get the JSON for the current Jupyter notebook"""
    import ipynbname

    try:
        nb_path = ipynbname.path()
        notebook_json = read_notebook_json(nb_path)
    except IndexError:
        raise DPError("Environment not supported.")
    except FileNotFoundError as e:
        raise DPError(
            "Notebook not found. This command must be executed from within a Jupyter notebook environment."
        ) from e

    return notebook_json


def get_vscode_notebook_json() -> dict:
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
        notebook_json = read_notebook_json(nb_path)
    except FileNotFoundError as e:
        raise DPError("Notebook not found. This command must be executed from within a notebook environment.") from e

    return notebook_json


def get_colab_notebook_json() -> dict:
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
        raise DPError(
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


def get_notebook_json() -> dict:
    """Get the JSON for the current Jupyter, Colab, or VSCode notebook"""
    if "google.colab" in sys.modules:
        notebook_json = get_colab_notebook_json()
    elif "VSCODE_PID" in os.environ:
        notebook_json = get_vscode_notebook_json()
    elif is_jupyter():
        notebook_json = get_jupyter_notebook_json()
    else:
        raise DPError("Can't detect notebook environment")

    return notebook_json


def output_cell_to_block(cell: dict, ipython_output_cache: dict) -> typing.Optional[BaseElement]:
    """Convert a IPython notebook output cell to a Datapane Block"""
    from .report.blocks import wrap_block

    # Get the output object from the IPython output cache
    cell_output_object = ipython_output_cache.get(cell["execution_count"], None)

    # If there's no corresponding output object, skip
    if cell_output_object is not None:
        with suppress(Exception):
            return wrap_block(cell_output_object)

    return None


def check_notebook_cache_parity(notebook_json: dict, ipython_input_cache: list) -> typing.Tuple[bool, typing.List[int]]:
    """Check that the IPython output cache is in sync with the saved notebook"""
    is_dirty = False
    dirty_cells: typing.List[int] = []

    # inline !bang commands (get_ipython().system), %line magics, and %%cell magics are not cached
    # exclude these from conversion
    ignored_cell_functions = ["get_ipython().system", "get_ipython().run_line_magic", "get_ipython().run_cell_magic"]

    # broad check: check the execution count is the same
    execution_counts = [cell.get("execution_count", 0) or 0 for cell in notebook_json["cells"]]

    latest_cell_execution_count = max(execution_counts)

    # -2 to account for zero-based indexing and the invoking cell not being saved
    latest_cache_execution_count = len(ipython_input_cache) - 2
    if latest_cache_execution_count != latest_cell_execution_count:
        is_dirty = True
        return is_dirty, dirty_cells

    # narrow check: check the cell source is the same for executed cells
    for cell in notebook_json["cells"]:
        cell_execution_count = cell.get("execution_count", None)
        if cell["cell_type"] == "code" and cell_execution_count:
            if cell_execution_count < len(ipython_input_cache):
                input_cache_source = ipython_input_cache[cell_execution_count]

                # skip and mark cells containing ignored functions
                if any(ignored_function in input_cache_source for ignored_function in ignored_cell_functions):
                    cell["contains_ignored_functions"] = True
                # dirty because input has changed between execution and save.
                elif "".join(cell["source"]) != input_cache_source:
                    is_dirty = True
                    dirty_cells.append(cell_execution_count)

    return is_dirty, dirty_cells


@capture_event("IPython Cells to Blocks")
def cells_to_blocks(opt_out: bool = True) -> typing.List[BaseElement]:
    """Convert IPython notebook cells to a list of Datapane Blocks

    Recognized cell tags:
        - `dp-exclude` - Exclude this cell (when opt_out=True)
        - `dp-include` - Include this cell (when opt_out=False)
        - `dp-show-code` - Show the input code for this cell

    ..note:: IPython output caching must be enabled for this function to work. It is enabled by default.
    """
    from IPython import get_ipython

    ip = get_ipython()
    user_ns = ip.user_ns
    ipython_output_cache = user_ns["_oh"]
    ipython_input_cache = user_ns["_ih"]

    notebook_json = get_notebook_json()

    notebook_is_dirty, dirty_cells = check_notebook_cache_parity(notebook_json, ipython_input_cache)

    if notebook_is_dirty:
        notebook_parity_message = (
            "Please ensure all cells in the notebook have been executed and saved before running the conversion."
        )

        if dirty_cells:
            notebook_parity_message += f"""

The following cells have not been executed and saved: {''.join(map(str, dirty_cells))}"""

        raise NotebookParityException(notebook_parity_message)

    blocks = []

    for cell in notebook_json["cells"]:
        tags = cell["metadata"].get("tags", [])

        if (opt_out and "dp-exclude" not in tags) or (not opt_out and "dp-include" in tags):
            if cell["cell_type"] == "markdown":
                from .report.blocks import Text

                markdown_block: BaseElement = Text("".join(cell["source"]))
                blocks.append(markdown_block)
            elif cell["cell_type"] == "code" and not cell.get("contains_ignored_functions", False):
                if "dp-show-code" in tags:
                    from .report.blocks import Code

                    code_block: BaseElement = Code("".join(cell["source"]))
                    blocks.append(code_block)

                output_block = output_cell_to_block(cell, ipython_output_cache)
                if output_block:
                    blocks.append(output_block)
                elif "dp-include" in tags:
                    display_msg(
                        f'Cell output of type {type(ipython_output_cache.get(cell["execution_count"]))} not supported. Skipping.',
                    )

    if not blocks:
        raise BlocksNotFoundException("No blocks found.")

    display_msg("Notebook converted to blocks.")

    return blocks
