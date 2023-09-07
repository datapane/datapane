from __future__ import annotations

import json
import logging
import os
import typing as t
from abc import ABC
from copy import copy
from itertools import count
from os import path as osp
from pathlib import Path
from uuid import uuid4

import importlib_resources as ir
from lxml import etree

from datapane import blocks as b
from datapane._vendor.bottle import SimpleTemplate
from datapane.client.exceptions import InvalidReportError
from datapane.client.utils import display_msg, log, open_in_browser
from datapane.common import HTML, NPath, timestamp, validate_view_doc
from datapane.common.viewxml_utils import ElementT, local_view_resources
from datapane.view import PreProcess, XMLBuilder

from .file_store import FileEntry
from .types import BaseProcessor, Formatting

if t.TYPE_CHECKING:
    pass


class PreProcessView(BaseProcessor):
    """Optimisations to improve the layout of the view using the Block-API"""

    def __init__(self, *, is_finalised: bool = True) -> None:
        self.is_finalised = is_finalised
        super().__init__()

    def __call__(self, _: t.Any) -> None:
        # AST checks
        if len(self.s.blocks.blocks) == 0:
            raise InvalidReportError("Empty blocks object - must contain at least one block")

        # convert Page -> Select + Group
        v = copy(self.s.blocks)
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
        pp = PreProcess(is_finalised=self.is_finalised)
        v.accept(pp)
        v1 = pp.root
        # v1 = copy(v)

        # update the processor state
        self.s.blocks = v1

        return None


class ConvertXML(BaseProcessor):
    """Convert the View AST into an XML fragment"""

    local_post_xslt = etree.parse(str(local_view_resources / "local_post_process.xslt"))
    local_post_transform = etree.XSLT(local_post_xslt)

    def __init__(self, *, pretty_print: bool = False, fragment: bool = False) -> None:
        self.pretty_print: bool = pretty_print
        self.fragment: bool = fragment
        super().__init__()

    def __call__(self, _: t.Any) -> ElementT:
        initial_doc = self.convert_xml()
        transformed_doc = self.post_transforms(initial_doc)

        # convert to string
        view_xml_str: str = etree.tounicode(transformed_doc, pretty_print=self.pretty_print)
        # s1 = dc.replace(s, view_xml=view_xml_str)
        self.s.view_xml = view_xml_str

        if log.isEnabledFor(logging.DEBUG):
            log.debug(etree.tounicode(transformed_doc, pretty_print=True))

        # return the doc for further processing (xml str stored in state)
        return transformed_doc

    def convert_xml(self) -> ElementT:
        # create initial state
        builder_state = XMLBuilder(store=self.s.store)
        self.s.blocks.accept(builder_state)
        return builder_state.get_root(self.fragment)

    def post_transforms(self, view_doc: ElementT) -> ElementT:
        # TODO - post-xml transformations, essentially xslt / lxml-based DOM operations
        # post_process via xslt
        processed_view_doc: ElementT = self.local_post_transform(view_doc)

        # TODO - custom lxml-based transforms go here...

        # validate post all transformations
        validate_view_doc(xml_doc=processed_view_doc)
        return processed_view_doc


