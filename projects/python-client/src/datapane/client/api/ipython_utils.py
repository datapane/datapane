from __future__ import annotations

import json
import typing

if typing.TYPE_CHECKING:
    from .report.blocks import BaseElement

"""
Datapane helper functions to improve the Datapane UX in Jupyter notebooks
"""


def block_to_iframe(block: BaseElement) -> str:
    """Convert a Block to HTML, placed within an iFrame

    Args:
        block: Datapane Block to convert

    Returns:
        HTML string for the block
    """
    # importing within function scope to avoid circular dependency
    from .report.core import App

    app = App(block)
    block_html_string = app.stringify(template_name="ipython_template.html")

    return block_html_string


def cell_to_block(cell: dict) -> BaseElement:
    """Convert a Jupyter notebook cell to a Datapane Block

    Args:
        cell: Jupyter notebook cell dict

    Returns:
        Datapane Block
    """
    # TODO
    pass


def cells_to_blocks(jupyter_output_cache: dict) -> list:
    """Convert Jupyter notebook cells to a list of Datapane Blocks

    Args:
        jupyter_output_cache: The output cache (Out or _oh) dict from a Jupyter notebook

    Returns:
        List of Datapane Blocks
    """
    import ipynbname

    nb_path = ipynbname.path()

    blocks = []
    notebook_json = json.loads(open(nb_path, encoding="utf-8").read())

    for cell in notebook_json["cells"]:
        tags = cell["metadata"].get("tags", [])

        if cell["cell_type"] == "markdown":
            from .report.blocks import Text

            block = Text("".join(cell["source"]))
            blocks.append(block)

        elif cell["cell_type"] == "code":
            from .report.blocks import Code

            if "show-code" in tags:
                block = Code("".join(cell["source"]))
                blocks.append(block)

            block = cell_to_block(cell)
            if block:
                blocks.append(block)

    return blocks
