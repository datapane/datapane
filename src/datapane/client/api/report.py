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
from .dp_object import BEObjectRef, UploadableObjectMixin
from .runtime import _report

E = ElementMaker()  # XML Tag Factory
local_post_xslt = etree.parse(str(local_report_def / "local_post_process.xslt"))
local_post_transform = etree.XSLT(local_post_xslt)
id_count = itertools.count(start=1)


@contextfunction
def include_raw(ctx, name):
    """ Normal jinja2 {% include %} doesn't escape {{...}} which appear in React's source code """
    env = ctx.environment
    return Markup(env.loader.get_source(env, name)[0])


def is_jupyter():
    """Checks if inside ipython shell inside browser"""
    return (
        hasattr(__builtins__, "get_ipython")
        and get_ipython().__class__.__name__ == "ZMQInteractiveShell"  # noqa: F821
    )


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

    def add_element(
        self, block: "ReportBlock", e: etree.Element, f: t.Optional[Path] = None
    ) -> "BuilderState":
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
    attributes: t.Dict[str, str]
    tag: str
    id: t.Optional[str] = None

    def __init__(self, id: str = None, **kwargs):
        self.id = str(id) if id else f"block-{next(id_count)}"
        self.attributes = {str(k): _conv_attrib(v) for (k, v) in kwargs.items()}

    @abstractmethod
    def to_xml(self, s: BuilderState) -> BuilderState:
        ...


BlockOrStr = t.Union[ReportBlock, str]


class BlockLayoutException(DPException):
    ...


class Blocks(ReportBlock):
    """
    Block objects at as a container that may hold a list of other Blocks object, such
    as Tables, Plots, and even recursive Blocks
    """

    tag = "Blocks"
    blocks: t.List[ReportBlock] = None

    def __init__(
        self,
        *arg_blocks: BlockOrStr,
        blocks: t.List[BlockOrStr] = None,
        id: str = None,
        rows: int = 0,
        columns: int = 1,
    ):
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

    def to_xml(self, s: BuilderState) -> BuilderState:
        # recurse into the elements and pull them out
        # NOTE - this works depth-first to create all sub-elements before the current, resulting in
        # simpler implementation, but out-of-order id's - to fix by creating Block first and passing down
        _s1: BuilderState = dc.replace(s, elements=[])
        _s2: BuilderState = reduce(lambda _s, x: x.to_xml(_s), self.blocks, _s1)
        _s3: BuilderState = dc.replace(_s2, elements=s.elements)
        _s3.add_element(self, E.Blocks(*_s2.elements, **self.attributes))
        return _s3


class Markdown(ReportBlock):
    """
    Markdown objects store Markdown text that can be displayed as formatted text when viewing your report
    """

    text: str
    tag = "Text"

    def __init__(self, text: str, id: str = None):
        super().__init__(id=id)
        self.text = text

    def to_xml(self, s: BuilderState) -> BuilderState:
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

    def to_xml(self, s: BuilderState) -> BuilderState:
        _E = getattr(E, self.tag)

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
    """File blocks store a file that can be displayed and downloaded"""

    tag = "File"

    def __init__(
        self,
        data: t.Optional[t.Any] = None,
        file: t.Optional[NPath] = None,
        is_json: bool = False,
        can_download: bool = True,
        name: t.Optional[str] = None,
        id: str = None,
    ):
        if file:
            file = Path(file)
        else:
            out_fn = self._save_obj(data, is_json=is_json)
            file = out_fn.file

        super().__init__(file=file, name=name or file.name, can_download=can_download, id=id)


class Plot(Asset):
    """
    Plot blocks store a Python-based plot, such as Altair, Boken, Matplotlib, or Plotly,
    that can be displayed in your report
    """

    tag = "Plot"

    def __init__(self, data: t.Any, caption: t.Optional[str] = None, id: str = None):
        out_fn = self._save_obj(data, is_json=False)
        super().__init__(file=out_fn.file, caption=caption, width=640, height=480, id=id)


