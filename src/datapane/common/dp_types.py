import enum
import typing as t
from datetime import timedelta
from os import PathLike
from pathlib import Path

# Typedefs
# A JSON-serialisable config object
SDict = t.Dict[str, t.Any]
SList = t.List[str]
JSON = t.Union[str, int, float, bool, None, t.Mapping[str, "JSON"], t.List["JSON"]]
JDict = SDict  # should be JSON
JList = t.List[JSON]
MIME = t.NewType("MIME", str)
URL = t.NewType("URL", str)
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


class DPMode(enum.Enum):
    """DP can operate in multiple modes as specified by this Enum"""

    APP = enum.auto()
    LIBRARY = enum.auto()
    FRAMEWORK = enum.auto()


# default in Library mode
__dp_mode: DPMode = DPMode.LIBRARY


def get_dp_mode() -> DPMode:
    global __dp_mode
    return __dp_mode


def set_dp_mode(dp_mode: DPMode) -> None:
    global __dp_mode
    __dp_mode = dp_mode