class PreUploadProcessor(BaseProcessor):
    def __call__(self, doc: ElementT) -> t.Tuple[str, t.List[t.BinaryIO]]:
        """
        pre-upload pass of the XML doc so can be uploaded to DPCloud
        modifies the document based on the FileStore
        """

        # NOTE - this currently relies on all assets existing linearly in document order
        # in the asset store - if we move to a cas we will need to update the algorithm here
        # replace ref -> attachment in view
        # all blocks with a ref
        refs: t.List[ElementT] = doc.xpath("/View//*[@src][starts-with(@src, 'ref://')]")
        for (idx, ref, f_entry) in zip(count(0), refs, self.s.store.files):
            ref: ElementT
            f_entry: FileEntry
            _hash: str = ref.get("src").split("://")[1]
            ref.set("src", f"attachment://{idx}")
            assert _hash == f_entry.hash  # sanity check

        self.s.view_xml = etree.tounicode(doc)
        return (self.s.view_xml, self.s.store.file_list)


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

    def escape_json_htmlsafe(self, obj: t.Any) -> str:
        """Escape JSON object for embedding in bottle templates."""

        # Taken from Jinja2's |tojson pipe function
        # (https://github.com/pallets/jinja/blob/b7cb6ee6675b12a027c5e7518f832b2926dfe293/src/jinja2/utils.py#L628)
        # Use of markupsafe is removed, as we use bottle's SimpleTemplate.
        return (
            json.dumps(obj)
            .replace("<", "\\u003c")
            .replace(">", "\\u003e")
            .replace("&", "\\u0026")
            .replace("'", "\\u0027")
        )

    def _write_html_template(
        self,
        name: str,
        formatting: t.Optional[Formatting] = None,
        app_runner: bool = False,
    ) -> t.Tuple[str, str]:
        """Internal method to write the ViewXML and assets into a HTML container and associated files"""
        name = name or "app"
        formatting = formatting or Formatting()

        report_id: str = uuid4().hex

        # TODO - split this out?
        vs = self.s
        if vs:
            assets = vs.store.as_dict() or {}
            view_xml = vs.view_xml
        else:
            assets = {}
            view_xml = ""

        app_data = dict(view_xml=view_xml, assets=assets)
        html = self.template.render(
            # Escape JS multi-line strings
            app_data=self.escape_json_htmlsafe(app_data),
            report_width_class=formatting.width.to_css(),
            report_name=name,
            report_date=timestamp(),
            css_header=formatting.to_css(),
            is_light_prose=json.dumps(formatting.light_prose),
            events=False,
            report_id=report_id,
            cdn_static="https://datapane-cdn.com/static",
            cdn_base=self.get_cdn(),
            app_runner=app_runner,
        )

        return html, report_id


class ExportBaseHTMLOnly(BaseExportHTML):
    """Export the base view used to render an App, containing no ViewXML nor Assets"""

    # TODO (JB) - Create base HTML-only template
    template_name = "local_template.html"

    def __init__(self, debug: bool, formatting: t.Optional[Formatting] = None):
        self.debug = debug
        self.formatting = formatting

    def generate_chrome(self) -> HTML:
        # TODO - this is a bit hacky
        self.s = None
        html, report_id = self._write_html_template("app", formatting=self.formatting, app_runner=True)
        return HTML(html)

    def get_cdn(self) -> str:
        return "/web-static" if self.debug else super().get_cdn()

    def __call__(self, _: t.Any) -> None:
        return None


class ExportHTMLInlineAssets(BaseExportHTML):
    """
    Export a view into a single HTML file containing:
    - View XML - embedded
    - Assetes - embedded as b64 data-uris
    """

    template_name = "local_template.html"

    def __init__(self, path: str, open: bool = False, name: str = "app", formatting: t.Optional[Formatting] = None):
        self.path = path
        self.open = open
        self.name = name
        self.formatting = formatting

    def __call__(self, _: t.Any) -> str:
        html, report_id = self._write_html_template(name=self.name, formatting=self.formatting)

        Path(self.path).write_text(html, encoding="utf-8")

        display_msg(f"App saved to ./{self.path}")

        if self.open:
            path_uri = f"file://{osp.realpath(osp.expanduser(self.path))}"
            open_in_browser(path_uri)

        return report_id


class ExportHTMLFileAssets(BaseExportHTML):
    """
    Export a view into a single HTML file on disk, containing
    - View XML - embedded
    - Assets - referenced as remote resources
    """

    template_name = "local_template.html"

    def __init__(self, app_dir: Path, name: str = "app", formatting: t.Optional[Formatting] = None):
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
        formatting: t.Optional[Formatting] = None,
    ):
        self.name = name
        self.formatting = formatting

    def __call__(self, _: t.Any) -> HTML:
        html, report_id = self._write_html_template(name=self.name, formatting=self.formatting)

        return HTML(html)
