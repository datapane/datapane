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
    iframe_html_string = app.stringify(template_name="ipython_template.html")

    return iframe_html_string
