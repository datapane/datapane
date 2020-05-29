import typing as t
from datetime import timedelta
from os import PathLike

# Typedefs
# A JSON-serialisable config object
SDict = t.Dict[str, t.Any]
SList = t.List[str]
JSON = t.Union[str, int, float, bool, None, t.Mapping[str, "JSON"], t.List["JSON"]]
JDict = SDict  # should be JSON
JList = t.List[JSON]
MIME = str
URL = str
NPath = t.Union[PathLike, str]
Hash = str
EnumType = int  # alias for enum values

# Constants
# NOTE - PKL_MIMETYPE and ARROW_MIMETYPE are custom mimetypes
PKL_MIMETYPE: MIME = "application/vnd.pickle+binary"
ARROW_MIMETYPE: MIME = "application/vnd.apache.arrow+binary"
ARROW_EXT = ".arrow"
TD_1_HOUR = timedelta(hours=1)
SECS_1_HOUR: int = int(TD_1_HOUR.total_seconds())
SECS_1_WEEK: int = int(timedelta(weeks=1).total_seconds())
