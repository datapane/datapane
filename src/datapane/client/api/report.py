"""
Datapane Reports API

This includes the APIs for the `Blocks` that make up a `Report` and APIs for saving and pblishing them.
"""

import dataclasses as dc
import itertools
import shutil
import typing as t
import uuid
import webbrowser
from abc import ABC, abstractmethod
from base64 import b64encode
from functools import reduce
from os import path as osp
from pathlib import Path

import importlib_resources as ir
import pandas as pd
from furl import furl
from jinja2 import Environment, FileSystemLoader, Markup, Template, contextfunction
from lxml import etree
from lxml.builder import ElementMaker
from lxml.etree import Element

from datapane.common import NPath, guess_type, log, timestamp
from datapane.common.report import local_report_def, validate_report_doc

from ..utils import DPException
from .common import DPTmpFile, Resource, do_download_file
from .dp_object import DPObjectRef, UploadableObjectMixin
from .runtime import _report

E = ElementMaker()  # XML Tag Factory
local_post_xslt = etree.parse(str(local_report_def / "local_post_process.xslt"))
local_post_transform = etree.XSLT(local_post_xslt)
id_count = itertools.count(start=1)


# only these types will be documented by default
__all__ = ["ReportBlock", "Blocks", "Markdown", "File", "Plot", "Table", "Report"]

__pdoc__ = {
    "ReportBlock.attributes": False,
    "File.caption": False,
    "Plot.file": False,
    "Table.file": False,
    "Report.endpoint": False,
}


@contextfunction
def include_raw(ctx, name):
    """ Normal jinja2 {% include %} doesn't escape {{...}} which appear in React's source code """
    env = ctx.environment
    return Markup(env.loader.get_source(env, name)[0])


def is_jupyter() -> bool:
    """Checks if inside ipython shell inside browser"""
    try:
        return get_ipython().__class__.__name__ == "ZMQInteractiveShell"  # noqa: F821
    except Exception:
        return False


class ReportFileWriter:
    """ Collects data needed to display a local report, and generates the local HTML """

    template: t.Optional[Template] = None
    assets: Path
    asset_url = "https://datapane.com/static"
    asset_js = "local-report-base.css"
    asset_css = "local-report-base.js"

    def _setup_template(self) -> Template:
        """ Jinja template setup for local rendering """
        # check we have the files, download if not
        self.assets = ir.files("datapane.resources.local_report")
        if not (self.assets / self.asset_js).exists():
            log.warning("Can't find report assets, downloading")
            do_download_file(f"{self.asset_url}/{self.asset_js}", self.assets / self.asset_js)
            do_download_file(f"{self.asset_url}/{self.asset_css}", self.assets / self.asset_css)

        template_loader = FileSystemLoader(self.assets)
        template_env = Environment(loader=template_loader)
        template_env.globals["include_raw"] = include_raw
        self.template = template_env.get_template("template.html")

    def write(self, report_doc: str, path: str, full_width: bool, standalone: bool):
        # create template on demand
        if not self.template:
            self._setup_template()

        # template.html inlines the report doc with backticks so we need to escape any inside the doc
        report_doc_esc = report_doc.replace("`", r"\`")
        r = self.template.render(
            report_doc=report_doc_esc,
            full_width=full_width,
            standalone=standalone,
            cdn_base="https://datapane.com",
        )
        Path(path).write_text(r, encoding="utf-8")


@dc.dataclass
class BuilderState:
    """Hold state whilst building the Report XML document"""

    embedded: bool
    attachment_count: int = 0
    # TODO - store as single element or a list?
    # element: t.Optional[etree.Element] = None  # Empty Blocks Element?
    elements: t.List[etree.Element] = dc.field(default_factory=list)
    attachments: t.List[Path] = dc.field(default_factory=list)

    def add_element(self, block: "ReportBlock", e: etree.Element, f: t.Optional[Path] = None) -> "BuilderState":
        e.set("id", block.id)

        self.elements.append(e)
        if f and not self.embedded:
            self.attachments.append(f)
            self.attachment_count += 1
            assert len(self.attachments) == self.attachment_count

        return self


################################################################################
# API Blocks
def _conv_attrib(v) -> str:
    """Convert a value to a str for use as an ElementBuilder attribute"""
    # TODO - use a proper serialisation framework here / lxml features
    v1 = str(v)
    return v1.lower() if isinstance(v, bool) else v1


