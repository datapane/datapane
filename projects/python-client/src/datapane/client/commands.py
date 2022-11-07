import dataclasses as dc
import typing as t
import uuid
from contextlib import contextmanager
from distutils.dir_util import copy_tree
from pathlib import Path
from typing import Dict, List

import click
import importlib_resources as ir
from jinja2 import Environment, FileSystemLoader
from requests import HTTPError
from tabulate import tabulate

from datapane import __rev__, __version__
from datapane.common import DPError, SDict, _setup_dp_logging, log
from datapane.common.dp_types import URL, add_help_text
from datapane.common.report import generate_name, validate_name

from . import analytics, api
from . import config as c
from .utils import failure_msg, success_msg

EXTRA_OUT: bool = False


# TODO
#  - add info subcommand
#  - convert to use typer (https://github.com/tiangolo/typer) or autoclick
def init(verbosity: int):
    """Init the cmd-line env"""
    c.init()
    _setup_dp_logging(verbosity=verbosity)


@dc.dataclass(frozen=True)
class DPContext:
    """
    Any shared context we want to pass across commands,
    easier to just use globals in general tho
    """

    pass


@contextmanager
def api_error_handler(err_msg: str):
    try:
        yield
    except HTTPError as e:
        if EXTRA_OUT:
            log.exception(e)
        else:
            log.error(e)
        failure_msg(err_msg, do_exit=True)


def gen_name() -> str:
    return f"new_{uuid.uuid4().hex}"


def print_table(xs: t.Iterable[SDict], obj_name: str, showindex: bool = True) -> None:
    success_msg(f"Available {obj_name}:")
    print(tabulate(xs, headers="keys", showindex=showindex))


class GlobalCommandHandler(click.Group):
    def __call__(self, *args, **kwargs):
        try:
            return self.main(*args, **kwargs)
        except Exception as e:
            analytics.capture("CLI Error", msg=str(e), type=str(type(e)))
            if EXTRA_OUT:
                log.exception(e)
            if isinstance(e, DPError):
                failure_msg(str(e))
            else:
                failure_msg(add_help_text(str(e)), do_exit=True)


def recursive_help(cmd, parent=None):  # noqa: ANN001
    ctx = click.core.Context(cmd, info_name=cmd.name, parent=parent)
    print(cmd.get_help(ctx))
    print()
    commands = getattr(cmd, "commands", {})
    for sub in commands.values():
        recursive_help(sub, ctx)


###############################################################################
# Main
@click.group(cls=GlobalCommandHandler)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase logging verbosity - can add multiple times",
)
@click.version_option(version=f"{__version__} ({__rev__})")
@click.pass_context
def cli(ctx: click.core.Context, verbose: int):
    """Datapane CLI Tool"""
    global EXTRA_OUT
    EXTRA_OUT = verbose > 0
    init(verbosity=verbose)
    ctx.obj = DPContext()


# @cli.command()
# def dumphelp():
#     recursive_help(cli)


###############################################################################
# Auth
@cli.command()
@click.option("--token", default=None, help="API Token to the Datapane server.")
@click.option("--server", default=c.DEFAULT_SERVER, help="Datapane API Server URL.")
@click.pass_obj
def login(obj: DPContext, token: str, server: str):
    """Login to a server with the given API token."""
    api.login(token, server)
    # click.launch(f"{server}/settings/")


@cli.command()
@click.pass_obj
def logout(obj: DPContext):
    """Logout from the server and reset the config file"""
    api.logout()


@cli.command()
def ping():
    """Check can connect to the server"""
    try:
        api.ping()
    except HTTPError as e:
        log.error(e)


@cli.command()
def hello_world():
    """Create and run an example report, and open in the browser"""
    api.hello_world()


@cli.command()
@click.argument("url", default=None)
@click.option("--execute/--no-execute", default=True)
def template(url: URL, execute: bool):
    """Retrieve and run a template report, and open in the browser

    URL is the location of the template repository. Relative locations can be used for first-party templates, e.g. `dp-template-classifier-dashboard`.
    """
    api.template(url, execute)


