"""
Datapane Processors

Describes an API for serializing a Report object, rendering it locally and publishing to a remote server
"""

import os
import threading
import typing as t
from abc import ABC
from base64 import b64encode
from functools import reduce
from http.server import HTTPServer, SimpleHTTPRequestHandler
from os import path as osp
from pathlib import Path
from shutil import copy, copytree, rmtree
from time import sleep
from uuid import uuid4

import importlib_resources as ir
from jinja2 import Environment, FileSystemLoader, Template
from lxml import etree
from lxml.etree import Element, _Element
from markupsafe import Markup  # used by Jinja

from datapane.client import config as c
from datapane.client.analytics import _NO_ANALYTICS, capture, capture_event
from datapane.client.api.common import Resource
from datapane.client.api.runtime import _report
from datapane.client.exceptions import DPError, InvalidReportError
from datapane.client.utils import display_msg, open_in_browser
from datapane.common import NPath, SDict, dict_drop_empty, log, timestamp
from datapane.common.report import local_report_def, validate_report_doc
from datapane.common.utils import compress_file

from .blocks import BuilderState, E
from .core import CDN_BASE, App, AppFormatting, AppWidth

try:
    from jinja2 import pass_context
except ImportError:
    # jinja2 =~ 2.11
    # Google Colab has 2.11.3 installed by default
    # Leave this in to avoid catastrpohic failure before restarting the kernel.
    from jinja2 import contextfunction as pass_context  # type: ignore


__all__ = ["upload", "save_report", "stringify_report", "serve", "build"]


# TODO - Refactor to share dp_tags.widths
report_width_classes = {
    AppWidth.FULL: "max-w-full",
    AppWidth.NARROW: "max-w-3xl",
    AppWidth.MEDIUM: "max-w-screen-xl",
}


local_post_xslt = etree.parse(str(local_report_def / "local_post_process.xslt"))
local_post_transform = etree.XSLT(local_post_xslt)

VUE_ESM_FILE = "vue.esm-browser.prod.js"
SERVED_REPORT_BUNDLE_DIR = "static"
SERVED_REPORT_ASSETS_DIR = "data"


class CompressedAssetsHTTPHandler(SimpleHTTPRequestHandler):
    """
    Python HTTP server for served local apps,
    with correct encoding header set on compressed assets
    """

    def end_headers(self):
        if self.path.startswith(f"/{SERVED_REPORT_ASSETS_DIR}") and not self.path.endswith(VUE_ESM_FILE):
            self.send_header("Content-Encoding", "gzip")
        super().end_headers()


@pass_context
def include_raw(ctx, name) -> Markup:  # noqa: ANN001
    """Normal jinja2 {% include %} doesn't escape {{...}} which appear in React's source code"""
    env = ctx.environment
    # Escape </script> to prevent 3rd party JS terminating the local app bundle.
    # Note there's an extra "\" because it needs to be escaped at both the python and JS level
    src = env.loader.get_source(env, name)[0].replace("</script>", r"<\\/script>")
    return Markup(src)


