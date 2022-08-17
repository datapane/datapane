"""
Datapane Reports Object

Describes the `Report` object and included APIs for saving and uploading them.
"""
import dataclasses as dc
import typing as t
import webbrowser
from base64 import b64encode
from enum import Enum
from functools import reduce
from os import path as osp
from pathlib import Path
from uuid import uuid4

import importlib_resources as ir
from jinja2 import Environment, FileSystemLoader, Template, contextfunction
from lxml import etree
from lxml.etree import Element, _Element
from markupsafe import Markup  # used by Jinja

from datapane.client import config as c
from datapane.client.analytics import _NO_ANALYTICS, capture, capture_event
from datapane.client.api.common import DPTmpFile, Resource
from datapane.client.api.dp_object import DPObjectRef
from datapane.client.api.runtime import _report
from datapane.client.utils import DPError, InvalidReportError, display_msg
from datapane.common import SDict, dict_drop_empty, log, timestamp
from datapane.common.report import local_report_def, validate_report_doc

from .blocks import BlockOrPrimitive, BuilderState, E, Page, PageOrPrimitive

local_post_xslt = etree.parse(str(local_report_def / "local_post_process.xslt"))
local_post_transform = etree.XSLT(local_post_xslt)

# only these types will be documented by default
__all__ = ["Report", "ReportWidth"]

__pdoc__ = {
    "Report.endpoint": False,
}


class ReportWidth(Enum):
    """The document width"""

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


@dc.dataclass
class ReportFormatting:
    """Sets the report styling and formatting"""

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


# Used to detect a single display message once per VM invocation
# SKIP_DISPLAY_MSG = False


@contextfunction
def include_raw(ctx, name) -> Markup:  # noqa: ANN001
    """Normal jinja2 {% include %} doesn't escape {{...}} which appear in React's source code"""
    env = ctx.environment
    # Escape </script> to prevent 3rd party JS terminating the local report bundle.
    # Note there's an extra "\" because it needs to be escaped at both the python and JS level
    src = env.loader.get_source(env, name)[0].replace("</script>", r"<\\/script>")
    return Markup(src)


class ReportFileWriter:
    """Collects data needed to display a local report document, and generates the local HTML"""

    template: t.Optional[Template] = None
    assets: Path
    logo: str
    dev_mode: bool = False

    def _setup_template(self):
        """Jinja template setup for local rendering"""
        # check we have the FE files, abort if not
        self.assets = ir.files("datapane.resources.local_report")
        if not (self.assets / "local-report-base.css").exists():
            raise DPError("Can't find local FE bundle - report.save not available, please install release version")

        # load the logo
        logo_img = (self.assets / "datapane-logo-dark.png").read_bytes()
        self.logo = f"data:image/png;base64,{b64encode(logo_img).decode('ascii')}"

        template_loader = FileSystemLoader(self.assets)
        template_env = Environment(loader=template_loader)
        template_env.globals["include_raw"] = include_raw
        self.template = template_env.get_template("template.html")

    def write(
        self,
        report_doc: str,
        path: str,
        name: str,
        author: t.Optional[str] = None,
        formatting: ReportFormatting = None,
    ) -> str:

        if formatting is None:
            formatting = ReportFormatting()

        # create template on demand
        if not self.template:
            self._setup_template()

        report_id = uuid4().hex
        r = self.template.render(
            report_doc=report_doc,
            report_width=formatting.width.value,
            report_name=name,
            report_author=author,
            report_date=timestamp(),
            css_header=formatting.to_css(),
            is_light_prose=formatting.light_prose,
            dp_logo=self.logo,
            report_id=report_id,
            author_id=c.config.session_id,
            events=not _NO_ANALYTICS,
        )
        Path(path).write_text(r, encoding="utf-8")

        return report_id


# Type aliases
BlockDict = t.Dict[str, BlockOrPrimitive]