###############################################################################
# Files
@cli.group()
def file():
    """Commands to work with Files"""
    pass


@file.command()
@click.argument("name")
@click.argument("file", type=click.Path(exists=True))
@click.option("--project")
@click.option("--overwrite", is_flag=True)
def upload(file: str, name: str, project: str, overwrite: bool):
    """Upload a csv or Excel file as a Datapane File"""
    log.info(f"Uploading {file}")
    r = api.File.upload_file(file, name=name, project=project, overwrite=overwrite)
    success_msg(f"Uploaded {click.format_filename(file)} to {r.url}")


@file.command()
@click.argument("name")
@click.option("--project")
@click.argument("file", type=click.Path())
def download(name: str, project: str, file: str):
    """Download file referenced by NAME to FILE"""
    r = api.File.get(name, project=project)
    r.download_file(file)
    success_msg(f"Downloaded {r.url} to {click.format_filename(file)}")


@file.command()
@click.argument("name")
@click.option("--project")
def delete(name: str, project: str):
    """Delete a file"""
    api.File.get(name, project).delete()
    success_msg(f"Deleted File {name}")


@file.command("list")
def file_list():
    """List files"""
    print_table(api.File.list(), "Files")


###############################################################################
# Reports
@cli.group()
def report():
    """Commands to work with Reports"""
    pass


def write_templates(scaffold_name: str, context: SDict):
    """Write templates for the given local scaffold (TODO - support git repos)"""
    # NOTE - only supports single hierarchy project dirs
    env = Environment(loader=FileSystemLoader("."))

    def render_file(fname: Path, context: Dict):
        rendered_script = env.get_template(fname.name).render(context)
        fname.write_text(rendered_script)

    # copy the scaffolds into the service
    def copy_scaffold() -> List[Path]:
        dir_path = ir.files("datapane.resources.templates") / scaffold_name
        copy_tree(str(dir_path), ".")
        return [Path(x.name) for x in dir_path.iterdir()]

    # run the scripts
    files = copy_scaffold()
    for f in files:
        if f.exists() and f.is_file():
            render_file(f, context=context)


# NOTE - CLI Report creation disabled for now until we have a replacement for Asset
# @report.command()
# @click.argument("name")
# @click.argument("files", type=click.Path(), nargs=-1, required=True)
# def create(files: Tuple[str], name: str):
#     """Create a Report from the provided FILES"""
#     blocks = [api.Asset.upload_file(file=Path(f)) for f in files]
#     r = api.Report(*blocks)
#     r.upload(name=name)
#     success_msg(f"Created Report {r.web_url}")


@report.command(name="init")
@click.argument("name", default=lambda: generate_name("Script"))
@click.option("--format", type=click.Choice(["notebook", "script"]), default="notebook")
def report_init(name: str, format: str):
    """Initialise a new report"""

    if format == "notebook":
        template = "report_ipynb"
    else:
        template = "report_py"

    if len(list(Path(".").glob("dp_report.*"))):
        failure_msg("Found existing project, cancelling", do_exit=True)

    validate_name(name)
    _context = dict(name=name)

    write_templates(template, _context)
    success_msg("Created sample report `dp_report`, edit as needed and run")


@report.command()  # type: ignore[no-redef]
@click.argument("name")
@click.option("--project")
def delete(name: str, project: str):
    """Delete a report"""
    api.Report.get(name, project).delete()
    success_msg(f"Deleted Report {name}")


@report.command("list")
def report_list():
    """List Reports"""
    print_table(api.Report.list(), "Reports")


# NOTE - NYI - disabled
# @report.command()
# @click.argument("name")
# @click.option("--project")
# @click.option("--filename", default="output.html", type=click.Path())
# def render(name: str, project: str, filename: str):
#     """Render a report to a static file"""
#     api.Report.get(name, project=project).render()