class Processor:
    """
    Contains logic for generating an App document and converting to XML
    """

    app: App

    def __init__(self, app: App):
        self.app = app

    def _to_xml(
        self,
        embedded: bool,
        served: bool,
        title: str = "Title",
        description: str = "Description",
        author: str = "Anonymous",
    ) -> t.Tuple[Element, t.List[Path]]:
        """Build XML report document"""
        # convert Pages to XML
        s = BuilderState(embedded, served)
        _s = reduce(lambda _s, p: p._to_xml(_s), self.app.pages, s)

        # create the pages
        pages: _Element = E.Pages(*_s.elements)
        if self.app.page_layout:
            pages.set("layout", self.app.page_layout.value)

        # add to main structure
        report_doc: Element = E.Report(
            E.Internal(),
            pages,
            version="1",
        )

        # add optional Meta
        if embedded or served:
            meta = E.Meta(
                E.Author(author or ""),
                E.CreatedOn(timestamp()),
                E.Title(title),
                E.Description(description),
            )
            report_doc.insert(0, meta)
        return report_doc, _s.attachments

    def _gen_report(
        self,
        embedded: bool,
        served: bool,
        title: str = "Title",
        description: str = "Description",
        author: str = "Anonymous",
        validate: bool = True,
    ) -> t.Tuple[str, t.List[Path]]:
        """Generate a report for saving/uploading"""
        report_doc, attachments = self._to_xml(embedded, served, title, description, author)

        if embedded and served:
            raise DPError("App can't be both embedded and served")

        # post_process and validate
        processed_report_doc = local_post_transform(
            report_doc, embedded="true()" if embedded else "false()", served="true()" if served else "false()"
        )
        if validate:
            validate_report_doc(xml_doc=processed_report_doc)
            self._report_status_checks(processed_report_doc, embedded)

        # convert to string
        report_str = etree.tounicode(processed_report_doc)
        log.debug("Successfully Built App")
        # log.debug(report_str)
        return report_str, attachments

    def _report_status_checks(self, processed_report_doc: etree._ElementTree, embedded: bool):
        # check for any unsupported local features, e.g. DataTable
        # NOTE - we could eventually have different validators for local and uploaded reports
        if embedded:
            return None

        # App checks
        # TODO - validate at least a single element
        asset_blocks = processed_report_doc.xpath("count(/Report/Pages/Page/*)")
        if asset_blocks == 0:
            raise InvalidReportError("Empty app - must contain at least one asset/block")


class LocalProcessor(Processor, ABC):
    """
    Provides shared logic for saved and served local app writing
    """

    template: t.Optional[Template] = None
    # Type is `ir.abc.Traversable` which extends `Path`,
    # but the former isn't compatible with `shutil`
    assets: Path = t.cast(Path, ir.files("datapane.resources.local_report"))
    logo: str
    template_name: str
    report_id: str = uuid4().hex
    served: bool

    def _setup_template(self):
        self.assert_bundle_exists()

        # load the logo
        logo_img = (self.assets / "datapane-logo-dark.png").read_bytes()
        self.logo = f"data:image/png;base64,{b64encode(logo_img).decode('ascii')}"

        template_loader = FileSystemLoader(self.assets)
        template_env = Environment(loader=template_loader)
        template_env.globals["include_raw"] = include_raw
        self.template = template_env.get_template(self.template_name)

    def write(
        self,
        report_doc: str,
        path: str,
        name: str,
        cdn_base: str = CDN_BASE,
        standalone: bool = False,
        author: t.Optional[str] = None,
        formatting: AppFormatting = None,
    ) -> str:
        report_id, r = self.render(
            report_doc,
            name,
            cdn_base,
            standalone,
            author,
            formatting,
        )

        Path(path).write_text(r, encoding="utf-8")

        return report_id

    def render(
        self,
        report_doc: str,
        name: str,
        cdn_base: str = CDN_BASE,
        standalone: bool = False,
        author: t.Optional[str] = None,
        formatting: AppFormatting = None,
    ) -> t.Tuple[str, str]:
        if formatting is None:
            formatting = AppFormatting()

        # create template on demand
        if not self.template:
            self._setup_template()

        report_id: str = uuid4().hex
        r = self.template.render(
            report_doc=report_doc,
            report_width_class=report_width_classes.get(formatting.width),
            report_name=name,
            report_author=author,
            report_date=timestamp(),
            css_header=formatting.to_css(),
            is_light_prose=formatting.light_prose,
            dp_logo=self.logo,
            report_id=report_id,
            author_id=c.config.session_id,
            events=not _NO_ANALYTICS,
            standalone=standalone,
            cdn_base=cdn_base,
        )

        return report_id, r

    def assert_bundle_exists(self):
        resource_to_check = "report" if self.served else "local-report-base.css"
        if not (self.assets / resource_to_check).exists():
            report_method = "save" if self.served else "serve"
            raise DPError(
                f"Can't find local FE bundle - App.{report_method} not available, please install release version"
            )


