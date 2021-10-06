import enum
import typing as t
from datetime import timedelta
from os import PathLike
from pathlib import Path

# Typedefs
# A JSON-serialisable config object
SDict = t.Dict[str, t.Any]
SSDict = t.Dict[str, str]
SList = t.List[str]
JSON = t.Union[str, int, float, bool, None, t.Mapping[str, "JSON"], t.List["JSON"]]
JDict = SDict  # should be JSON
JList = t.List[JSON]
MIME = t.NewType("MIME", str)
URL = t.NewType("URL", str)
HTML = t.NewType("HTML", str)
NPath = t.Union[Path, PathLike, str]
Hash = t.NewType("Hash", str)
EnumType = int  # alias for enum values

# Constants
# NOTE - PKL_MIMETYPE and ARROW_MIMETYPE are custom mimetypes
PKL_MIMETYPE = MIME("application/vnd.pickle+binary")
ARROW_MIMETYPE = MIME("application/vnd.apache.arrow+binary")
ARROW_EXT = ".arrow"
TD_1_HOUR = timedelta(hours=1)
TD_1_DAY = timedelta(days=1)
SECS_1_HOUR: int = int(TD_1_HOUR.total_seconds())
SECS_1_WEEK: int = int(timedelta(weeks=1).total_seconds())
SIZE_1_MB: int = 1024 * 1024


class DPMode(enum.Enum):
    """DP can operate in multiple modes as specified by this Enum"""

    SCRIPT = enum.auto()  # run from the cmd-line
    LIBRARY = enum.auto()  # imported into a process
    FRAMEWORK = enum.auto()  # running dp-runner


# default in Library mode
__dp_mode: DPMode = DPMode.LIBRARY


def get_dp_mode() -> DPMode:
    global __dp_mode
    return __dp_mode


def set_dp_mode(dp_mode: DPMode) -> None:
    global __dp_mode
    __dp_mode = dp_mode


################################################################################
# Built-in exceptions
def add_help_text(x: str) -> str:
    return f"{x}\nPlease run with `dp.enable_logging()`, restart your Jupyter kernel/Python instance, and/or visit https://www.github.com/datapane/datapane to raise issue / discuss if error repeats"


class DPError(Exception):
    def __str__(self):
        # update the error message with help text
        return add_help_text(super().__str__())
