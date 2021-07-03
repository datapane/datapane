"""
Datapane Reports Object

Describes the `Report` object and included APIs for saving and uploading them.
"""
import shutil
import typing as t
import warnings
import webbrowser
from base64 import b64encode
from enum import Enum, IntEnum
from functools import reduce
from os import path as osp
from pathlib import Path

import importlib_resources as ir
from jinja2 import Environment, FileSystemLoader, Markup, Template, contextfunction
from lxml import etree
from lxml.etree import Element

from datapane.client import config as c
from datapane.client.analytics import capture_event
from datapane.client.api.common import DPTmpFile, Resource
from datapane.client.api.dp_object import DPObjectRef
from datapane.client.api.runtime import _report
from datapane.client.utils import DPError, InvalidReportError, is_jupyter
from datapane.common import dict_drop_empty, log, timestamp
from datapane.common.report import local_report_def, validate_report_doc
from datapane.common.utils import DEFAULT_HTML_HEADER

from .blocks import (
    Block,
    BlockOrPrimitive,
    BuilderState,
    E,
    Group,
    Page,
    PageOrPrimitive,
    Select,
    wrap_block,
)

U = t.TypeVar("U", bound="TextReport")

local_post_xslt = etree.parse(str(local_report_def / "local_post_process.xslt"))
local_post_transform = etree.XSLT(local_post_xslt)

# only these types will be documented by default
__all__ = ["Report", "ReportType"]

__pdoc__ = {
    "Report.endpoint": False,
}


# TODO(protocol) TODO(obsolete)
class Visibility(IntEnum):
    """The report visibility type"""

    PRIVATE = 0  # private to owner
    # UNLISTED = 1  # public but not searchable
    PUBLIC = 2  # anon/unauthed access


class ReportType(Enum):
    """The document type"""

    DASHBOARD = "dashboard"
    REPORT = "report"
    ARTICLE = "article"


# Used to detect a single display message once per VM invocation
SKIP_DISPLAY_MSG = False


def display_msg(text: str, md: str = None):
    if is_jupyter():
        from IPython.display import Markdown, display

        msg = md or text
        display(Markdown(msg))
    else:
        print(text)


@contextfunction
def include_raw(ctx, name):
    """ Normal jinja2 {% include %} doesn't escape {{...}} which appear in React's source code """
    env = ctx.environment
    # Escape </script> to prevent 3rd party JS terminating the local report bundle.
    # Note there's an extra "\" because it needs to be escaped at both the python and JS level
    src = env.loader.get_source(env, name)[0].replace("</script>", r"<\\/script>")
    return Markup(src)


class ReportFileWriter:
    """ Collects data needed to display a local report document, and generates the local HTML """

    template: t.Optional[Template] = None
    assets: Path
    logo: str
    dev_mode: bool = False

    def _setup_template(self):
        """ Jinja template setup for local rendering """
        # check we have the FE files, abort if not
        self.assets = ir.files("datapane.resources.local_report")
        if not (self.assets / "local-report-base.css").exists():
            raise DPError("Can't find local FE bundle - report.save not available, please install release version")

        # load the logo
        logo_img = (self.assets / "datapane-logo-dark.png").read_bytes()
        self.logo = f"data:image/png;base64,{b64encode(logo_img).decode()}"

        template_loader = FileSystemLoader(self.assets)
        template_env = Environment(loader=template_loader)
        template_env.globals["include_raw"] = include_raw
        self.template = template_env.get_template("template.html")

    def _display_msg(self):
        # TODO(obsolete)
        global SKIP_DISPLAY_MSG

        # only display once per session, else skip
        if SKIP_DISPLAY_MSG or c.config.is_org:
            return None
        else:
            SKIP_DISPLAY_MSG = True

        display_msg(
            text="Thanks for using Datapane, to automate and securely share documents in your organization please see Datapane Teams - https://datapane.com/",
            md="Thanks for using **Datapane**, to automate and securely share documents in your organization please see [Datapane Teams](https://datapane.com/)",
        )

    def write(self, report_doc: str, path: str, report_type: ReportType, name: str, author: t.Optional[str]):
        # create template on demand
        if not self.template:
            self._setup_template()

        url = "https://datapane.com/create-workspace/"
        display_msg(
            text=f"Report saved to {path}. To host and share securely, create a free private workspace at {url}",
            md=f"Report saved to {path}. To host and share securely, [create a free private workspace]({url})",
        )

        # TODO(obsolete)
        # self._display_msg()

        # template.html inlines the report doc with backticks so we need to escape any inside the doc
        report_doc_esc = report_doc.replace("`", r"\`")
        r = self.template.render(
            report_doc=report_doc_esc,
            report_type=report_type,
            report_name=name,
            report_author=author,
            report_date=timestamp(),
            html_header=DEFAULT_HTML_HEADER,
            dp_logo=self.logo,
        )
        Path(path).write_text(r, encoding="utf-8")


