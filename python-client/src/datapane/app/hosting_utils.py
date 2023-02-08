import enum
import pathlib
import sys
import typing as t

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

# load your files into the image
# To exclude files, setup a .dockerignore
COPY ./ /app/

%(install_deps_block)s

# execute your app (what to run on the server)
CMD exec python '%(file_to_exec)s'
""".lstrip()


_pip_install_block = r"""
# Install the App dependencies
RUN \
  if test -f 'requirements.txt'; then \
    pip install --no-cache-dir -r requirements.txt ;\
  fi
""".strip()


def generate_dockerfile(
    python_version: str = DEFAULT_PYTHON_VERSION,
    installer: SupportedInstallers = DEFAULT_INSTALLER,
    file_to_exec: t.Union[str, None] = None,
):
    # TODO: better error handling
    assert _is_valid_python_version(python_version), "The python version you specified is not supported"
    assert _is_valid_installer(installer), "The chosen installer is not supported"

    if installer == SupportedInstallers.pip:
        install_deps_block = _pip_install_block
    else:
        # TODO: we shouldn't ever get here
        install_deps_block = ""

    if file_to_exec is None:
        file_to_exec = "<app>.py"

    return DOCKERFILE_TEMPLATE % dict(
        python_version=python_version,
        install_deps_block=install_deps_block,
        file_to_exec=file_to_exec,
    )


def python_files(cwd: t.Union[str, pathlib.Path] = ".", /):
    cwd = pathlib.Path(cwd) if isinstance(cwd, str) else cwd
    for path in cwd.glob("*.py"):
        if not path.is_file():
            continue
        # ignoring "hidden" files
        if path.name.startswith((".", "_")):
            continue
        yield path


def _is_valid_python_version(python_version: str) -> bool:
    try:
        return SUPPORTED_PYTHON_VERSIONS.contains(python_version)
    except InvalidVersion:
        return False


def _is_valid_installer(installer: t.Union[SupportedInstallers, str]) -> bool:
    return installer in SupportedInstallers.__members__
