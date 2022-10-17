"""
Datapane helper functions to improve the Datapane UX in IPython notebooks
"""
from __future__ import annotations

import io
import json
import os
import typing
from pathlib import Path

from datapane.client import DPError
from datapane.client.analytics import capture_event
from datapane.client.utils import display_msg

if typing.TYPE_CHECKING:
    from .report.blocks import BaseElement, Code, Text


def block_to_iframe(block: BaseElement) -> str:
    """Convert a Block to HTML, placed within an iFrame

    Args:
        block: Datapane Block to convert

    Returns:
        HTML string for the block
    """
    from .report.core import App

    app = App(block)
    block_html_string = app.stringify(template_name="ipython_template.html")

    return block_html_string


def read_notebook_json(path: Path) -> dict:
    """Read a notebook IPYNB file

    Args:
        path: Path to the notebook IPYNB file

    Returns:
        Notebook JSON
    """
    with open(path, encoding="utf-8") as f:
        notebook_json = json.load(f)

    return notebook_json


@capture_event("Get Jupyter Notebook JSON")
def get_jupyter_notebook_json() -> dict:
    """Get the JSON for the current Jupyter notebook

    Returns:
        Notebook JSON
    """
    import ipynbname

    try:
        nb_path = ipynbname.path()
        notebook_json = read_notebook_json(nb_path)
    except FileNotFoundError as e:
        raise DPError(
            "Notebook not found. This command must be executed from within a Jupyter notebook environment."
        ) from e

    return notebook_json


@capture_event("Get VSCode Notebook JSON")
def get_vscode_notebook_json() -> dict:
    """Get the JSON for the current VSCode notebook

    Returns:
        Notebook JSON
    """
    import ipynbname

    try:
        nb_path = ipynbname.path()

        # VSCode path name in sesssion is suffixed with -jvsc-[identifier]
        nb_path = Path(str(nb_path.split("-jvsc-")[0] + ".ipynb"))

        notebook_json = read_notebook_json(nb_path)
    except FileNotFoundError as e:
        raise DPError("Notebook not found. This command must be executed from within a notebook environment.") from e

    return notebook_json


@capture_event("Get Colab Notebook JSON")
def get_colab_notebook_json() -> dict:
    """Get the JSON for the current Colab notebook

    Returns:
        Notebook JSON
    """
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
    """Get the JSON for the current Jupyter, Colab, or VSCode notebook

    Returns:
        Notebook JSON
    """
    from IPython import get_ipython

    if "COLAB_GPU" in os.environ:
        notebook_json = get_colab_notebook_json()
    elif "VSCODE_PID" in os.environ:
        notebook_json = get_vscode_notebook_json()
    elif get_ipython().__class__.__name__ == "ZMQInteractiveShell":
        notebook_json = get_jupyter_notebook_json()
    else:
        raise DPError("Can't detect notebook environment")

    return notebook_json


def markdown_cell_to_block(cell: dict) -> Text:
    """Convert a IPython notebook cell to a Datapane Text Block

    Args:
        cell: IPython notebook cell dict

    Returns:
        Datapane Block
    """
    from .report.blocks import Text

    block = Text("".join(cell["source"]))

    return block


def input_cell_to_block(cell: dict) -> Code:
    """Convert a IPython notebook cell to a Datapane Code Block

    Args:
        cell: IPython notebook cell dict

    Returns:
        Datapane Block
    """
    from .report.blocks import Code

    block = Code("".join(cell["source"]))

    return block


def output_cell_to_block(cell: dict, ipython_output_cache: dict) -> typing.Any[BaseElement, None]:
    """Convert a IPython notebook output cell to a Datapane Block

    Args:
        cell: IPython notebook cell dict

    Returns:
        Datapane Block
    """
    from .report.blocks import wrap_block

    # Get the output object from the IPython output cache
    cell_output_object = ipython_output_cache.get(cell["execution_count"], None)

    # If there's corresponding output object, skip
    if cell_output_object is None:
        return None

    try:
        block = wrap_block(cell_output_object)
        return block
    except Exception:
        return None


@capture_event("IPython Cells to Blocks")
def cells_to_blocks(ipython_output_cache: dict, opt_out: bool = True) -> typing.List[BaseElement]:
    """Convert IPython notebook cells to a list of Datapane Blocks

    Recognized cell tags:
        - `dp-exclude` - Exclude this cell (when opt_out=True)
        - `dp-include` - Include this cell (when opt_out=False)
        - `dp-show-code` - Show the input code for this cell

    Args:
        ipython_output_cache: The output cache (Out or _oh) dict from a IPython notebook
        opt_out: When True, all cells are converted to blocks unless explicitly opted out with the tag `dp-exclude`. When False, only cells with the tag `dp-include` are converted to blocks.

    Returns:
        List of Datapane Blocks

    ..note:: IPython output caching must be enabled for this function to work. It is enabled by default.
    """
    display_msg("Converting cells to blocks.")

    notebook_json = get_notebook_json()

    blocks = []

    for cell in notebook_json["cells"]:
        tags = cell["metadata"].get("tags", [])

        if (opt_out and "dp-exclude" not in tags) or (not opt_out and "dp-include" in tags):
            block = None  # type: typing.Any[BaseElement, None]

            if cell["cell_type"] == "markdown":
                block = markdown_cell_to_block(cell)
                blocks.append(block)

            elif cell["cell_type"] == "code":
                if "dp-show-code" in tags:
                    block = input_cell_to_block(cell)
                    blocks.append(block)

                if cells_to_blocks.__name__ not in "".join(cell["source"]):
                    block = output_cell_to_block(cell, ipython_output_cache)
                    if block:
                        blocks.append(block)
                    elif "dp-include" in tags:
                        display_msg(
                            f'Cell output of type {type(ipython_output_cache.get(cell["execution_count"]))} not supported. Skipping.',
                        )

    if not blocks:
        display_msg("No blocks found.")

    display_msg(
        "Please ensure all cells in the notebook have been executed and then saved before running this command."
    )

    return blocks