class ReportBlock(ABC):
    """Base Block class - subclassed by all Block types

    ..note:: The class is not used directly.
    """

    attributes: t.Dict[str, str]
    _tag: str
    id: t.Optional[str] = None

    def __init__(self, id: str = None, **kwargs):
        """
        Args:
            id: A unique id to reference the block, used when querying blocks via XPath to aid embedding
        """
        self.id = str(id) if id else f"block-{next(id_count)}"
        self.attributes = {str(k): _conv_attrib(v) for (k, v) in kwargs.items()}

    @abstractmethod
    def _to_xml(self, s: BuilderState) -> BuilderState:
        ...


BlockOrStr = t.Union[ReportBlock, str]


class BlockLayoutException(DPException):
    ...


class Blocks(ReportBlock):
    """
    Block objects act as a container that hold a list of nested Blocks object, such
    as Tables, Plots, etc.. - they may even hold Blocks themselves recursively.

    Blocks are used to provide a grouping for blocks can have layout options applied to them
    """

    _tag = "Blocks"
    blocks: t.List[ReportBlock] = None

    def __init__(
        self,
        *arg_blocks: BlockOrStr,
        blocks: t.List[BlockOrStr] = None,
        id: str = None,
        rows: int = 0,
        columns: int = 1,
    ):
        """
        Args:
            *arg_blocks: Blocks to add to report
            blocks: Allows providing the report blocks as a single list
            id: A unique id for the blocks to aid querying (optional)
            rows: Display the contained blocks, e.g. Plots, using _n_ rows
            columns: Display the contained blocks, e.g. Plots, using _n_ columns

        .. tip:: Blocks can be passed using either arg parameters or the `blocks` kwarg, e.g.
          `dp.Blocks(plot, table, columns=2)` or `dp.Blocks(blocks=[plot, table], columns=2)`
        """
        # wrap str in Markdown block
        _blocks = blocks or list(arg_blocks)
        self.blocks = [(Markdown(b) if isinstance(b, str) else b) for b in _blocks]

        # set row/column handling
        if rows == 1 and columns == 1:
            raise BlockLayoutException("Can't set both rows and columns to 1")
        if rows == 0 and columns == 0:
            raise BlockLayoutException("Can't set both rows and columns to 0")
        if rows > 0 and columns > 0 and len(_blocks) > rows * columns:
            raise BlockLayoutException("Too many blocks for given rows & columns")
        if rows > 0 and columns == 1:
            # if user has set rows and not changed columns, convert columns to auto-flow mode
            columns = 0

        super().__init__(id=id, rows=rows, columns=columns)

    def _to_xml(self, s: BuilderState) -> BuilderState:
        # recurse into the elements and pull them out
        # NOTE - this works depth-first to create all sub-elements before the current, resulting in
        # simpler implementation, but out-of-order id's - to fix by creating Block first and passing down
        _s1: BuilderState = dc.replace(s, elements=[])
        _s2: BuilderState = reduce(lambda _s, x: x._to_xml(_s), self.blocks, _s1)
        _s3: BuilderState = dc.replace(_s2, elements=s.elements)
        _s3.add_element(self, E.Blocks(*_s2.elements, **self.attributes))
        return _s3


class Markdown(ReportBlock):
    """
    Markdown objects store Markdown text that can be displayed as formatted text when viewing your report.

    ..note:: This object is also available as `dp.Text`, and any strings provided directly to the Report/Blocks object are converted automatically to Markdown blocks

    ..tip:: You can insert a dataframe in a Markdown block as a table by using `df.to_markdown()`, or use dp.Table for larger data if you need sorting, filtering and more.
    """

    text: str
    _tag = "Text"

    def __init__(self, text: str, id: str = None):
        """
        Args:
            text: The markdown formatted text, use triple-quotes, (`\"\"\"# My Title\"\"\"`) to create multi-line markdown text
            id: A unique id for the block to aid querying (optional)
        """
        super().__init__(id=id)
        self.text = text

    def _to_xml(self, s: BuilderState) -> BuilderState:
        # NOTE - do we use etree.CDATA wrapper?
        return s.add_element(self, E.Text(etree.CDATA(self.text)))