class Uploader(Processor):
    """
    Uploads a given App to the server that the user is logged into (e.g. datapane.com)
    """

    def go(
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
        display_msg("Uploading app and associated data - *please wait...*")

        self._upload_report(
            name,
            description,
            source_url,
            publicly_visible=publicly_visible,
            tags=tags,
            project=project,
            formatting=formatting,
            overwrite=overwrite,
            **kwargs,
        )

        if open:
            open_in_browser(self.app.web_url)

        capture("CLI App Upload", report_id=self.app.id)

        display_msg(
            "App successfully uploaded. View and share your app at {web_url:l}.",
            web_url=self.app.web_url,
        )

    # TODO - inline into upload - wait on new report API
    def _upload_report(
        self,
        name: str,
        description: str = "",
        source_url: str = "",
        publicly_visible: t.Optional[bool] = None,
        tags: t.Optional[t.List[str]] = None,
        project: t.Optional[str] = None,
        formatting: t.Optional[AppFormatting] = None,
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
        report_str, attachments = self._gen_report(embedded=False, served=False, title=name, description=description)
        files = dict(attachments=attachments)

        res = Resource(self.app.endpoint).post_files(files, overwrite=overwrite, document=report_str, **kwargs)

        # Set dto based on new URL
        self.app.url = res.url
        self.app.refresh()

        # add report to internal API handler for use by_datapane
        _report.append(self.app)


class Saver(LocalProcessor):
    """
    Saves a given App as a single HTML file
    """

    served = False
    template_name = "template.html"

    def go(
        self,
        path: str,
        open: bool = False,
        standalone: bool = False,
        name: t.Optional[str] = None,
        author: t.Optional[str] = None,
        formatting: t.Optional[AppFormatting] = None,
        cdn_base: str = CDN_BASE,
    ) -> None:
        report_id = self._save(path, cdn_base, open, standalone, name, author, formatting)
        capture("CLI Report Save", report_id=report_id)

    @capture_event("CLI Report Preview")
    def preview(
        self,
        open: bool,
        standalone: bool = False,
        formatting: t.Optional[AppFormatting] = None,
    ) -> None:
        """Preview the app in a new browser window.
        Can be called multiple times, refreshing the existing created preview file.
        Pass open=False to stop openning a new tab on subsequent previews

        Args:
            open: Open in your browser after creating (default: True)
            standalone: Inline the app source in the HTML app file rather than loading via CDN (default: False)
            formatting: Sets the basic app styling
        """
        self._save(self.app._preview_file.name, open=open, standalone=standalone, formatting=formatting)

    def _save(
        self,
        path: str,
        cdn_base: str = CDN_BASE,
        open: bool = False,
        standalone: bool = False,
        name: t.Optional[str] = None,
        author: t.Optional[str] = None,
        formatting: t.Optional[AppFormatting] = None,
    ) -> str:

        if not name:
            name = Path(path).stem[:127]

        local_doc, _ = self._gen_report(embedded=True, served=False, title=name)
        report_id = self.write(
            local_doc,
            path,
            name=name,
            cdn_base=cdn_base,
            standalone=standalone,
            formatting=formatting,
        )

        display_msg(f"App saved to ./{path}")

        if open:
            path_uri = f"file://{osp.realpath(osp.expanduser(path))}"
            open_in_browser(path_uri)

        return report_id


class Server(LocalProcessor):
    """
    Builds a given App for use in a server environment, or serves the App directly in a local server
    """

    served = True
    template_name = "served_template.html"

    def go(
        self,
        name: str = "app",
        dest: t.Optional[NPath] = None,
        port: int = 8000,
        host: str = "localhost",
        formatting: t.Optional[AppFormatting] = None,
        open: bool = True,
        overwrite: bool = False,
    ) -> None:
        path = self.build(name=name, dest=dest, formatting=formatting, compress_assets=True, overwrite=overwrite)

        os.chdir(path)  # Run the server in the specified path
        server = HTTPServer((host, port), CompressedAssetsHTTPHandler)
        display_msg(f"Server started at {host}:{port}")

        if open:
            # If the endpoint is simply opened then there is a race
            # between the page loading and server becoming available.
            threading.Thread(target=self._open_server, args=(host, port), daemon=True).start()

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass

        server.server_close()

    def build(
        self,
        name: str = "app",
        dest: t.Optional[NPath] = None,
        formatting: t.Optional[AppFormatting] = None,
        compress_assets: bool = False,
        overwrite: bool = False,
    ) -> Path:
        path: Path = Path(dest or os.getcwd()) / name
        app_exists = path.is_dir()

        if app_exists and overwrite:
            rmtree(path)
        elif app_exists and not overwrite:
            raise DPError(f"App exists at given path {str(path)} -- set `overwrite=True` to allow overwrite")

        bundle_path = path / SERVED_REPORT_BUNDLE_DIR
        assets_path = path / SERVED_REPORT_ASSETS_DIR

        bundle_path.mkdir(parents=True)
        assets_path.mkdir(parents=True)

        self.assert_bundle_exists()

        # Copy across symlinked app bundle.
        # Ignore `call-arg` as CI errors on `dirs_exist_ok`
        copytree(self.assets / "report", bundle_path / "app", dirs_exist_ok=True)  # type: ignore[call-arg]
        copy(self.assets / "local-report-base.css", bundle_path / "app" / "local-report-base.css")

        # Copy across symlinked Vue module
        copy(self.assets / VUE_ESM_FILE, bundle_path / VUE_ESM_FILE)

        local_doc, attachments = self._gen_report(embedded=False, served=True, title=name)

        # Copy across attachments
        for a in attachments:
            destination_path = assets_path / a.name
            if compress_assets:
                with compress_file(a) as a_gz:
                    copy(a_gz, destination_path)
            else:
                copy(a, destination_path)

        self.write(
            local_doc,
            str(path / "index.html"),
            name=name,
            formatting=formatting,
        )

        display_msg(f"Successfully built app in {path}")

        return path

    @staticmethod
    def _open_server(host: str, port: int) -> None:
        """Opens localserver endpoint, should be called in its own thread"""
        sleep(1)  # yield to main thread in order to allow start server process to run
        open_in_browser(f"http://{host}:{port}")


class Stringify(LocalProcessor):
    """
    Stringifies a given App as a single HTML string
    """

    served = False
    template_name = "template.html"

    def go(
        self,
        standalone: bool = False,
        name: t.Optional[str] = None,
        author: t.Optional[str] = None,
        formatting: t.Optional[AppFormatting] = None,
        cdn_base: str = CDN_BASE,
    ) -> str:
        report_id, view_html_string = self._stringify(cdn_base, standalone, name, author, formatting)

        if self.template_name == "ipython_template.html":
            capture("IPython Block Display", report_id=report_id)
        else:
            capture("App Stringified", report_id=report_id)

        return view_html_string

    def _stringify(
        self,
        cdn_base: str = CDN_BASE,
        standalone: bool = False,
        name: t.Optional[str] = None,
        author: t.Optional[str] = None,
        formatting: t.Optional[AppFormatting] = None,
    ) -> t.Tuple[str, str]:

        if not name:
            name = "Stringified App"

        local_doc, _ = self._gen_report(embedded=True, served=False, title=name)
        report_id, view_html_string = self.render(
            local_doc,
            name=name,
            cdn_base=cdn_base,
            standalone=standalone,
            formatting=formatting,
        )

        return report_id, view_html_string


def serve(
    app: App,
    name: str = "app",
    dest: t.Optional[NPath] = None,
    port: int = 8000,
    host: str = "localhost",
    formatting: t.Optional[AppFormatting] = None,
    open: bool = True,
    overwrite: bool = False,
):
    """Serve the app from a local http server
    Args:
        app: The `App` object
        name: The name of the app directory to be created
        dest: File path to store the app directory
        open: Open in your browser after creating (default: False)
        port: The port used to serve the app (default: 8000)
        host: The host used to serve the app (default: localhost)
        formatting: Sets the basic app styling; note that this is ignored if a app exists at the specified path
        overwrite: Replace existing app with the same name and destination if already exists (default: False)
    """
    Server(app).go(name=name, dest=dest, port=port, host=host, formatting=formatting, open=open, overwrite=overwrite)


def build(
    app: App,
    name: str = "app",
    dest: t.Optional[NPath] = None,
    formatting: t.Optional[AppFormatting] = None,
    compress_assets: bool = False,
    overwrite: bool = False,
) -> None:
    """Build an app with a directory structure, which can be served by a local http server
    Args:
        app: The `App` object
        name: The name of the app directory to be created
        dest: File path to store the app directory
        compress_assets: Compress user assets during app generation (default: True)
        formatting: Sets the basic app styling
        overwrite: Replace existing app with the same name and destination if already exists (default: False)
    """
    Server(app).build(name=name, dest=dest, formatting=formatting, compress_assets=compress_assets, overwrite=overwrite)


def save_report(
    app: App,
    path: str,
    open: bool = False,
    standalone: bool = False,
    name: t.Optional[str] = None,
    author: t.Optional[str] = None,
    formatting: t.Optional[AppFormatting] = None,
    cdn_base: str = CDN_BASE,
) -> None:
    """Save the app document to a local HTML file
    Args:
        app: The `App` object
        path: File path to store the document
        open: Open in your browser after creating (default: False)
        standalone: Inline the app source in the HTML app file rather than loading via CDN (default: False)
        name: Name of the document (optional: uses path if not provided)
        author: The app author / email / etc. (optional)
        formatting: Sets the basic app styling
        cdn_base: The base url to use for standalone apps (default: https://datapane-cdn.com/{version})
    """
    Saver(app).go(
        path=path, open=open, standalone=standalone, name=name, author=author, formatting=formatting, cdn_base=cdn_base
    )


def stringify_report(
    app: App,
    standalone: bool = False,
    name: t.Optional[str] = None,
    author: t.Optional[str] = None,
    formatting: t.Optional[AppFormatting] = None,
    cdn_base: str = CDN_BASE,
    template_name: str = "template.html",
) -> str:
    """Stringify the app document to a HTML string

    Args:
        standalone: Inline the app source in the HTML app file rather than loading via CDN (default: False)
        name: Name of the document (optional: uses path if not provided)
        author: The app author / email / etc. (optional)
        formatting: Sets the basic app styling
        cdn_base: The base url to use for standalone apps (default: https://datapane-cdn.com/{version})
        template_name: The name of the template to use for repor rendering (default: template.html)
    """
    stringify_processor = Stringify(app)
    stringify_processor.template_name = template_name

    view_html_string = stringify_processor.go(
        standalone=standalone, name=name, author=author, formatting=formatting, cdn_base=cdn_base
    )

    return view_html_string


def upload(
    app: App,
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
):
    """
    Upload the app document, including its attached assets, to the logged-in Datapane Server.
    Args:
        app: The `App` object
        name: The document name - can include spaces, caps, symbols, etc., e.g. "Profit & Loss 2020"
        description: A high-level description for the document, this is displayed in searches and thumbnails
        source_url: A URL pointing to the source code for the document, e.g. a GitHub repo or a Colab notebook
        publicly_visible: Visible to anyone with the link
        tags: A list of tags (as strings) used to categorise your document
        project: Project to add the app to
        open: Open the file in your browser after creating
        formatting: Set the basic styling for your app
        overwrite: Overwrite the app
    """
    Uploader(app).go(
        name=name,
        description=description,
        source_url=source_url,
        publicly_visible=publicly_visible,
        tags=tags,
        project=project,
        open=open,
        formatting=formatting,
        overwrite=overwrite,
        **kwargs,
    )
