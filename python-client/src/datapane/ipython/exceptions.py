from __future__ import annotations

from datapane.client import display_msg


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
