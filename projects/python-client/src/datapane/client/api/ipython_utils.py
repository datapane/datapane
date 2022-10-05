"""
Datapane helper functions to improve the Datapane UX in Jupyter notebooks
"""
from __future__ import annotations

import io
import json
import os
import typing

from datapane.client.utils import display_msg
from requests import get

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

def get_jupyter_notebook_json() -> dict:
    """Get the JSON for the current Jupyter notebook

    Returns:
        Notebook JSON
    """
    import ipynbname

    nb_path = ipynbname.path()
    notebook_json = json.loads(open(nb_path, encoding="utf-8").read())

    return notebook_json

def get_colab_notebook_json() -> dict:
    """Get the JSON for the current Colab notebook

    Returns:
        Notebook JSON
    """
    from googleapiclient.http import MediaIoBaseDownload
    from googleapiclient.discovery import build
    from google.colab import auth

    # Get the notebook's Google Drive file_id 
    file_id = get('http://172.28.0.2:9000/api/sessions').json()[0]['path'].replace("fileId=","")

    auth.authenticate_user()
    drive_service = build('drive', 'v3')

    request = drive_service.files().get_media(fileId=file_id)
    downloaded = io.BytesIO()
    downloader = MediaIoBaseDownload(downloaded, request)
    done = False
    while done is False:
        # _ is a placeholder for a progress object that we ignore.
        # (Our file is small, so we skip reporting progress.)
        _, done = downloader.next_chunk()

    downloaded.seek(0)
    notebook_json = json.loads(downloaded.read().decode('utf-8'))

    return notebook_json

def get_notebook_json() -> dict:
    """Get the JSON for the current Colab or Jupyter notebook

    Returns:
        Notebook JSON
    """ 
    if 'COLAB_GPU' in os.environ:
        notebook_json = get_colab_notebook_json()
    else: 
        notebook_json = get_jupyter_notebook_json()

    return notebook_json

def markdown_cell_to_block(cell: dict) -> Text:
    """Convert a Jupyter notebook cell to a Datapane Text Block

    Args:
        cell: Jupyter notebook cell dict

    Returns:
        Datapane Block
    """
    from .report.blocks import Text

    block = Text("".join(cell["source"]))

    return block

def input_cell_to_block(cell: dict) -> Code:
    """Convert a Jupyter notebook cell to a Datapane Code Block

    Args:
        cell: Jupyter notebook cell dict

    Returns:
        Datapane Block
    """
    from .report.blocks import Code

    block = Code("".join(cell["source"]))

    return block

def output_cell_to_block(cell: dict, jupyter_output_cache: dict) -> BaseElement:
    """Convert a Jupyter notebook output cell to a Datapane Block

    Args:
        cell: Jupyter notebook cell dict

    Returns:
        Datapane Block
    """
    from .report.blocks import wrap_block

    # Get the output object from the Jupyter output cache
    cell_output_object = jupyter_output_cache.get(cell["execution_count"], None)

    # If there's corresponding output object, skip
    if cell_output_object is None:
        return None

    try:
        block = wrap_block(cell_output_object)
        return block
    except Exception as e:
        return None

def cells_to_blocks(jupyter_output_cache: dict, opt_out=True) -> list:
    """Convert Jupyter notebook cells to a list of Datapane Blocks

    Recognized cell tags:
        - `dp-exclude` - Exclude this cell (when opt_out=True)
        - `dp-include` - Include this cell (when opt_out=False)
        - `dp-show-code` - Show the input code for this cell

    Args:
        jupyter_output_cache: The output cache (Out or _oh) dict from a Jupyter notebook
        opt_out: When True, all cells are converted to blocks unless explicitly opted out with the tag `dp-exclude`. When False, only cells with the tag `dp-include` are converted to blocks.

    Returns:
        List of Datapane Blocks
    """
    display_msg(f"Converting cells to blocks.")
    display_msg(f"  Please make sure you have run all cells in the notebook before running this command.")

    notebook_json = get_notebook_json()

    blocks = []

    for cell in notebook_json["cells"]:
        tags = cell["metadata"].get("tags", [])

        if (opt_out and "dp-exclude" not in tags) or (not opt_out and "dp-include" in tags):

            if cell["cell_type"] == "markdown":
                block = markdown_cell_to_block(cell)
                blocks.append(block)

            elif cell["cell_type"] == "code":
                if "dp-show-code" in tags:
                    block = input_cell_to_block(cell)
                    blocks.append(block)

                block = output_cell_to_block(cell, jupyter_output_cache)
                if block:
                    blocks.append(block)

    return blocks
