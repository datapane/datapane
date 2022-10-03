from __future__ import annotations

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


def cells_to_blocks(jupyter_output_cache: dict) -> list:
    """Convert Jupyter notebook cells to a list of Datapane Blocks

    Args:
        jupyter_output_cache: The output cache (Out or _oh) dict from a Jupyter notebook

    Returns:
        List of Datapane Blocks
    """
    blocks = []
    return blocks