class BaseReport(DPObjectRef):
    endpoint: str = "/reports/"
    pages: t.List[Page]
    report_type: ReportType = ReportType.REPORT
    # id_count: int = 1

    def _to_xml(
        self, embedded: bool, title: str = "Title", description: str = "Description", author: str = "Anonymous"
    ) -> t.Tuple[Element, t.List[Path]]:
        """Build XML report document"""
        # convert Pages to XML
        s = BuilderState(embedded)
        _s = reduce(lambda _s, p: p._to_xml(_s), self.pages, s)

        # add main structure
        report_doc: Element = E.Report(
            E.Internal(),
            E.Main(*_s.elements),
            version="1",
        )

        # add optional Meta
        if embedded:
            meta = E.Meta(
                E.Author(c.config.username or author),
                E.CreatedOn(timestamp()),
                E.Title(title),
                E.Description(description),
                E.Type(self.report_type.value),
            )
            report_doc.insert(0, meta)
        return (report_doc, _s.attachments)

    def _gen_report(
        self,
        embedded: bool,
        title: str = "Title",
        description: str = "Description",
        author: str = "Anonymous",
        check_empty: bool = True,
    ) -> t.Tuple[str, t.List[Path]]:
        """Generate a report for saving/uploading"""
        report_doc, attachments = self._to_xml(embedded, title, description, author)

        # post_process and validate
        processed_report_doc = local_post_transform(report_doc, embedded="true()" if embedded else "false()")
        validate_report_doc(xml_doc=processed_report_doc)
        self._report_status_checks(processed_report_doc, embedded, check_empty)

        # convert to string
        report_str = etree.tounicode(processed_report_doc)
        log.debug("Successfully Built Report")
        # log.debug(report_str)
        return (report_str, attachments)

    def _report_status_checks(self, processed_report_doc: etree._ElementTree, embedded: bool, check_empty: bool):
        # NOTE - common checks go here
        pass

    def _upload_report(
        self,
        name: str,
        description: str = "",
        source_url: str = "",
        tags: t.List[str] = None,
        group: t.Optional[str] = None,
        **kwargs,
    ) -> None:
        # TODO - clean up arg handling
        # process params
        tags = tags or []
        kwargs.update(
            name=name,
            description=description,
            tags=tags,
            source_url=source_url,
            group=group,
            type=self.report_type.value,  # set the type of report using type argument passed to the constructor
        )
        # current protocol is to strip all empty args and patch (via a post)
        # TODO(protocol) - alternate plan would be keeping local state in resource handle and posting all
        kwargs = dict_drop_empty(kwargs)

        # generate the report
        report_str, attachments = self._gen_report(embedded=False, title=name, description=description)
        # TODO(protocol) always include attachments parameter
        # if not attachments:
        #     kwargs["attachments"] = []
        res = Resource(self.endpoint).post_files(dict(attachments=attachments), api_document=report_str, **kwargs)

        # Set dto based on new URL
        self.url = res.url
        self.refresh()

        # add report to internal API handler for use by_datapane
        _report.append(self)


BlockDict = t.Dict[str, BlockOrPrimitive]
BlockList = t.List[BlockOrPrimitive]


