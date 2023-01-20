from datapane.client.utils import display_msg
from datapane.common import DPError


class IncompatibleVersionError(DPError):
    pass


class UnsupportedResourceError(DPError):
    pass


class ReportTooLargeError(DPError):
    pass


class InvalidTokenError(DPError):
    pass


class UnsupportedFeatureError(DPError):
    pass


class InvalidReportError(DPError):
    pass


class MissingCloudPackagesError(DPError):
    def __init__(self, *a, **kw):
        # quick hack until we setup a conda meta-package for cloud
        self.args = (
            "Cloud packages not found, please run `pip install datapane[cloud]` or `conda install -c conda-forge nbconvert flit-core`",
        )


class NotebookException(Exception):
    """Exception raised when a Notebook to Datapane conversion fails."""

    def _render_traceback_(self):
        display_msg(
            f"""**Conversion failed**

{str(self)}"""
        )


class NotebookParityException(NotebookException):
    """Exception raised when IPython output cache is not in sync with the saved notebook"""


class BlocksNotFoundException(NotebookException):
    """Exception raised when no blocks are found during conversion"""
