import dataclasses as dc
import tarfile
import time
import typing as t
import uuid
from contextlib import contextmanager
from distutils.dir_util import copy_tree
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import click
import click_spinner
import importlib_resources as ir
from jinja2 import Environment, FileSystemLoader
from requests import HTTPError
from tabulate import tabulate

from datapane import __rev__, __version__
from datapane.common import DPError, SDict, _setup_dp_logging, dict_drop_empty, log
from datapane.common.dp_types import add_help_text

from . import analytics, api, apps
from . import config as c
from .apps import config as sc
from .utils import failure_msg, process_cmd_param_vals, success_msg

EXTRA_OUT: bool = False


# TODO
#  - add info subcommand
#  - convert to use typer (https://github.com/tiangolo/typer) or autoclick
def init(verbosity: int, config_env: str):
    """Init the cmd-line env"""
    c.init(config_env=config_env)
    _setup_dp_logging(verbosity=verbosity)

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


def recursive_help(cmd, parent=None):
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
@click.option("--env", default=c.DEFAULT_ENV, help="Alternate config environment to use.")
@click.version_option(version=f"{__version__} ({__rev__})")
@click.pass_context
def cli(ctx, verbose: int, env: str):
    """Datapane CLI Tool"""
    global EXTRA_OUT
    EXTRA_OUT = verbose > 0
    init(verbosity=verbose, config_env=env)
    ctx.obj = DPContext(env=env)


# @cli.command()
# def dumphelp():
#     recursive_help(cli)


###############################################################################
# Auth
@cli.command()
@click.option("--token", default=None, help="API Token to the Datapane server.")
@click.option("--server", default=c.DEFAULT_SERVER, help="Datapane API Server URL.")
@click.pass_obj
def login(obj: DPContext, token, server):
    """Login to a server with the given API token."""
    api.login(token, server, env=obj.env)
    # click.launch(f"{server}/settings/")


@cli.command()
@click.pass_obj
def logout(obj: DPContext):
    """Logout from the server and reset the config file"""
    api.logout(obj.env)


@cli.command()
def ping():
    """Check can connect to the server"""
    try:
        api.ping()
    except HTTPError as e:
        log.error(e)


@cli.command()
def signup():
    """Signup and link your account to the Datapane CLI"""
    api.signup()


@cli.command()
def hello_world():
    """Create and run an example report, and open in the browser"""
    api.hello_world()


###############################################################################
# Files
@cli.group()
def file():
    """Commands to work with Files"""
    ...


@file.command()
@click.argument("name")
@click.argument("file", type=click.Path(exists=True))
@click.option("--project")
def upload(file: str, name: str, project: str):
    """Upload a csv or Excel file as a Datapane File"""
    log.info(f"Uploading {file}")
    r = api.File.upload_file(file, name=name, project=project)
    success_msg(f"Uploaded {click.format_filename(file)} to {r.url}")


@file.command()
@click.argument("name")
@click.option("--owner")
@click.argument("file", type=click.Path())
def download(name: str, owner: str, file: str):
    """Download file referenced by NAME to FILE"""
    r = api.File.get(name, owner=owner)
    r.download_file(file)
    success_msg(f"Downloaded {r.url} to {click.format_filename(file)}")


@file.command()
@click.argument("name")
def delete(name: str):
    """Delete a file"""
    api.File.get(name).delete()
    success_msg(f"Deleted File {name}")


@file.command("list")
def file_list():
    """List files"""
    print_table(api.File.list(), "Files")


###############################################################################
# Apps
@cli.group()
def app():
    """Commands to work with Apps"""
    ...


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
        copy_tree(dir_path, ".")
        return [Path(x.name) for x in dir_path.iterdir()]

    # run the scripts
    files = copy_scaffold()
    for f in files:
        if f.exists() and f.is_file():
            render_file(f, context=context)


@app.command(name="init")
@click.argument("name", default=lambda: sc.generate_name("Report"))
def app_init(name: str):
    """Initialise a new app project"""
    if sc.DATAPANE_YAML.exists():
        failure_msg("Found existing project, cancelling", do_exit=True)

    sc.validate_name(name)
    _context = dict(name=name)

    write_templates("app", _context)
    success_msg(f"Created dp_app.py for project '{name}', edit as needed and upload")


