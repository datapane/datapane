"""
Datapane Reports Object

Describes the `Report` object and included APIs for saving and publishing them.
"""

import shutil
import typing as t
import uuid
import warnings
import webbrowser
from base64 import b64encode
from enum import Enum, IntEnum
from functools import reduce
from os import path as osp
from pathlib import Path

import importlib_resources as ir
from glom import glom
from jinja2 import Environment, FileSystemLoader, Markup, Template, contextfunction
from lxml import etree
from lxml.etree import Element

from datapane.client import config as c
from datapane.client.api.common import DPTmpFile, Resource
from datapane.client.api.dp_object import DPObjectRef
from datapane.client.api.runtime import _report
from datapane.client.utils import DPError, UnsupportedFeatureError
from datapane.common import log, timestamp
from datapane.common.report import local_report_def, validate_report_doc

from .blocks import BlockOrPrimitive, BuilderState, E, Group, Page, PageOrPrimitive, Select

local_post_xslt = etree.parse(str(local_report_def / "local_post_process.xslt"))
local_post_transform = etree.XSLT(local_post_xslt)

# only these types will be documented by default
__all__ = ["Report", "Visibility", "ReportType"]

__pdoc__ = {
    "Report.endpoint": False,
}


class Visibility(IntEnum):
    """The report visibility type"""

    PRIVATE = 0  # private to owner
    PUBLIC = 2  # anon/unauthed access


class ReportType(Enum):
    """The report type"""

    DASHBOARD = "dashboard"
    REPORT = "report"
    ARTICLE = "article"


SKIP_DISPLAY_MSG = False


def is_jupyter() -> bool:
    """Checks if inside ipython shell inside browser"""
    try:
        return get_ipython().__class__.__name__ == "ZMQInteractiveShell"  # noqa: F821
    except Exception:
        return False


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
    src = env.loader.get_source(env, name)[0].replace("</script>", "<\\\/script>")
    return Markup(src)


class ReportFileWriter:
    """ Collects data needed to display a local report, and generates the local HTML """

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
        global SKIP_DISPLAY_MSG

        # only display once per session, else skip
        if SKIP_DISPLAY_MSG:
            return None
        else:
            SKIP_DISPLAY_MSG = True

        display_msg(
            text="Thanks for using Datapane, to automate and securely share reports in your organization please see Datapane Cloud - https://datapane.com/enterprise/",
            md="Thanks for using **Datapane**, to automate and securely share reports in your organization please see [Datapane Cloud](https://datapane.com/enterprise/)",
        )

    def write(self, report_doc: str, path: str, report_type: ReportType, name: str, author: t.Optional[str]):

        # create template on demand
        if not self.template:
            self._setup_template()

        self._display_msg()

        # template.html inlines the report doc with backticks so we need to escape any inside the doc
        report_doc_esc = report_doc.replace("`", r"\`")
        r = self.template.render(
            report_doc=report_doc_esc,
            report_type=report_type,
            report_name=name,
            report_author=author,
            report_date=timestamp(),
            dp_logo=self.logo,
        )
        Path(path).write_text(r, encoding="utf-8")


