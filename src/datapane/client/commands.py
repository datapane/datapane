import dataclasses as dc
import os
import tarfile
import time
import typing as t
import uuid
from contextlib import contextmanager
from distutils.dir_util import copy_tree
from distutils.util import strtobool
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

import click
import click_spinner
import importlib_resources as ir
from jinja2 import Environment, FileSystemLoader
from requests import HTTPError
from tabulate import tabulate

from datapane import __rev__, __version__
from datapane.common import JDict, SDict, log

from . import api
from . import config as c
from . import scripts
from .scripts import config as sc

DEBUG: bool = False


# TODO
#  - add info subcommand
#  - convert to use typer (https://github.com/tiangolo/typer) or autoclick
def init(debug: Optional[bool], config_env: str):
    """Init the cmd-line env"""
    api.init(config_env=config_env, debug=debug or False)

    # config_f = c.load_from_envfile(config_env)
    # _debug = debug if debug is not None else c.config.debug
    # setup_logging(verbose_mode=_debug)
    # log.debug(f"Loaded environment from {config_f}")


@dc.dataclass(frozen=True)
class DPContext:
    """
    Any shared context we want to pass across commands,
    easier to just use globals in general tho
    """

    env: str


def success_msg(msg: str):
    click.secho(msg, fg="green")


def failure_msg(msg: str, do_exit: bool = False):
    click.secho(msg, fg="red")
    if do_exit:
        ctx: click.Context = click.get_current_context(silent=True)
        if ctx:
            ctx.exit(2)
        else:
            exit(2)


@contextmanager
def api_error_handler(err_msg: str):
    try:
        yield
    except HTTPError as e:
        if DEBUG:
            log.exception(e)
        else:
            log.error(e)
        failure_msg(err_msg, do_exit=True)


def gen_name() -> str:
    return f"new_{uuid.uuid4().hex}"


def print_table(xs: t.Iterable[SDict], obj_name: str) -> None:
    success_msg(f"Available {obj_name}:")
    print(tabulate(xs, headers="keys", showindex=True))


class CatchIncompatibleVersion(click.Group):
    def __call__(self, *args, **kwargs):
        try:
            return self.main(*args, **kwargs)
        except api.IncompatibleVersionException as exc:
            if DEBUG:
                log.exception(exc)
            failure_msg(str(exc))
        except HTTPError as e:
            if DEBUG:
                log.exception(e)
            failure_msg(str(e), do_exit=True)
        except Exception as e:
            if DEBUG:
                log.exception(e)
            failure_msg(str(e), do_exit=True)


###############################################################################
# Main
@click.group(cls=CatchIncompatibleVersion)
@click.option("--debug/--no-debug", default=None, help="Enable additional debug output.")
@click.option("--env", default=c.DEFAULT_ENV, help="Alternate config environment to use.")
@click.version_option(version=f"{__version__} ({__rev__})")
@click.pass_context
def cli(ctx, debug: bool, env: str):
    """Datapane CLI Tool"""
    global DEBUG
    DEBUG = debug
    init(debug, env)
    ctx.obj = DPContext(env=env)


###############################################################################
# Auth
@cli.command()
@click.option("--token", prompt="Your API Token", help="API Token to the Datapane server.")
@click.option("--server", default="https://datapane.com", help="Datapane API Server URL.")
@click.pass_obj
def login(obj: DPContext, token, server):
    """Login to a server with the given API token."""
    config = c.Config(server=server, token=token)
    r = api.check_login(config=config)

    # update config with valid values
    with c.update_config(obj.env) as x:
        x["server"] = server
        x["token"] = token

    # click.launch(f"{server}/settings/")
    success_msg(f"Logged in to {server} as {r.username}")


@cli.command()
@click.pass_obj
def logout(obj: DPContext):
    """Logout from the server and reset the API token in the config file."""
    with c.update_config(obj.env) as x:
        x["server"] = c.DEFAULT_SERVER
        x["token"] = c.DEFAULT_TOKEN

    success_msg(f"Logged out from {c.config.server}")


@cli.command()
def ping():
    """Check can connect to the server."""
    try:
        r = api.check_login()
        success_msg(f"Connected to {c.config.server} as {r.username}")
    except HTTPError as e:
        failure_msg(f"Couldn't successfully connect to {c.config.server}, check your login details")
        log.error(e)


###############################################################################
# Blobs
@cli.group()
def blob():
    """Commands to work with Blobs"""
    ...