class TextReport(BaseReport):
    """
    Upload plots, text, tables, and files as assets that can be used within a TextReport created in the browser
    """

    def __init__(
        self, *arg_blocks: BlockOrPrimitive, blocks: t.Union[BlockDict, BlockList] = None, **kw_blocks: BlockOrPrimitive
    ):
        """
        Blocks can be created with the `name` parameter, if not set, one can be provided here using keyword args.
        Use the blocks dict parameter to add a dynamically generated set of named blocks, useful when working in Jupyter

        Args:
            *arg_blocks: List of blocks to add to document - if a name is not present it will be auto-generated
            blocks: Allows providing the document blocks as a single dictionary of named blocks
            **kw_blocks: Keyword argument set of blocks, whose block name will be that given in the keyword

        Returns:
            A `TextReport` object containing assets that can be uploaded for use with your online TextReport

        .. tip:: Blocks can be passed using either arg parameters or the `blocks` kwarg as a dictionary, e.g.
          `dp.TextReport(my_plot=plot, my_table=table)` or `dp.TextReport(blocks={"my_plot": plot, "my_table":table})`

        .. tip:: Create a dictionary first to hold your blocks to edit them dynmically, for instance when using Jupyter, and use the `blocks` parameter
        """
        super().__init__()

        # set the blocks
        def _conv_block(name: str, block: BlockOrPrimitive) -> Block:
            x = wrap_block(block)
            x._set_name(name)
            return x

        _blocks: BlockList
        if isinstance(blocks, dict):
            _blocks = [_conv_block(k, v) for (k, v) in blocks.items()]
        elif isinstance(blocks, list):
            _blocks = blocks
        else:
            # use arg and kw blocks
            _blocks = list(arg_blocks)
            _blocks.extend([_conv_block(k, v) for (k, v) in kw_blocks.items()])

        if not _blocks:
            log.debug("No blocks provided - creating empty report")

        # set the pages
        self.pages = [Page(blocks=[Group(blocks=_blocks, name="top-group")])]

    @property
    def edit_url(self):
        return f"{self.web_url}edit/"

    def upload(
        self,
        id: t.Optional[str] = "",
        name: t.Optional[str] = "",
        description: str = "",
        source_url: str = "",
        tags: t.List[str] = None,
        group: t.Optional[str] = None,
        open: bool = False,
        **kwargs,
    ) -> "TextReport":
        """
        Create a TextReport document on the logged-in Datapane Server.

        Args:
            id: The document id - use when pushing assets to an existing report
            name: The document name - can include spaces, caps, symbols, etc., e.g. "Profit & Loss 2020"
            description: A high-level description for the document, this is displayed in searches and thumbnails
            source_url: A URL pointing to the source code for the document, e.g. a GitHub repo or a Colab notebook
            tags: A list of tags (as strings) used to categorise your document
            group: Group to add the report to (Teams only)
            open: Open the file in your browser after creating

        Returns:
            A `TextReport` document object that can be used to upload assets
        """

        assert id or name, "id or name must be set"
        if id:
            # TODO - this seems incorrect - do we want this indirection
            # TODO - cache the name? - would this work if name changed?
            x: "TextReport" = TextReport.by_id(id)
            if not x.is_text_report:
                raise DPError("Expected a TextReport object, found a Report object")
            name = x.name

        self._upload_report(name, description, source_url, tags, group, is_text_report=True, **kwargs)
        display_msg(
            text=f"TextReport assets successfully uploaded - you can edit and format at {self.edit_url}, and view the final report at {self.web_url}",
            md=f"TextReport assets successfully uploaded - you can edit and format [here]({self.edit_url}), and view the final report [here]({self.web_url})",
        )

        if open:
            webbrowser.open_new_tab(self.edit_url)
        return self

    def _report_status_checks(self, processed_report_doc: etree._ElementTree, embedded: bool, check_empty: bool):
        super()._report_status_checks(processed_report_doc, embedded, check_empty)

        if embedded:
            return None

        asset_blocks = processed_report_doc.xpath("count(/Report/Main//*)")
        if asset_blocks < 3 and check_empty:
            raise InvalidReportError(
                "Empty TextReport, require at least one asset, please see the docs for syntax help"
            )