class Asset(ReportBlock, UploadableObjectMixin):
    """
    Asset objects form basis of all File-related blocks (abstract class, not exported)
    """

    file: Path = None
    caption: t.Optional[str] = None

    def __init__(self, file: Path, caption: str = None, id: str = None, **kwargs):
        # storing objects for delayed upload
        super().__init__(id=id, **kwargs)
        self.file = Path(file)
        self.caption = caption or ""

    def _to_xml(self, s: BuilderState) -> BuilderState:
        _E = getattr(E, self._tag)

        content_type = guess_type(self.file)
        file_size = str(self.file.stat().st_size)

        if s.embedded:
            # load the file and embed into a data-uri
            # NOTE - currently we read entire file into memory first prior to b64 encoding,
            #  to consider using base64io-python to stream and encode in 1-pass
            content = b64encode(self.file.read_bytes()).decode()
            e = _E(
                type=content_type,
                size=file_size,
                **self.attributes,
                src=f"data:{content_type};base64,{content}",
            )
        else:
            e = _E(
                type=guess_type(self.file),
                size=file_size,
                **self.attributes,
                src=f"attachment://{s.attachment_count}",
            )

        if self.caption:
            e.append(E.Caption(self.caption))
        return s.add_element(self, e, self.file)


class File(Asset):
    """
    File blocks are used to attach a file to the report that can be displayed (if possible) and downloaded by report viewers

    Any types of files may be attached, for instance, images (png / jpg), PDFs, JSON data, Excel files, etc.
    """

    _tag = "File"

    def __init__(
        self,
        data: t.Optional[t.Any] = None,
        file: t.Optional[NPath] = None,
        is_json: bool = False,
        can_download: bool = True,
        name: t.Optional[str] = None,
        id: str = None,
    ):
        """
        Args:
            data: A python object to attach to the report (e.g. a dictionary)
            file: Path to a file to attach to the report (e.g. a JPEG image)
            is_json: If `True`, treat the `data` as JSON data already
            can_download: Allow users to download the file when viewing the report
            name: Name to be used when downloading the file
            id: A unique id for the block to aid querying (optional)


        ..note:: either `data` or `file` must be provided
        """
        if file:
            file = Path(file)
        else:
            out_fn = self._save_obj(data, as_json=is_json)
            file = out_fn.file

        super().__init__(file=file, name=name or file.name, can_download=can_download, id=id)


class Plot(Asset):
    """
    Plot blocks store a Python-based plot object, including ones created by Altair, Plotly, Matplotlib, Bokeh, and Folium,
    for interactive display in your report when viewed in the browser.
    """

    _tag = "Plot"

    def __init__(self, data: t.Any, caption: t.Optional[str] = None, id: str = None):
        """

        Args:
            data: The `plot` object to attach
            caption: A caption to display below the plot (optional)
            id: A unique id for the block to aid querying (optional)
        """
        out_fn = self._save_obj(data, as_json=False)
        super().__init__(file=out_fn.file, caption=caption, width=640, height=480, id=id)


class Table(Asset):
    """
    Table blocks store a dataframe that can be viewed, sorted, filtered by users viewing your report,
    and downloaded by them as a CSV or Excel file.

    ..tip:: For smaller dataframes where you don't require sorting and filtering, also consider embedding your dataframe in a Datapane Markdown block, e.g. `dp.Markdown(df.to_markdown())`
    """

    _tag = "Table"

    def __init__(
        self,
        df: pd.DataFrame,
        caption: t.Optional[str] = None,
        can_pivot: bool = True,
        id: str = None,
    ):
        """
        Args:
            df: The pandas dataframe to attach to the report
            caption: A caption to display below the plot (optional)
            can_pivot: Is the table pivotable (not yet supported)
            id: A unique id for the block to aid querying (optional)

            ..hint:: `can_pivot` is currently unsupported and can be ignored

        """
        fn = self._save_df(df)
        (rows, columns) = df.shape
        super().__init__(file=fn.file, caption=caption, rows=rows, columns=columns, can_pivot=can_pivot, id=id)