@blob.command()
@click.argument("name")
@click.argument("file", type=click.Path(exists=True))
@click.option("--visibility", type=click.Choice(["PUBLIC", "ORG", "PRIVATE"]), default="PRIVATE")
def upload(file: str, name: str, visibility: str):
    """Upload a csv or Excel file as a Datapane Blob"""
    log.info(f"Uploading {file}")
    r = api.Blob.upload_file(file, name=name, visibility=visibility)
    success_msg(f"Uploaded {click.format_filename(file)} to {r.url}")


@blob.command()
@click.argument("name")
@click.option("--owner")
@click.option("--version")
@click.argument("file", type=click.Path())
def download(name: str, owner: str, version: str, file: str):
    """Download blob referenced by NAME to FILE"""
    r = api.Blob.get(name, owner=owner, version=version)
    r.download_file(file)
    success_msg(f"Downloaded {r.url} to {click.format_filename(file)}")


@blob.command()
@click.argument("name")
def delete(name: str):
    """Delete a blob"""
    api.Blob.get(name).delete()
    success_msg(f"Deleted Blob {name}")


@blob.command()
def list():
    """List blobs"""
    print_table(api.Blob.list(), "Blobs")


###############################################################################
# Scripts
@cli.group()
def script():
    """Commands to work with Scripts"""
    ...


@script.command(name="init")
@click.argument("name", default=lambda: os.path.basename(os.getcwd()))
def script_init(name: str):
    """Initialise a new script project"""
    # NOTE - only supports single hierarchy project dirs
    env = Environment(loader=FileSystemLoader("."))

    def render_file(fname: Path, context: Dict):
        rendered_script = env.get_template(fname.name).render(context)
        fname.write_text(rendered_script)

    # copy the scaffolds into the service
    def copy_scaffold() -> List[Path]:
        dir_path = ir.files("datapane.resources") / "scaffold"
        copy_tree(dir_path, ".")
        return [Path(x.name) for x in dir_path.iterdir()]

    if sc.DATAPANE_YAML.exists():
        raise ValueError("Found existing project, cancelling")

    name = name.replace("-", "_")
    sc.validate_name(name)
    files = copy_scaffold()

    # run the scripts
    _context = dict(name=name)
    for f in files:
        if f.exists() and f.is_file():
            render_file(f, context=_context)
    success_msg(f"Created dp_script.py for project '{name}', edit as needed and upload")


@script.command()
@click.option("--config", type=click.Path(exists=True))
@click.option("--script", type=click.Path(exists=True))
@click.option("--name")
@click.option("--visibility", type=click.Choice(["PUBLIC", "ORG", "PRIVATE"]), default="PRIVATE")
def deploy(name: Optional[str], script: Optional[str], config: Optional[str], visibility: str):
    """Package and deploy a Python script or Jupyter notebook as a Datapane Script bundle"""
    script = script and Path(script)
    config = config and Path(config)
    init_kwargs = dict(visibility=visibility, name=name, script=script, config_file=config)
    kwargs = {k: v for k, v in init_kwargs.items() if v is not None}

    # if not (script or config or sc.DatapaneCfg.exists()):
    #     raise AssertationError(f"Not valid project dir")

    dp_cfg = scripts.DatapaneCfg.create_initial(**kwargs)
    log.debug(f"Packaging and uploading Datapane project {dp_cfg.name}")

    # start the build process
    with click_spinner.spinner(), scripts.build_bundle(dp_cfg) as sdist:

        if DEBUG:
            tf: tarfile.TarFile
            log.debug("Bundle from following files:")
            with tarfile.open(sdist) as tf:
                for n in tf.getnames():
                    log.debug(f"  {n}")

        r: api.Script = api.Script.upload_pkg(sdist, dp_cfg)
        success_msg(f"Uploaded {click.format_filename(str(dp_cfg.script))} to {r.web_url}")


@script.command()
@click.argument("name")
@click.option("--version")
@click.option("--owner")
def download(name: str, owner: str, version: str):
    """Download script referenced by NAME to FILE"""
    s = api.Script.get(name, owner=owner, version=version)
    fn = s.download_pkg()
    success_msg(f"Downloaded {s.url} to {click.format_filename(str(fn))}")


@script.command()
@click.argument("name")
def delete(name: str):
    """Delete a script"""
    api.Script.get(name).delete()
    success_msg(f"Deleted Script {name}")


@script.command()
def list():
    """List Scripts"""
    print_table(api.Script.list(), "Scripts")