class Table(Asset):
    """
    Table blocks store a dataframe that can be viewed and filtered in your report, and exported to CSV or Excel.
    Provides pivot-table functionality by default.
    """

    tag = "Table"

    def __init__(
        self,
        df: pd.DataFrame,
        caption: t.Optional[str] = None,
        can_pivot: bool = True,
        id: str = None,
    ):
        fn = self._save_df(df)
        (rows, columns) = df.shape
        super().__init__(
            file=fn.file, caption=caption, rows=rows, columns=columns, can_pivot=can_pivot, id=id
        )


################################################################################
# Report DPObject
class Report(BEObjectRef):
    """
    Reports collate plots, text, and tables into an interactive report that can be analysed by users
    in their Browser
    """

    endpoint: str = "/reports/"
    top_block: Blocks
    last_saved: t.Optional[str] = None  # Path to local report
    tmp_report: t.Optional[Path] = None  # Temp local report
    local_writer = ReportFileWriter()
    full_width: bool = False

    def __init__(
        self,
        *arg_blocks: BlockOrStr,
        blocks: t.List[BlockOrStr] = None,
        full_width: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.full_width = full_width
        # wrap blocks within a single Blocks root element during generation
        _blocks = blocks or list(arg_blocks)
        if all(isinstance(b, Blocks) for b in _blocks):
            self.top_block = Blocks(blocks=_blocks)
        else:
            # add additional top-level Blocks element to group mixed elements
            self.top_block = Blocks(blocks=[Blocks(blocks=_blocks)])

    def _gen_report(
        self, embedded: bool, title: str, description: str
    ) -> t.Tuple[str, t.List[Path]]:
        """Build XML report document"""
        # convert Blocks to XML
        s = BuilderState(embedded)
        _s = self.top_block.to_xml(s)
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
        processed_report_doc = local_post_transform(
            report_doc, embedded="true()" if embedded else "false()"
        )
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
        open: bool = False,
        tags: list = None,
        tweet: t.Union[bool, str] = False,
        source_url: str = "",
        **kwargs,
    ):
        """Deploy the report and its Assets to Datapane"""
        tags = tags or []
        print("Publishing report and associated data - please wait..")
        kwargs.update(name=name, description=description, tags=tags, source_url=source_url)

        report_str, attachments = self._gen_report(
            embedded=False, title=name, description=description
        )
        res = Resource(self.endpoint).post_files(
            dict(attachments=attachments), document=report_str, **kwargs
        )

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

    def save(
        self,
        path: str,
        open: bool = False,
        standalone: bool = False,
        **kwargs,
    ):
        """Save the report to a local HTML file"""
        self.last_saved = path

        local_doc, _ = self._gen_report(
            embedded=True, title="Local Report", description="Description"
        )

        self.local_writer.write(local_doc, path, self.full_width, standalone)

        if open:
            path_uri = f"file://{osp.realpath(osp.expanduser(path))}"
            webbrowser.open_new_tab(path_uri)

    def preview(self, width: int = 600, height: int = 500):
        """ Preview the report inside IPython notebooks in browser """
        if is_jupyter():
            from IPython.display import IFrame

            # Remove the previous temp report if it's been generated
            if self.tmp_report and self.tmp_report.exists():
                self.tmp_report.unlink()

            # We need to copy the report HTML to a local temp file,
            # as most browsers block iframes to absolute local paths.
            tmpfile = DPTmpFile(ext=".html")
            if self.last_saved:
                # Copy to tmp file if already saved
                shutil.copy(self.last_saved, tmpfile.name)
            else:
                # Else save directly to tmp file
                self.save(path=tmpfile.name)
            self.tmp_report = tmpfile.file

            # NOTE - iframe must be relative path
            iframe_src = self.tmp_report.relative_to(Path(".").absolute())
            return IFrame(src=str(iframe_src), width=width, height=height)
