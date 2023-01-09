"""
Datapane Reports Object

Describes the `Report` object
"""

from __future__ import annotations

import dataclasses as dc
import os
import typing as t
from enum import Enum
from pathlib import Path
from uuid import uuid4

from datapane import __version__ as dp_version
from datapane.client.api.common import DPTmpFile
from datapane.client.api.dp_object import DPObjectRef
from datapane.client.exceptions import DPError

from .blocks import BlockOrPrimitive, Page, PageOrPrimitive

CDN_BASE: str = os.getenv("DATAPANE_CDN_BASE", f"https://datapane-cdn.com/v{dp_version}")

# only these types will be documented by default
__all__ = ["App", "AppWidth"]

__pdoc__ = {
    "App.endpoint": False,
}


class AppWidth(Enum):
    NARROW = "narrow"
    MEDIUM = "medium"
    FULL = "full"


class TextAlignment(Enum):
    JUSTIFY = "justify"
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"


class FontChoice(Enum):
    DEFAULT = "Inter var, ui-sans-serif, system-ui"
    SANS = "ui-sans-serif, sans-serif, system-ui"
    SERIF = "ui-serif, serif, system-ui"
    MONOSPACE = "ui-monospace, monospace, system-ui"


class PageLayout(Enum):
    TOP = "top"
    SIDE = "side"


# Set deprecated `ReportWidth` for backwards compatibility
ReportWidth = AppWidth


@dc.dataclass
class AppFormatting:
    """Sets the app styling and formatting"""

    bg_color: str = "#FFF"
    accent_color: str = "#4E46E5"
    font: t.Union[FontChoice, str] = FontChoice.DEFAULT
    text_alignment: TextAlignment = TextAlignment.JUSTIFY
    width: ReportWidth = ReportWidth.MEDIUM
    light_prose: bool = False

    def to_css(self) -> str:
        if isinstance(self.font, FontChoice):
            font = self.font.value
        else:
            font = self.font

        return f""":root {{
    --dp-accent-color: {self.accent_color};
    --dp-bg-color: {self.bg_color};
    --dp-text-align: {self.text_alignment.value};
    --dp-font-family: {font};
}}"""


@dc.dataclass
class ReportFormatting(AppFormatting):
    pass


# Used to detect a single display message once per VM invocation
# SKIP_DISPLAY_MSG = False

# Type aliases
BlockDict = t.Dict[str, BlockOrPrimitive]


class App(DPObjectRef):
    """
    App documents collate plots, text, tables, and files into an interactive document that
    can be analyzed and shared by users in their Browser
    """

    _tmp_report: t.Optional[Path] = None  # Temp local report
    _preview_file = DPTmpFile(f"{uuid4().hex}.html")
    list_fields: t.List[str] = ["name", "web_url", "project"]

    endpoint: str = "/reports/"
    pages: t.List[Page]
    page_layout: t.Optional[PageLayout]
    # id_count: int = 1

    def __init__(
        self,
        *arg_blocks: PageOrPrimitive,
        blocks: t.List[PageOrPrimitive] = None,
        layout: t.Optional[PageLayout] = None,
        **kwargs,
    ):
        """
        Args:
            *arg_blocks: Group to add to document
            blocks: Allows providing the document blocks as a single list

        Returns:
            A `App` document object that can be uploaded, saved, etc.

        ..tip:: Blocks can be passed using either arg parameters or the `blocks` kwarg, e.g.
          `dp.App(plot, table)` or `dp.App(blocks=[plot, table])`

        ..tip:: Create a list first to hold your blocks to edit them dynamically, for instance when using Jupyter, and use the `blocks` parameter
        """
        super().__init__(**kwargs)
        self.page_layout = layout
        self._preprocess_pages(blocks or list(arg_blocks))

    def upload(
        self,
        name: str,
        description: str = "",
        source_url: str = "",
        publicly_visible: t.Optional[bool] = None,
        tags: t.Optional[t.List[str]] = None,
        project: t.Optional[str] = None,
        open: bool = False,
        formatting: t.Optional[AppFormatting] = None,
        overwrite: bool = False,
        **kwargs,
    ) -> None:
        from .processors import upload

        upload(
            self, name, description, source_url, publicly_visible, tags, project, open, formatting, overwrite, **kwargs
        )

    def save(
        self,
        path: str,
        open: bool = False,
        standalone: bool = False,
        name: t.Optional[str] = None,
        author: t.Optional[str] = None,
        formatting: t.Optional[AppFormatting] = None,
        cdn_base: str = CDN_BASE,
    ) -> None:
        from .processors import save_report

        save_report(self, path, open, standalone, name, author, formatting, cdn_base)

    @staticmethod
    def from_notebook(
        opt_out: bool = True, show_code: bool = False, show_markdown: bool = True, template: str = "auto"
    ) -> App:
        from datapane.client.ipython_template import _registry, guess_template

        from ..ipython_utils import cells_to_blocks

        blocks = cells_to_blocks(opt_out=opt_out, show_code=show_code, show_markdown=show_markdown)
        app_template_cls = _registry.get(template) or guess_template(blocks)
        app_template = app_template_cls(blocks)
        app_template.transform()
        app_template.validate()
        blocks = app_template.blocks

        app = App(blocks=blocks)

        return app

    def stringify(
        self,
        standalone: bool = False,
        name: t.Optional[str] = None,
        author: t.Optional[str] = None,
        formatting: t.Optional[AppFormatting] = None,
        cdn_base: str = CDN_BASE,
        template_name: str = "template.html",
    ) -> str:
        from .processors import stringify_report

        view_html_string = stringify_report(self, standalone, name, author, formatting, cdn_base, template_name)

        return view_html_string

    def _preprocess_pages(self, pages: t.List[BlockOrPrimitive]):
        # pre-process report blocks
        if all(isinstance(b, Page) for b in pages):
            # we have all pages - all good!
            self.pages = t.cast(t.List[Page], pages)
        elif any(isinstance(b, Page) for b in pages):
            # mixed pages& blocks - not good!
            raise DPError("Mixed pages and non-page blocks, please wrap using dp.Page")
        else:
            # all blocks - wrap as a single page, including layout/mixed/raw elements
            self.pages = [Page(blocks=pages)]


class Report(App):
    """
    Deprecated (renamed to App)
    """

    def __init__(
        self,
        *arg_blocks: PageOrPrimitive,
        blocks: t.List[PageOrPrimitive] = None,
        layout: t.Optional[PageLayout] = None,
        **kwargs,
    ):
        super().__init__(*arg_blocks, blocks=blocks, layout=layout, **kwargs)