def process_cmd_param_vals(params: Tuple[str, ...]) -> JDict:
    """Convert a list of k=v to a typed JSON dict"""

    def convert_param_val(x: str) -> t.Union[int, float, str, bool]:
        # TODO - this can be optimised / cleaned-up
        try:
            return int(x)
        except ValueError:
            try:
                return float(x)
            except ValueError:
                try:
                    return bool(strtobool(x))
                except ValueError:
                    return x

    def split_param(xs: Tuple[str]) -> Iterator[t.Tuple[str, str]]:
        err_msg = "'{}', should be name=value"
        for x in xs:
            try:
                k, v = x.split("=", maxsplit=1)
            except ValueError:
                raise click.BadParameter(err_msg.format(x))
            if not k or not v:
                raise click.BadParameter(err_msg.format(x))
            yield (k, v)

    return {k: convert_param_val(v) for (k, v) in split_param(params)}


@script.command()
@click.option("--parameter", "-p", multiple=True)
@click.option("--cache/--disable-cache", default=True)
@click.option("--wait/--no-wait", default=True)
@click.option("--owner")
@click.option("--show-output", is_flag=True, default=False, help="Display the run output")
@click.argument("name")
def run(name: str, parameter: Tuple[str], cache: bool, wait: bool, owner: str, show_output: bool):
    """Run a report"""
    params = process_cmd_param_vals(parameter)
    log.info(f"Running script with parameters {params}")
    script = api.Script.get(name, owner=owner)
    with api_error_handler("Error running script"):
        r = script.run(parameters=params, cache=cache)
    if wait:
        with click_spinner.spinner():
            while not r.is_complete():
                time.sleep(2)
                r.refresh()
            log.debug(f"Run completed with status {r.status}")
            if show_output:
                click.echo(r.output)
            if r.status == "SUCCESS":
                if r.result:
                    success_msg(f"Script result - '{r.result}'")
                if r.report:
                    report = api.Report.by_id(r.report)
                    success_msg(f"Report generated at {report.web_url}")
            else:
                failure_msg(f"Script run failed/cancelled\n{r.error_msg}: {r.error_detail}")

    else:
        success_msg(f"Script run started, view at {script.web_url}")


###############################################################################
# Reports
@cli.group()
def report():
    """Commands to work with Reports"""
    ...


@report.command()
@click.argument("name")
@click.argument("files", type=click.Path(), nargs=-1, required=True)
@click.option("--headline", default="Untitled")
@click.option("--visibility", type=click.Choice(["PUBLIC", "ORG", "PRIVATE"]), default="PRIVATE")
def create(files: Tuple[str], name: str, headline: str, visibility: str):
    """Create a Report from the provided FILES"""
    blocks = [api.Asset.upload_file(file=Path(f)) for f in files]
    r = api.Report(*blocks)
    r.publish(name=name, headline=headline, visibility=visibility)
    success_msg(f"Created Report {r.web_url}")


@report.command()
@click.argument("name")
def delete(name: str):
    """Delete a report"""
    api.Report.get(name).delete()
    success_msg(f"Deleted Report {name}")


@report.command()
def list():
    """List Reports"""
    print_table(api.Report.list(), "Reports")


@report.command()
@click.argument("name")
@click.option("--version")
@click.option("--owner")
@click.option("--filename", default="output.html", type=click.Path())
def render(name: str, version: str, owner: str, filename: str):
    """Render a report to a static file"""
    api.Report.get(name, version=version, owner=owner).render()


#############################################################################
# Variables
@cli.group()
def variable():
    """Commands to work with Variables"""
    ...


@variable.command()
@click.argument("name", required=True)
@click.argument("value", required=True)
@click.option("--visibility", type=click.Choice(["PUBLIC", "ORG", "PRIVATE"]), default="PRIVATE")
def add(name: str, value: str, visibility: str):
    """
    Add a variable

    NAME: name of variable
    VALUE: value of variable

    --visibility(default=PRIVATE):
    PUBLIC: visible to everyone,
    ORG: visible to all authenticated users in an organization (note: this option is only for organizations),
    PRIVATE: only visible to you
    """
    api.Variable.add(name, value, visibility)
    success_msg(f"Created variable: {name}")


@variable.command()
def list():
    """List all variables"""
    print_table(api.Variable.list(), "Variables")


@variable.command()
@click.argument("name", required=True)
@click.option("--owner")
@click.option("--version")
@click.option("--show", is_flag=True, help="Print the variable value.")
def get(name, owner, version, show):
    """Get variable value using variable name"""
    res = api.Variable.get(name, owner=owner, version=version)
    if show:
        print(str(res.value).strip())
    else:
        print_table([{"name": name, "value": res.value, "visibility": res.visibility}], "Variable")


@variable.command()
@click.argument("name")
def delete(name):
    """Delete a variable using variable name"""
    api.Variable.get(name).delete()
    success_msg(f"Deleted variable {name}")