################################################################################
# Report DPObject
class Report(DPObjectRef):
    """
    Reports collate plots, text, tables, and files into an interactive report that
    can be analysed and shared by users in their Browser

    """

    endpoint: str = "/reports/"
    pages: t.List[Page]
    _last_saved: t.Optional[str] = None  # Path to local report
    _tmp_report: t.Optional[Path] = None  # Temp local report
    _local_writer = ReportFileWriter()
    report_type: ReportType = ReportType.REPORT
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
            *arg_blocks: Group to add to report
            blocks: Allows providing the report blocks as a single list
            type: Set the Report type, this will affect the formatting and layout of the report

        Returns:
            A `Report` object that can be published, saved, etc.

        .. tip:: Group can be passed using either arg parameters or the `blocks` kwarg, e.g.
          `dp.Report(plot, table)` or `dp.Report(blocks=[plot, table])`
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

    def _gen_report(self, embedded: bool, title: str, description: str = "Description") -> t.Tuple[str, t.List[Path]]:
        """Build XML report document"""
        # convert Pages to XML
        s = BuilderState(embedded)
        _s = reduce(lambda _s, p: p._to_xml(_s), self.pages, s)

        # add main structure and Meta
        report_doc: Element = E.Report(
            E.Meta(
                E.Author(c.config.username or "anonymous"),
                E.CreatedOn(timestamp()),
                E.Title(title),
                E.Description(description),
            ),
            E.Main(*_s.elements, type=self.report_type.value),
            version="1",
        )
        report_doc.set("{http://www.w3.org/XML/1998/namespace}id", f"_{uuid.uuid4().hex}")

        # post_process and validate
        processed_report_doc = local_post_transform(report_doc, embedded="true()" if embedded else "false()")
        validate_report_doc(xml_doc=processed_report_doc)

        # check for any unsupported local features, e.g. DataTable
        # NOTE - we could eventually have different validators for local and published reports
        if embedded:
            uses_datatable: bool = processed_report_doc.xpath("boolean(/Report/Main//DataTable)")
            if uses_datatable:
                raise UnsupportedFeatureError(
                    "DataTable component contains advanced analysis features that are not supported when saving or previewing locally,"
                    + " please either publish your report to a Datapane Server or use the dp.Table component instead"
                )

        # convert to string
        report_str = etree.tounicode(processed_report_doc, pretty_print=True)
        log.debug("Successfully Built Report")
        # log.debug(report_str)
        return (report_str, _s.attachments)

    def publish(
        self,
        name: str,
        description: str = "",
        source_url: str = "",
        visibility: t.Optional[Visibility] = None,
        open: bool = False,
        tags: t.List[str] = None,
        group: t.Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Publish the report, including its attached assets, to the logged-in Datapane Server.

        Args:
            name: The report name - can include spaces, caps, symbols, etc., e.g. "Profit & Loss 2020"
            description: A high-level description for the report, this is displayed in searches and thumbnails
            source_url: A URL pointing to the source code for the report, e.g. a GitHub repo or a Colab notebook
            visibility: one of `"PUBLIC"` _(default on Datapane.com)_, or `"PRIVATE"` _(limited on Datapame.com, unlimited on Datapane Enterprise)_
            open: Open the file in your browser after creating
            tags: A list of tags (as strings) used to categorise your report
        """

        display_msg("Publishing report and associated data - please wait..")

        # process params
        tags = tags or []
        # TODO - remove deprecation
        if isinstance(visibility, str):
            visibility_str = visibility
            warnings.warn("Passing visibility as a string is deprecated, use dp.Visibility enum instead.")
        else:
            visibility_str = glom(visibility, "name", default=None)
        kwargs.update(
            name=name, description=description, tags=tags, source_url=source_url, visibility=visibility_str, group=group
        )

        report_str, attachments = self._gen_report(embedded=False, title=name, description=description)
        res = Resource(self.endpoint).post_files(dict(attachments=attachments), document=report_str, **kwargs)

        # Set dto based on new URL
        self.url = res.url
        self.refresh()

        # add report to internal API handler for use by_datapane
        _report.append(self)
        if open:
            webbrowser.open_new_tab(self.web_url)

        display_msg(text=f"Report successfully published at {self.web_url}")

    def save(self, path: str, open: bool = False, name: t.Optional[str] = None, author: t.Optional[str] = None) -> None:
        """Save the report to a local HTML file

        Args:
            path: File path to store the report
            open: Open the file in your browser after creating (default: False)
            name: Name of the report (optional: uses path if not provided)
            author: The report author / email / etc.
        """
        self._last_saved = path

        if not name:
            name = Path(path).stem

        local_doc, _ = self._gen_report(embedded=True, title=name)
        self._local_writer.write(local_doc, path, self.report_type, name=name, author=author or c.config.username)

        if open:
            path_uri = f"file://{osp.realpath(osp.expanduser(path))}"
            webbrowser.open_new_tab(path_uri)

    def preview(self, width: int = 960, height: int = 700):
        """
        Preview the report inside your currently running Jupyter notebook

        Args:
            width: Width of the report preview in Jupyter (default: 960)
            height: Height of the report preview in Jupyter (default: 700)
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
