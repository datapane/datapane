import enum
import pathlib
import sys
import typing as t
from shlex import quote

from packaging.specifiers import SpecifierSet
from packaging.version import InvalidVersion


@enum.unique
class SupportedInstallers(str, enum.Enum):
    pip = "pip"

    def __str__(self):
        return self._name_

    @classmethod
    def as_list(cls):
        return [m._name_ for m in cls.__members__.values()]


DEFAULT_INSTALLER = SupportedInstallers.pip
DEFAULT_PYTHON_VERSION = "{version.major}.{version.minor}".format(version=sys.version_info)
SUPPORTED_PYTHON_VERSIONS = SpecifierSet(">=3.8,<3.12")


# use printf-style formatting, to avoid conflicting with sh/docker variables
DOCKERFILE_TEMPLATE = r"""
ARG PYTHON_VERSION='%(python_version)s'

FROM python:${PYTHON_VERSION}
WORKDIR /app/

%(install_deps_block)s

# load your files into the image
# To exclude files, setup a .dockerignore
COPY ./ .

%(notebook_convert_block)s

# execute your app (what to run on the server)
CMD exec python %(app_file)s
""".lstrip()

_pip_install_block = r"""
# Install the App dependencies
# Note: If your requirements.txt file depends on other files,
#       you should change to 'COPY ./ .'.
# If you don't have a requirements.txt file:
#  - remove the below lines
#  - let us know your usecase, so we can improve Datapane!
COPY ./requirements.txt .
RUN \
  echo "Installing dependencies from requirements.txt..." \
  && pip install --no-cache-dir -r requirements.txt
""".strip()

_notebook_convert_block = r"""
# Note: Datapane currently expects a python file to execute.
#       This converts your notebook to a python file.
# If you face issues, please let us know!
RUN \
  echo "Generating %(output_path)s from your notebook %(notebook_path)s..." \
  && datapane app generate script-from-nb --nb %(notebook_path)s --out %(output_path)s
"""


def generate_dockerfile(
    python_version: str = DEFAULT_PYTHON_VERSION,
    installer: SupportedInstallers = DEFAULT_INSTALLER,
    app_file: t.Union[str, pathlib.Path, None] = None,
):
    # TODO: better error handling
    assert _is_valid_python_version(python_version), "The python version you specified is not supported"
    assert _is_valid_installer(installer), "The chosen installer is not supported"

    if installer == SupportedInstallers.pip:
        install_deps_block = _pip_install_block
    else:
        # TODO: we shouldn't ever get here
        install_deps_block = ""

    if app_file is None:
        app_file = "<app>.py"
    app_file = pathlib.Path(app_file)

    if app_file.suffix == ".ipynb":
        notebook_convert_block = _notebook_convert_block % dict(
            notebook_path=q(app_file),
            output_path=q(app_file.with_suffix(".py")),
        )
        app_file = app_file.with_suffix(".py")
    else:
        notebook_convert_block = ""

    return DOCKERFILE_TEMPLATE % dict(
        python_version=python_version,
        install_deps_block=install_deps_block,
        notebook_convert_block=notebook_convert_block,
        app_file=q(app_file),
    )


def python_files(cwd: t.Union[str, pathlib.Path] = ".", /, extensions: t.Sequence[str] = (".py", ".ipynb")):
    cwd = pathlib.Path(cwd) if isinstance(cwd, str) else cwd

    # iterdir() doesn't define an order.
    # 'sort' it for consistency on ipynb vs py duplicates.
    for path in sorted(cwd.iterdir()):
        if path.suffix not in extensions:
            continue
        # ignoring "hidden" files - POSIX and Python style
        if path.name.startswith((".", "_")):
            continue
        if not path.is_file():
            continue
        yield path


def _is_valid_python_version(python_version: str) -> bool:
    try:
        return SUPPORTED_PYTHON_VERSIONS.contains(python_version)
    except InvalidVersion:
        return False


def _is_valid_installer(installer: t.Union[SupportedInstallers, str]) -> bool:
    return installer in SupportedInstallers.__members__


def q(s: t.Union[str, pathlib.Path]) -> str:
    """Shell-quote a string or path."""
    return quote(str(s))