################################################################################
# Report DPObject
class Report(DPObjectRef):
    """
    Reports collate plots, text, tables, and files into an interactive report that
    can be analysed and shared by users in their Browser

    """

    endpoint: str = "/reports/"
    _top_block: Blocks  # Test
    _last_saved: t.Optional[str] = None  # Path to local report
    _tmp_report: t.Optional[Path] = None  # Temp local report
    _local_writer = ReportFileWriter()
    full_width: bool = False
    """When set, the report is full-width suitable for use in a dashboard"""

    def __init__(
        self,
        *arg_blocks: BlockOrStr,
        blocks: t.List[BlockOrStr] = None,
        full_width: bool = False,
        **kwargs,
    ):
        """
        Args:
            *arg_blocks: Blocks to add to report
            blocks: Allows providing the report blocks as a single list
            full_width: Set to `True` to increase the report width, for instance when creating a dashboard

        Returns:
            A `Report` object that can be published, saved, etc.

        .. tip:: Blocks can be passed using either arg parameters or the `blocks` kwarg, e.g.
          `dp.Report(plot, table)` or `dp.Report(blocks=[plot, table])`
        """
        super().__init__(**kwargs)
        self.full_width = full_width
        # wrap blocks within a single Blocks root element during generation
        _blocks = blocks or list(arg_blocks)
        if all(isinstance(b, Blocks) for b in _blocks):
            self._top_block = Blocks(blocks=_blocks)
        else:
            # add additional top-level Blocks element to group mixed elements
            self._top_block = Blocks(blocks=[Blocks(blocks=_blocks)])

    def _gen_report(self, embedded: bool, title: str, description: str) -> t.Tuple[str, t.List[Path]]:
        """Build XML report document"""
        # convert Blocks to XML
        s = BuilderState(embedded)
        _s = self._top_block._to_xml(s)
        assert len(_s.elements) == 1
        # unwrap blocks from top_block
        _top_blocks: t.List[Element] = _s.elements[0].getchildren()

        # add main structure and Meta
        report_doc: Element = E.Report(
            E.Meta(
                E.Author("Anonymous"),  # TODO - get username from config?
                E.CreatedOn(timestamp()),
                E.Title(title),
                E.Description(description),
            ),
            E.Main(*_top_blocks, full_width=_conv_attrib(self.full_width)),
            version="1",
        )
        report_doc.set("{http://www.w3.org/XML/1998/namespace}id", f"_{uuid.uuid4().hex}")

        # post_process and validate
        processed_report_doc = local_post_transform(report_doc, embedded="true()" if embedded else "false()")
        validate_report_doc(xml_doc=processed_report_doc)

        # convert to string
        report_str = etree.tounicode(processed_report_doc, pretty_print=True)
        log.debug("Built Report")
        log.info(report_str)
        return (report_str, _s.attachments)

    def publish(
        self,
        name: str,
        description: str = "",
        source_url: str = "",
        visibility: t.Optional[str] = None,
        open: bool = False,
        tags: t.List[str] = None,
        tweet: t.Union[bool, str] = False,
        **kwargs,
    ) -> None:
        """
        Publish the report, including its attached assets, to the logged-in Datapane Server.

        Args:
            name: The report name - can include spaces, caps, symbols, etc., e.g. "Profit & Loss 2020"
            description: A high-level description for the report, this is displayed in searches and thumbnails
            source_url: A URL pointing to the source code for the report, e.g. a GitHub repo or a Colab report
            visibility: one of `"PUBLIC"` _(default on Public)_, `"UNLISTED"`, `"ORG"` _(Teams only)_, or `"PRIVATE"` _(Teams only)_
            open: Open the file in your browser after creating
            tags: A list of tags (as strings) used to categorise your report
            tweet: Open twitter to tweet your published report - can customise the tweet by passing the message in as this parameter
        """

        tags = tags or []
        print("Publishing report and associated data - please wait..")
        kwargs.update(name=name, description=description, tags=tags, source_url=source_url, visibility=visibility)

        report_str, attachments = self._gen_report(embedded=False, title=name, description=description)
        res = Resource(self.endpoint).post_files(dict(attachments=attachments), document=report_str, **kwargs)

        # Set dto based on new URL
        self.url = res.url
        self.refresh()

        # add report to internal API handler for use by_datapane
        _report.append(self)
        if open:
            webbrowser.open_new_tab(self.web_url)
        if tweet:
            if isinstance(tweet, str):
                desc = tweet[:260]
            elif description:
                desc = description[:260]
            else:
                desc = f"Check out my new report - {name}"[:260]
            tweet_url = (
                furl(url="https://twitter.com/intent/tweet")
                .add({"text": desc, "url": self.web_url, "hashtags": "datapane,python"})
                .url
            )
            webbrowser.open_new_tab(tweet_url)

        print(f"Report successfully published at {self.web_url}")

    def save(self, path: str, open: bool = False, standalone: bool = False) -> None:
        """Save the report to a local HTML file

        Args:
            path: location to save the HTML file
            open: Open the file in your browser after creating
            standalone: Create a fully standalone HTML report with no external/network dependencies _(this can result in large files)_
        """
        self._last_saved = path

        local_doc, _ = self._gen_report(embedded=True, title="Local Report", description="Description")

        self._local_writer.write(local_doc, path, self.full_width, standalone)

        if open:
            path_uri = f"file://{osp.realpath(osp.expanduser(path))}"
            webbrowser.open_new_tab(path_uri)

    def preview(self, width: int = 600, height: int = 500) -> None:
        """
        Preview the report inside your currently running Jupyter notebook

        Args:
            width: Width of the report preview in Jupyter (default: 600)
            height: Height of the report preview in Jupyter (default: 500)
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