@app.command()
@click.option("--config", type=click.Path(exists=True))
@click.option("--script", type=click.Path(exists=True))
@click.option("--name")
@click.option("--environment")
@click.option("--project")
def deploy(
    name: Optional[str],
    script: Optional[str],
    config: Optional[str],
    environment: Optional[str],
    project: Optional[str],
):
    """Package and deploy a Python script or Jupyter notebook as a Datapane App bundle"""
    script = script and Path(script)
    config = config and Path(config)
    init_kwargs = dict(name=name, script=script, config_file=config, environment=environment, project=project)
    kwargs = dict_drop_empty(init_kwargs, none_only=True)

    # if not (script or config or sc.DatapaneCfg.exists()):
    #     raise DPError(f"Not valid project dir")

    dp_cfg = apps.DatapaneCfg.create_initial(**kwargs)
    log.debug(f"Packaging and uploading Datapane project {dp_cfg.name}")

    # start the build process
    with apps.build_bundle(dp_cfg) as sdist:

        if EXTRA_OUT:
            tf: tarfile.TarFile
            log.debug("Bundle from following files:")
            with tarfile.open(sdist) as tf:
                for n in tf.getnames():
                    log.debug(f"  {n}")

        r: api.App = api.App.upload_pkg(sdist, dp_cfg)
        success_msg(f"Uploaded {click.format_filename(str(dp_cfg.script))} to {r.web_url}")


@app.command()
@click.argument("name")
@click.option("--owner")
def download(name: str, owner: str):
    """Download app referenced by NAME to FILE"""
    s = api.App.get(name, owner=owner)
    fn = s.download_pkg()
    success_msg(f"Downloaded {s.url} to {click.format_filename(str(fn))}")


@app.command()
@click.argument("name")
def delete(name: str):
    """Delete an app"""
    api.App.get(name).delete()
    success_msg(f"Deleted App {name}")


@app.command("list")
def app_list():
    """List Apps"""
    print_table(api.App.list(), "Apps")


@app.command()
@click.option("--parameter", "-p", multiple=True)
@click.option("--cache/--disable-cache", default=True)
@click.option("--wait/--no-wait", default=True)
@click.option("--owner")
@click.option("--show-output", is_flag=True, default=False, help="Display the run output")
@click.argument("name")
def run(
    name: str,
    parameter: Tuple[str],
    cache: bool,
    wait: bool,
    owner: str,
    show_output: bool,
):
    """Run a report"""
    params = process_cmd_param_vals(parameter)
    log.info(f"Running app with parameters {params}")
    app = api.App.get(name, owner=owner)
    with api_error_handler("Error running app"):
        r = app.run(parameters=params, cache=cache)
    if wait:
        with click_spinner.spinner():
            while not r.is_complete():
                time.sleep(5)
                r.refresh()
            log.debug(f"Run completed with status {r.status}")
            if show_output:
                click.echo(r.output)
            if r.status == "SUCCESS":
                if r.result:
                    success_msg(f"App result - '{r.result}'")
                if r.report:
                    report = api.Report.by_id(r.report)
                    success_msg(f"Report generated at {report.web_url}")
            else:
                failure_msg(f"App run failed/cancelled\n{r.error_msg}: {r.error_detail}")

    else:
        success_msg(f"App run started, view at {app.web_url}")


###############################################################################
# Reports
@cli.group()
def report():
    """Commands to work with Reports"""
    ...


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
@click.argument("name", default=lambda: sc.generate_name("Script"))
@click.option("--format", type=click.Choice(["notebook", "script"]), default="notebook")
def report_init(name: str, format: str):
    """Initialise a new report"""

    if format == "notebook":
        template = "report_ipynb"
    else:
        template = "report_py"

    if len(list(Path(".").glob("dp_report.*"))):
        failure_msg("Found existing project, cancelling", do_exit=True)

    sc.validate_name(name)
    _context = dict(name=name)

    write_templates(template, _context)
    success_msg("Created sample report `dp_report`, edit as needed and run")


