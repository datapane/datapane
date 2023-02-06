from __future__ import annotations

import json
import logging
import os
import typing as t
from abc import ABC
from copy import copy
from os import path as osp
from pathlib import Path
from uuid import uuid4

import importlib_resources as ir
from bottle import SimpleTemplate
from lxml import etree
from lxml.etree import _Element as ElementT

from datapane import blocks as b
from datapane.client import config as c
from datapane.client.analytics import _NO_ANALYTICS, capture
from datapane.client.exceptions import InvalidReportError
from datapane.client.utils import display_msg, log, open_in_browser
from datapane.cloud_api import AppFormatting, AppWidth
from datapane.common import HTML, NPath, timestamp, validate_report_doc
from datapane.common.viewxml_utils import local_report_def
from datapane.view import CollectFunctions, PreProcess, XMLBuilder

from .types import BaseProcessor

if t.TYPE_CHECKING:
    pass


class PreProcessView(BaseProcessor):
    """Optimisations to improve the layout of the view using the Block-API"""

    def __call__(self, _) -> None:
        # AST checks
        if len(self.s.view.blocks) == 0:
            raise InvalidReportError("Empty view - must contain at least one block")

        # convert Page -> Select + Group
        v = copy(self.s.view)
        if all(isinstance(blk, b.Page) for blk in v.blocks):
            # convert to top-level Select
            p: b.Page  # noqa: F842
            v.blocks = [
                b.Select(
                    blocks=[b.Group(blocks=p.blocks, label=p.title, name=p.name) for p in v.blocks],
                    type=b.SelectType.TABS,
                )
            ]

        # Block-API visitors
        pp = PreProcess()
        v.accept(pp)
        v1 = pp.root
        # v1 = copy(v)

        # update the processor state
        self.s.view = v1

        return None


class AppTransformations(BaseProcessor):
    """Transform an app prior to running"""

    def __call__(self, _) -> None:
        ci = CollectFunctions()
        self.s.view.accept(ci)
        # s1 = dc.replace(s, entries=ci.entries)
        self.s.entries = ci.entries
        return None


class PreUploadProcessor(BaseProcessor):
    def __call__(self, _) -> t.Any:
        """TODO - pre-upload pass of the AST, can handle inlining file attributes from AssetStore"""
        return None


class ConvertXML(BaseProcessor):
    """Convert the View AST into an XML fragment"""

    local_post_xslt = etree.parse(str(local_report_def / "local_post_process.xslt"))
    local_post_transform = etree.XSLT(local_post_xslt)

    def __call__(self, _) -> str:
        initial_doc = self.convert_xml()
        transformed_doc = self.post_transforms(initial_doc)

        # convert to string
        view_xml_str: str = etree.tounicode(transformed_doc)
        # s1 = dc.replace(s, view_xml=view_xml_str)
        self.s.view_xml = view_xml_str

        if log.isEnabledFor(logging.DEBUG):
            log.debug(etree.tounicode(transformed_doc, pretty_print=True))

        return view_xml_str

    def convert_xml(self) -> ElementT:
        # create initial state
        builder_state = XMLBuilder(store=self.s.store)
        self.s.view.accept(builder_state)
        return builder_state.elements[0]

    def post_transforms(self, view_doc: ElementT) -> ElementT:
        # TODO - post-xml transformations, essentially xslt / lxml-based DOM operations
        #  e.g. s/View/Group/g
        # post_process via xslt
        processed_view_doc: ElementT = self.local_post_transform(view_doc)

        # TODO - custom lxml-based transforms go here...

        # validate post all transformations
        validate_report_doc(xml_doc=processed_view_doc)
        return processed_view_doc