# Python/API Report
class Report(BaseReport):
    """
    Report documents collate plots, text, tables, and files into an interactive document that
    can be analysed and shared by users in their Browser
    """

    _last_saved: t.Optional[str] = None  # Path to local report
    _tmp_report: t.Optional[Path] = None  # Temp local report
    _local_writer = ReportFileWriter()
    list_fields: t.List[str] = ["name", "web_url", "group"]
    """When set, the report is full-width suitable for use in a dashboard"""

    def __init__(
        self,
        *arg_blocks: PageOrPrimitive,
        blocks: t.List[PageOrPrimitive] = None,
        type: ReportType = ReportType.REPORT,
        **kwargs,
    ):
        """
        Args:
            *arg_blocks: Group to add to document
            blocks: Allows providing the document blocks as a single list
            type: Set the Report type, this will affect the formatting and layout of the document

        Returns:
            A `Report` document object that can be uploaded, saved, etc.

        .. tip:: Blocks can be passed using either arg parameters or the `blocks` kwarg, e.g.
          `dp.Report(plot, table)` or `dp.Report(blocks=[plot, table])`

        .. tip:: Create a list first to hold your blocks to edit them dynmically, for instance when using Jupyter, and use the `blocks` parameter
        """
        super().__init__(**kwargs)
        self.report_type = type
        self._preprocess_pages(blocks or list(arg_blocks))

    def _preprocess_pages(self, pages: t.List[BlockOrPrimitive]):
        # pre-process report blocks
        if all(isinstance(b, Page) for b in pages):
            # we have all pages
            self.pages = t.cast(t.List[Page], pages)
        elif all(isinstance(b, (Group, Select)) for b in pages):
            # all blocks - wrap as a single page
            self.pages = [Page(blocks=pages)]
        else:
            # add additional top-level Group element to group mixed elements
            self.pages = [Page(blocks=[Group(blocks=pages)])]

    def upload(
        self,
        name: str,
        description: str = "",
        source_url: str = "",
        tags: t.List[str] = None,
        group: t.Optional[str] = None,
        open: bool = False,
        **kwargs,
    ) -> None:
        """
        Upload the report document, including its attached assets, to the logged-in Datapane Server.

        Args:
            name: The document name - can include spaces, caps, symbols, etc., e.g. "Profit & Loss 2020"
            description: A high-level description for the document, this is displayed in searches and thumbnails
            source_url: A URL pointing to the source code for the document, e.g. a GitHub repo or a Colab notebook
            tags: A list of tags (as strings) used to categorise your document
            group: Group to add the report to (Teams only)
            open: Open the file in your browser after creating
        """

        if "visibility" in kwargs:
            kwargs.pop("visibility")
            if c.config.is_public:
                warnings.warn(
                    "Visibility parameter deprecated, your reports are drafts by default and can be published via the report share feature in your browser"
                )
            else:
                warnings.warn(
                    "Visibility parameter deprecated, your reports are private by default and can be shared via the report share feature in your browser"
                )

        display_msg("Publishing document and associated data - *please wait...*")

        self._upload_report(name, description, source_url, tags, group, **kwargs)

        if open:
            webbrowser.open_new_tab(self.web_url)

        display_msg(
            text=f"Report successfully uploaded at {self.web_url}, follow the link to view your report and optionally share it with the Datapane Community",
            md=f"Report successfully uploaded, click [here]({self.web_url}) to view your report and optionally share it with the Datapane Community",
        )

    def publish(self, *a, **kw) -> None:
        warnings.warn("Deprecated - please use report.upload instead")
        self.upload(*a, **kw)

    @capture_event("CLI Report Save")
    def save(self, path: str, open: bool = False, name: t.Optional[str] = None, author: t.Optional[str] = None) -> None:
        """Save the report document to a local HTML file

        Args:
            path: File path to store the document
            open: Open in your browser after creating (default: False)
            name: Name of the document (optional: uses path if not provided)
            author: The report author / email / etc. (optional)
        """
        self._last_saved = path

        if not name:
            name = Path(path).stem[:127]

        local_doc, _ = self._gen_report(embedded=True, title=name)
        self._local_writer.write(local_doc, path, self.report_type, name=name, author=author or c.config.username)

        if open:
            path_uri = f"file://{osp.realpath(osp.expanduser(path))}"
            webbrowser.open_new_tab(path_uri)

    @capture_event("CLI Report Preview")
    def preview(self, width: int = 960, height: int = 700):
        """
        Preview the document inside your currently running Jupyter notebook

        Args:
            width: Width of the preview in Jupyter (default: 960)
            height: Height of the preview in Jupyter (default: 700)
        """
        if is_jupyter():
            from IPython.display import IFrame

            # Remove the previous temp report if it's been generated
            if self._tmp_report and self._tmp_report.exists():
                self._tmp_report.unlink()

            # We need to copy the report HTML to a local temp file,
            # as most browsers block iframes to absolute local paths.
            tmpfile = DPTmpFile(ext=".html")
            if self._last_saved:
                # Copy to tmp file if already saved
                shutil.copy(self._last_saved, tmpfile.name)
            else:
                # Else save directly to tmp file
                self.save(path=tmpfile.name)
            self._tmp_report = tmpfile.file

            # NOTE - iframe must be relative path
            iframe_src = self._tmp_report.relative_to(Path(".").absolute())
            return IFrame(src=str(iframe_src), width=width, height=height)
        else:
            log.warning("Can't preview - are you running in Jupyter?")

    def _report_status_checks(self, processed_report_doc: etree._ElementTree, embedded: bool, check_empty: bool):
        super()._report_status_checks(processed_report_doc, embedded, check_empty)

        # check for any unsupported local features, e.g. DataTable
        # NOTE - we could eventually have different validators for local and uploaded reports
        if embedded:
            pass
        else:
            # TODO - validate at least a single element
            asset_blocks = processed_report_doc.xpath("count(/Report/Main//*)")
            if asset_blocks < 3 and check_empty:
                raise InvalidReportError("Empty report - must contain at least one asset/block")
            elif asset_blocks < 4:
                url = "https://docs.datapane.com/reports/blocks/layout-pages-and-selects"
                display_msg(
                    text=f"Your report only contains a single element - did you know you can include additional plots, tables and text in a report? Check out {url} for more info",
                    md=f"Your report only contains a single element - did you know you can include additional plots, tables and text in a report? Check out [the docs]({url}) for more info",
                )

            has_text: bool = processed_report_doc.xpath("boolean(/Report/Main/Page//Text)")
            if not has_text:
                display_msg(
                    "Your report doesn't contain any text - consider using TextReport to upload assets and add text to your report from your browser"
                )