@report.command()
@click.argument("name")
def delete(name: str):
    """Delete a report"""
    api.Report.get(name).delete()
    success_msg(f"Deleted Report {name}")


@report.command("list")
def report_list():
    """List Reports"""
    print_table(api.Report.list(), "Reports")


# NOTE - NYI - disabled
# @report.command()
# @click.argument("name")
# @click.option("--owner")
# @click.option("--filename", default="output.html", type=click.Path())
# def render(name: str, owner: str, filename: str):
#     """Render a report to a static file"""
#     api.Report.get(name, owner=owner).render()


#############################################################################
# Environments
@cli.group()
def environment():
    """Commands to work with Environments"""
    ...


@environment.command()
@click.argument("name", required=True)
@click.option("--environment", "-env", multiple=True)
@click.option("--docker-image")
@click.option("--project")
def create(name: str, environment: Tuple[str], docker_image: str, project: str):
    """
    Create a environment

    NAME: name of environment
    ENVIRONMENT: environment variables
    DOCKER IMAGE: docker image to be used inside apps
    PROJECT: Project name (optional and only applicable for teams)
    """
    environment = process_cmd_param_vals(environment)
    api.Environment.create(name, environment, docker_image, project)
    success_msg(f"Created environment: {name}")


@environment.command("list")
def environment_list():
    """List all environments"""
    print_table(api.Environment.list(), "Environments")


@environment.command()
@click.argument("name", required=True)
@click.option("--owner")
def get(name, owner):
    """Get environment value using environment name"""
    res = api.Environment.get(name, owner=owner)
    environment = "\n".join([f"{k}={v}" for k, v in res.environment.items()])
    success_msg(f"Available {res.name}:")
    print(f"\nProject - {res.project}")
    print(f"\nEnvironment Variables-----------\n{environment}")
    print(f"\nDocker Image - {res.docker_image}")


@environment.command()
@click.argument("name")
def delete(name):
    """Delete an environment using environment name"""
    api.Environment.get(name).delete()
    success_msg(f"Deleted environment {name}")


#############################################################################
# Schedules
@cli.group()
def schedule():
    """Commands to work with Schedules"""
    ...


@schedule.command()
@click.option("--parameter", "-p", multiple=True)
@click.argument("name", required=True)
@click.argument("cron", required=True)
@click.option("--owner")
def create(name: str, cron: str, parameter: Tuple[str], owner: str):
    """
    Create a schedule

    NAME: Name of the App to run
    CRON: crontab representing the schedule interval
    PARAMETERS: key/value list of parameters to use when running the app on schedule
    [OWNER]: App owner
    """
    params = process_cmd_param_vals(parameter)
    log.info(f"Adding schedule with parameters {params}")
    app_obj = api.App.get(name, owner=owner)
    schedule_obj = api.Schedule.create(app_obj, cron, params)
    success_msg(f"Created schedule: {schedule_obj.id} ({schedule_obj.url})")


@schedule.command()
@click.option("--parameter", "-p", multiple=True)
@click.argument("id", required=True)
@click.argument("cron", required=False)
def update(id: str, cron: str, parameter: Tuple[str]):
    """
    Add a schedule

    ID: ID/URL of the Schedule
    CRON: crontab representing the schedule interval
    PARAMETERS: key/value list of parameters to use when running the app on schedule
    """

    params = process_cmd_param_vals(parameter)
    assert cron or parameter, "Must update either cron or parameters"

    log.info(f"Updating schedule with parameters {params}")

    schedule_obj = api.Schedule.by_id(id)
    schedule_obj.update(cron, params)
    success_msg(f"Updated schedule: {schedule_obj.id} ({schedule_obj.url})")


@schedule.command("list")
def schedule_list():
    """List all schedules"""
    print_table(api.Schedule.list(), "Schedules", showindex=False)


# @schedule.command()
# @click.argument("id", required=True)
# def get(id: str):
#     """Get variable value using variable name"""
#     res = api.Schedule.by_id(id)
#     print_table([res.dto], "Schedule")


@schedule.command()
@click.argument("id", required=True)
def delete(id: str):
    """Delete a schedule by its id/url"""
    api.Schedule.by_id(id).delete()
    success_msg(f"Deleted schedule {id}")
