"""Support for handling datapane script config"""
import dataclasses as dc
import json
import os
import re
from pathlib import Path
from typing import ClassVar, List, Optional

import dacite
import importlib_resources as ir
import jsonschema
import nbconvert
import nbformat
import yaml
from traitlets.config import Config as TConfig

from datapane.common import SDict, log

# app paths
DATAPANE_YAML = Path("datapane.yaml")
PYPROJECT_TOML = Path("pyproject.toml")
DEFAULT_PY = Path("dp_script.py")
DEFAULT_IPYNB = Path("dp_script.ipynb")
re_check_name = re.compile(r"^\w+$")

# TODO - look at other libs
#  - https://lidatong.github.io/dataclasses-json/ (or marshmallow)
#  - https://github.com/edaniszewski/bison
#  - https://pydantic-docs.helpmanual.io/

# TODO
#  - add support to extract elements from inline and pyproject
#  - use datapane.py by default as script
#  - convert notebook (use 1st markdown as docstring?)


def validate_name(x: str):
    if re_check_name.match(x) is None:
        raise AssertionError(f"'{x}' is not a valid service name, must be [a-z0-9-_]")


def default_title() -> str:
    return "New Untitled Script"


@dc.dataclass
class DatapaneCfg:
    """Wrapper around the datapane script config"""

    name: str = "datapane"
    # relative path to script
    script: Path = dc.field(
        default_factory=lambda: DEFAULT_IPYNB if DEFAULT_IPYNB.exists() else DEFAULT_PY
    )
    config: dc.InitVar[Path] = None
    proj_dir: ClassVar[Path] = None

    # run options
    container_image_name: str = ""
    # docker_image: Optional[str] = None
    parameters: List[SDict] = dc.field(default_factory=list)
    pre_commands: List[str] = dc.field(default_factory=list)
    post_commands: List[str] = dc.field(default_factory=list)

    # metadata
    title: str = dc.field(default_factory=default_title)
    description: str = "Datapane Script"
    repo: str = ""
    visibility: str = "PRIVATE"

    # build options
    include: List[str] = dc.field(default_factory=list)
    exclude: List[str] = dc.field(default_factory=list)
    requirements: List[str] = dc.field(default_factory=list)

    def __post_init__(self, config: Optional[Path]):
        validate_name(self.name)

        # TODO - support running config/script from another dir with abs paths
        # all paths are relative and we're running from the same dir
        if config:
            assert (
                config.parent == self.script.parent == Path(".")
            ), "All files must be in the main project directory"
        # we must be in the project dir for now
        # TODO - move this logic to create_initial
        self.proj_dir = self.script.resolve(strict=False).parent
        assert os.getcwd() == os.path.abspath(self.proj_dir), "Please run from source directory"

        # # config and script dir must be in same dir
        # if config:
        #     assert config.resolve(strict=True).parent == self.proj_dir, \
        #         "Config and Script directory must be in same directory"

        # validate config
        if self.parameters:
            config_schema = json.loads(
                ir.read_text("datapane.resources", "script_parameter_def.schema.json")
            )
            jsonschema.validate(self.parameters, config_schema)

    @classmethod
    def create_initial(cls, config_file: Path = None, script: Path = None, **kw) -> "DatapaneCfg":
        raw_config = {}

        if config_file:
            assert config_file.exists()
        else:
            config_file = DATAPANE_YAML

        if config_file.exists():
            # read config from the yaml file
            log.debug(f"Reading datapane config file at {config_file}")
            with config_file.open("r") as f:
                raw_config = yaml.safe_load(f)
        elif PYPROJECT_TOML.exists():
            # TODO - implement pyproject parsing
            log.warning("pyproject.toml found but not currently supported - ignoring")
            raw_config = {}
        elif script:
            # we don't have a default config - perhaps in the script file
            # TODO - try read config from source-code
            abs_script = config_file.parent / script
            if script.suffix == ".ipynb":
                log.debug("Converting notebook")
                mod_code = extract_py_notebook(abs_script)
            else:
                mod_code = abs_script.read_text()
            log.debug("Reading config from python script/notebook")
            log.debug(mod_code)

        # overwrite config with command-line options
        if script:
            raw_config.update(script=script)
        raw_config.update(kw)

        dp_cfg = dacite.from_dict(cls, data=raw_config, config=dacite.Config(cast=[Path]))
        return dp_cfg

    @classmethod
    def create(cls, **raw_config) -> "DatapaneCfg":
        return dacite.from_dict(cls, data=raw_config, config=dacite.Config(cast=[Path]))

    @staticmethod
    def exists() -> bool:
        check_files = [DATAPANE_YAML, PYPROJECT_TOML, DEFAULT_PY, DEFAULT_IPYNB]
        return any(x.exists() for x in check_files)

    def to_dict(self) -> SDict:
        d = dc.asdict(self)
        # TODO - make script a getter/setter
        d["script"] = str(d["script"])  # this is hacky - need a better DTO-conversion method
        build_fields = {"include", "exclude"}
        return {k: v for k, v in d.items() if k not in build_fields}


def extract_py_notebook(in_file: Path) -> str:
    """Extract the python code from a given notebook"""
    # we use config for importing
    c = TConfig()
    c.PythonExporter.preprocessors = []
    # load the notebook
    notebook: nbformat.NotebookNode = nbformat.read(str(in_file), as_version=4)
    # TODO - any preprocessing here
    # convert it
    conv = nbconvert.PythonExporter(config=c)
    (body, resources) = conv.from_notebook_node(notebook)
    # (body, resources) = conv.from_filename(str(in_file))
    # write the notebook
    # writer = nbconvert.writers.FilesWriter()
    # writer.write(body, resources, "output_notebook")
    return body