class Report(DPObjectRef):
    """
    Report documents collate plots, text, tables, and files into an interactive document that
    can be analysed and shared by users in their Browser
    """

    _tmp_report: t.Optional[Path] = None  # Temp local report
    _local_writer = ReportFileWriter()
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
            A `Report` document object that can be uploaded, saved, etc.

        ..tip:: Blocks can be passed using either arg parameters or the `blocks` kwarg, e.g.
          `dp.Report(plot, table)` or `dp.Report(blocks=[plot, table])`

        ..tip:: Create a list first to hold your blocks to edit them dynamically, for instance when using Jupyter, and use the `blocks` parameter
        """
        super().__init__(**kwargs)
        self.page_layout = layout
        self._preprocess_pages(blocks or list(arg_blocks))

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

    def _to_xml(
        self, embedded: bool, title: str = "Title", description: str = "Description", author: str = "Anonymous"
    ) -> t.Tuple[Element, t.List[Path]]:
        """Build XML report document"""
        # convert Pages to XML
        s = BuilderState(embedded)
        _s = reduce(lambda _s, p: p._to_xml(_s), self.pages, s)

        # create the pages
        pages: _Element = E.Pages(*_s.elements)
        if self.page_layout:
            pages.set("layout", self.page_layout.value)

        # add to main structure
        report_doc: Element = E.Report(
            E.Internal(),
            pages,
            version="1",
        )

        # add optional Meta
        if embedded:
            meta = E.Meta(
                E.Author(author or ""),
                E.CreatedOn(timestamp()),
                E.Title(title),
                E.Description(description),
            )
            report_doc.insert(0, meta)
        return (report_doc, _s.attachments)

    def _gen_report(
        self,
        embedded: bool,
        title: str = "Title",
        description: str = "Description",
        author: str = "Anonymous",
        validate: bool = True,
    ) -> t.Tuple[str, t.List[Path]]:
        """Generate a report for saving/uploading"""
        report_doc, attachments = self._to_xml(embedded, title, description, author)

        # post_process and validate
        processed_report_doc = local_post_transform(report_doc, embedded="true()" if embedded else "false()")
        if validate:
            validate_report_doc(xml_doc=processed_report_doc)
            self._report_status_checks(processed_report_doc, embedded)

        # convert to string
        report_str = etree.tounicode(processed_report_doc)
        log.debug("Successfully Built Report")
        # log.debug(report_str)
        return (report_str, attachments)

    def _report_status_checks(self, processed_report_doc: etree._ElementTree, embedded: bool):
        # check for any unsupported local features, e.g. DataTable
        # NOTE - we could eventually have different validators for local and uploaded reports
        if embedded:
            return None

        # Report checks
        # TODO - validate at least a single element
        asset_blocks = processed_report_doc.xpath("count(/Report/Pages/Page/*)")
        if asset_blocks == 0:
            raise InvalidReportError("Empty report - must contain at least one asset/block")

    @property
    def edit_url(self) -> str:
        return f"{self.web_url}edit/"

    ############################################################################
    # Uploaded Reports
    # TODO - inline into upload - wait on new report API
    def _upload_report(
        self,
        name: str,
        description: str = "",
        source_url: str = "",
        publicly_visible: bool = False,
        tags: t.List[str] = None,
        project: t.Optional[str] = None,
        formatting: t.Optional[ReportFormatting] = None,
        overwrite: bool = False,
        **kwargs,
    ) -> None:
        # TODO - clean up arg handling
        # process params
        tags = tags or []

        formatting_kwargs: SDict = {}
        if formatting:
            formatting_kwargs.update(
                width=formatting.width.value,
                style_header=(
                    f'<style type="text/css">\n{formatting.to_css()}\n</style>'
                    if c.config.is_org
                    else formatting.to_css()
                ),
                is_light_prose=formatting.light_prose,
            )

        kwargs.update(
            name=name,
            description=description,
            tags=tags,
            source_url=source_url,
            publicly_visible=publicly_visible,
            project=project,
            **formatting_kwargs,
        )
        # current protocol is to strip all empty args and patch (via a post)
        # TODO(protocol) - alternate plan would be keeping local state in resource handle and posting all
        kwargs = dict_drop_empty(kwargs)

        # generate the report
        report_str, attachments = self._gen_report(embedded=False, title=name, description=description)
        files = dict(attachments=attachments)

        res = Resource(self.endpoint).post_files(files, overwrite=overwrite, document=report_str, **kwargs)

        # Set dto based on new URL
        self.url = res.url
        self.refresh()

        # add report to internal API handler for use by_datapane
        _report.append(self)

    def upload(
        self,
        name: str,
        description: str = "",
        source_url: str = "",
        publicly_visible: bool = False,
        tags: t.List[str] = None,
        project: t.Optional[str] = None,
        open: bool = False,
        formatting: t.Optional[ReportFormatting] = None,
        overwrite: bool = False,
        **kwargs,
    ) -> None:
        """
        Upload the report document, including its attached assets, to the logged-in Datapane Server.

        Args:
            name: The document name - can include spaces, caps, symbols, etc., e.g. "Profit & Loss 2020"
            description: A high-level description for the document, this is displayed in searches and thumbnails
            source_url: A URL pointing to the source code for the document, e.g. a GitHub repo or a Colab notebook
            publicly_visible: Visible to anyone with the link
            tags: A list of tags (as strings) used to categorise your document
            project: Project to add the report to
            open: Open the file in your browser after creating
            formatting: Set the basic styling for your report
            overwrite: Overwrite the report
        """

        display_msg("Uploading report and associated data - *please wait...*")

        self._upload_report(
            name,
            description,
            source_url,
            publicly_visible,
            tags,
            project,
            formatting=formatting,
            overwrite=overwrite,
            **kwargs,
        )

        if open:
            webbrowser.open_new_tab(self.web_url)

        display_msg(
            "Report successfully uploaded. View and share your report at {web_url:l}.",
            web_url=self.web_url,
        )

    ############################################################################
    # Local saved reports
    def _save(
        self,
        path: str,
        open: bool = False,
        name: t.Optional[str] = None,
        author: t.Optional[str] = None,
        formatting: t.Optional[ReportFormatting] = None,
    ) -> str:

        if not name:
            name = Path(path).stem[:127]

        local_doc, _ = self._gen_report(embedded=True, title=name)
        report_id = self._local_writer.write(
            local_doc,
            path,
            name=name,
            formatting=formatting,
        )

        display_msg(f"Report saved to ./{path}")

        if open:
            path_uri = f"file://{osp.realpath(osp.expanduser(path))}"
            webbrowser.open_new_tab(path_uri)

        return report_id

    def save(
        self,
        path: str,
        open: bool = False,
        name: t.Optional[str] = None,
        author: t.Optional[str] = None,
        formatting: t.Optional[ReportFormatting] = None,
    ) -> None:
        """Save the report document to a local HTML file

        Args:
            path: File path to store the document
            open: Open in your browser after creating (default: False)
            name: Name of the document (optional: uses path if not provided)
            author: The report author / email / etc. (optional)
            formatting: Sets the basic report styling
        """

        report_id = self._save(path, open, name, author, formatting)
        capture("CLI Report Save", report_id=report_id)

    @capture_event("CLI Report Preview")
    def preview(
        self,
        open: bool,
        formatting: t.Optional[ReportFormatting] = None,
    ) -> None:
        """Preview the report in a new browser window.
        Can be called multiple times, refreshing the existing created preview file.
        Pass open=False to stop openning a new tab on subsequent previews

        Args:
            open: Open in your browser after creating (default: True)
            formatting: Sets the basic report styling
        """
        self._save(self._preview_file.name, open=open, formatting=formatting)