###############################################################################
# HTML Exporting Processors
class BaseExportHTML(BaseProcessor, ABC):
    """Provides shared logic for writing an app to local disk"""

    # Type is `ir.abc.Traversable` which extends `Path`,
    # but the former isn't compatible with `shutil`
    template_dir: Path = t.cast(Path, ir.files("datapane.resources.html_templates"))
    template: SimpleTemplate
    template_name: str

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # TODO (JB) - why doesn't altering TEMPLATE_PATH work as described in docs? Need to pass dir to `lookup` kwarg instead
        cls.template = SimpleTemplate(name=cls.template_name, lookup=[str(cls.template_dir)])

    def get_cdn(self) -> str:
        from datapane import __is_dev_build__, __version__

        if cdn_base := os.getenv("DATAPANE_CDN_BASE"):
            return cdn_base
        elif __is_dev_build__:
            return "https://datapane-cdn.com/dev"
        else:
            return f"https://datapane-cdn.com/v{__version__}"

    def _write_html_template(
        self,
        name: str,
        formatting: t.Optional[AppFormatting] = None,
        app_runner: bool = False,
    ) -> t.Tuple[str, str]:
        """Internal method to write the ViewXML and assets into a HTML container and associated files"""
        name = name or "app"
        formatting = formatting or AppFormatting()

        report_id: str = uuid4().hex

        # TODO - split this out?
        vs = self.s
        if vs:
            assets = vs.store.as_dict() or {}
            view_xml = vs.view_xml
        else:
            assets = {}
            view_xml = ""

        html = self.template.render(
            report_doc=view_xml,
            assets=assets,
            report_width_class=report_width_classes.get(formatting.width),
            report_name=name,
            report_date=timestamp(),
            css_header=formatting.to_css(),
            is_light_prose=json.dumps(formatting.light_prose),
            report_id=report_id,
            author_id=c.config.session_id,
            events=json.dumps(not _NO_ANALYTICS),
            cdn_static="https://datapane-cdn.com/static",
            cdn_base=self.get_cdn(),
            app_runner=app_runner,
        )

        return html, report_id


class ExportBaseHTMLOnly(BaseExportHTML):
    """Export the base view used to render an App, containing no ViewXML nor Assets"""

    # TODO (JB) - Create base HTML-only template
    template_name = "local_template.html"

    def __init__(self, debug: bool, formatting: t.Optional[AppFormatting] = None):
        self.debug = debug
        self.formatting = formatting

    def generate_chrome(self) -> HTML:
        # TODO - this is a bit hacky
        self.s = None
        html, report_id = self._write_html_template("app", formatting=self.formatting, app_runner=True)
        return HTML(html)

    def get_cdn(self) -> str:
        return "/web-static" if self.debug else super().get_cdn()

    def __call__(self, _) -> None:
        return None


class ExportHTMLInlineAssets(BaseExportHTML):
    """
    Export a view into a single HTML file containing:
    - View XML - embedded
    - Assetes - embedded as b64 data-uris
    """

    template_name = "local_template.html"

    def __init__(self, path: str, open: bool = False, name: str = "app", formatting: t.Optional[AppFormatting] = None):
        self.path = path
        self.open = open
        self.name = name
        self.formatting = formatting

    def __call__(self, _) -> str:
        html, report_id = self._write_html_template(name=self.name, formatting=self.formatting)

        Path(self.path).write_text(html, encoding="utf-8")

        display_msg(f"App saved to ./{self.path}")

        if self.open:
            path_uri = f"file://{osp.realpath(osp.expanduser(self.path))}"
            open_in_browser(path_uri)

        capture("CLI Report Save", report_id=report_id)
        return report_id


class ExportHTMLFileAssets(BaseExportHTML):
    """
    Export a view into a single HTML file on disk, containing
    - View XML - embedded
    - Assets - referenced as remote resources
    """

    template_name = "local_template.html"

    def __init__(self, app_dir: Path, name: str = "app", formatting: t.Optional[AppFormatting] = None):
        self.app_dir = app_dir
        self.name = name
        self.formatting = formatting

    def __call__(self, dest: t.Optional[NPath] = None) -> Path:
        html, report_id = self._write_html_template(
            name=self.name,
            formatting=self.formatting,
        )

        index_path = self.app_dir / "index.html"
        index_path.write_text(html, encoding="utf-8")
        display_msg(f"Built app in {self.app_dir}")
        return self.app_dir


class ExportHTMLStringInlineAssets(BaseExportHTML):
    """
    Export the View as an in-memory string representing a resizable HTML fragment, containing
    - View XML - embedded
    - Assetes - embedded as b64 data-uris
    """

    template_name = "ipython_template.html"

    def __init__(
        self,
        name: str = "Stringified App",
        formatting: t.Optional[AppFormatting] = None,
    ):
        self.name = name
        self.formatting = formatting

    def __call__(self, _) -> HTML:
        html, report_id = self._write_html_template(name=self.name, formatting=self.formatting)

        return HTML(html)


# TODO - Refactor to share dp_tags.widths
report_width_classes = {
    AppWidth.NARROW: "max-w-3xl",
    AppWidth.MEDIUM: "max-w-screen-xl",
    AppWidth.FULL: "max-w-full",
}
