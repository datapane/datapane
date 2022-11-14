from __future__ import annotations

import json
import os
import typing as t
import webbrowser
from abc import ABC
from base64 import b64encode
from os import path as osp
from pathlib import Path
from uuid import uuid4

import importlib_resources as ir
from bottle import SimpleTemplate
from lxml import etree

from datapane.client import config as c
from datapane.client import display_msg
from datapane.client.analytics import _NO_ANALYTICS, capture
from datapane.client.utils import InvalidReportError
from datapane.cloud_api import AppFormatting, AppWidth
from datapane.common import HTML, NPath, timestamp, validate_report_doc
from datapane.common.viewxml_utils import local_report_def
from datapane.view import CollectInteractive, XMLBuilder

from .types import BaseProcessor

if t.TYPE_CHECKING:
    pass

local_post_xslt = etree.parse(str(local_report_def / "local_post_process.xslt"))
local_post_transform = etree.XSLT(local_post_xslt)


def get_cdn() -> str:
    from datapane import __version__

    cdn_base: str = os.getenv("DATAPANE_CDN_BASE", f"https://datapane-cdn.com/v{__version__}")
    return cdn_base


class OptimiseAST(BaseProcessor):
    def __call__(self, _) -> None:
        """TODO - optimisations to improve the layout of the view"""
        # TODO - run ApplyDiynamic
        # AST checks
        if len(self.s.view.blocks) == 0:
            raise InvalidReportError("Empty view - must contain at least one block")

        return None


class AppTransformations(BaseProcessor):
    def __call__(self, _) -> None:
        ci = CollectInteractive()
        self.s.view.accept(ci)
        # s1 = dc.replace(s, entries=ci.entries)
        self.s.entries = ci.entries
        return None


class PreUploadProcessor(BaseProcessor):
    def __call__(self, _) -> t.Any:
        """TODO - pre-upload pass of the AST, can handle inlining file attributes from AssetStore"""
        return None


class ConvertXML(BaseProcessor):
    """Convert the AST into XML"""

    def __call__(self, _) -> str:
        """Convert the View AST into an XML fragment"""

        # create initial state
        builder_state = XMLBuilder(store=self.s.store)
        self.s.view.accept(builder_state)
        view_doc = builder_state.elements[0]

        # post_process and validate
        processed_view_doc = local_post_transform(view_doc)
        validate_report_doc(xml_doc=processed_view_doc)

        # convert to string
        view_xml_str: str = etree.tounicode(view_doc)

        # s1 = dc.replace(s, view_xml=view_xml_str)
        self.s.view_xml = view_xml_str

        return view_xml_str


###############################################################################
# HTML Exporting Processors
class BaseExportHTML(BaseProcessor, ABC):
    """Provides shared logic for writing an app to local disk"""

    # Type is `ir.abc.Traversable` which extends `Path`,
    # but the former isn't compatible with `shutil`
    internal_resources: Path = t.cast(Path, ir.files("datapane.resources.local_report"))
    # load the logo once into a class attrib
    __logo_img = (internal_resources / "datapane-logo-dark.png").read_bytes()
    logo: str = f"data:image/png;base64,{b64encode(__logo_img).decode('ascii')}"

    template: SimpleTemplate
    template_name: str

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # TODO (JB) - why doesn't altering TEMPLATE_PATH work as described in docs? Need to pass dir to `lookup` kwarg instead
        _template_dir = (cls.internal_resources / "bottle_templates").resolve()
        cls.template = SimpleTemplate(name=cls.template_name, lookup=[str(_template_dir)])

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

        cdn_base: str = get_cdn()
        html = self.template.render(
            report_doc=view_xml,
            assets=assets,
            report_width_class=report_width_classes.get(formatting.width),
            report_name=name,
            report_date=timestamp(),
            css_header=formatting.to_css(),
            is_light_prose=json.dumps(formatting.light_prose),
            dp_logo=self.logo,
            report_id=report_id,
            author_id=c.config.session_id,
            events=json.dumps(not _NO_ANALYTICS),
            cdn_base=f"{cdn_base}/report",
            app_runner=json.dumps(app_runner),
        )

        return html, report_id


class ExportBaseHTMLOnly(BaseExportHTML):
    """Export the base view used to render an App, containing no ViewXML nor Assets"""

    # TODO (JB) - Create base HTML-only template
    template_name = "local_template.html"

    def __init__(self, formatting: t.Optional[AppFormatting] = None):
        self.formatting = formatting

    def generate_chrome(self) -> HTML:
        # TODO - this is a bit hacky
        self.s = None
        html, report_id = self._write_html_template("app", formatting=self.formatting, app_runner=True)
        return HTML(html)

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

        if open:
            path_uri = f"file://{osp.realpath(osp.expanduser(self.path))}"
            webbrowser.open_new_tab(path_uri)

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
