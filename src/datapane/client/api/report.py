import dataclasses as dc
import shutil
import typing as t
import uuid
import webbrowser
from copy import deepcopy
from pathlib import Path
from urllib import parse as up

import pandas as pd
from munch import Munch

from datapane.client import config as c
from datapane.common import JSON, JDict, NPath, guess_type, log

from .common import DPTmpFile, Resource
from .dp_object import BEObjectRef, ExportableObjectMixin
from .runtime import _report


def is_jupyter():
    """Checks if inside ipython shell inside browser"""
    return (
        "get_ipython" in __builtins__
        and get_ipython().__class__.__name__ == "ZMQInteractiveShell"  # noqa: F821
    )


class Asset(BEObjectRef, ExportableObjectMixin):
    """We handle Asset's differently as effectively have to store the user request until
    it's been attached to a Datapane Asset block"""

    endpoint = "/assets/"

    file: Path = None
    kwargs: JDict = None

    @classmethod
    def upload_file(cls, file: NPath, **kwargs: JSON) -> "Asset":
        return cls(file=Path(file), kwargs=kwargs)

    @classmethod
    def upload_df(cls, df: pd.DataFrame, **kwargs: JSON) -> "Asset":
        fn = cls._save_df(df)
        return cls(file=fn.file, kwargs=kwargs)

    @classmethod
    def upload_obj(cls, data: t.Any, is_json: bool = False, **kwargs: JSON) -> "Asset":
        fn = cls._save_obj(data, is_json)
        return cls(file=fn.file, kwargs=kwargs)

    def _post_update(self, block_id: int):
        block_url = up.urljoin(c.config.server, f"api/blocks/{block_id}/")
        res = self.post_with_file(self.file, report_block=block_url, **self.kwargs)
        # reset the object internally (we could copy res here?)
        self.dto = res
        self.url = res.url

    def __init__(self, file: Path = None, kwargs: JDict = None):
        super().__init__()
        # storing objects for delayed upload
        if file:
            self.file = Path(file)
        self.kwargs = kwargs

    def __str__(self) -> str:
        return super().__str__() if self.has_dto else str(self.file)

    def __repr__(self) -> str:
        return super().__repr__() if self.has_dto else str(self.file)


# NOTE - hacks re API compatibility
@dc.dataclass(frozen=True)
class Markdown:
    content: str


class Plot(Asset):
    def __init__(self, data: t.Any, **kwargs: JSON):
        out_fn = self._save_obj(data, is_json=False)
        super().__init__(file=out_fn.file, kwargs=kwargs)


class Table(Asset):
    def __init__(self, df: pd.DataFrame, **kwargs: JSON):
        fn = self._save_df(df)
        super().__init__(file=fn.file, kwargs=kwargs)


class JSONObject(Asset):
    def __init__(self, obj: t.Any, **kwargs: JSON):
        out_fn = self._save_obj(obj, is_json=True)
        super().__init__(file=out_fn.file, kwargs=kwargs)


# Internal type to represent the blocks as exposed to the lib consumer
BlockType = t.Union[Asset, Markdown]


def mk_block(b: BlockType) -> JSON:
    r = Munch()
    r.ref_id = str(uuid.uuid4())
    if isinstance(b, Markdown):
        r.type = "MARKDOWN"
        r.content = b.content
    elif isinstance(b, Asset):
        r.type = "ASSET"
        r.asset = None  # block.asset
    return r


class Report(BEObjectRef):
    endpoint: str = "/reports/"
    blocks: t.List[BEObjectRef]
    last_saved: t.Optional[str] = None  # Path to local report
    tmp_report: t.Optional[Path] = None  # Temp local report

    def __init__(self, *blocks: BlockType):
        super().__init__()
        self.blocks = list(blocks)

    def publish(self, name: str, open: bool = False, **kwargs):
        """Deploy the report and its Assets to Datapane"""
        kwargs.update(name=name)
        new_blocks = [mk_block(b) for b in self.blocks]
        res = Resource(self.endpoint).post(blocks=new_blocks, **kwargs)

        # upload assets and attach to the report
        #  - this is a bit hacky as relies on the ordering staying the same
        #  - could update by using refId
        log.info("Uploading assets for Report")
        for (idx, b) in enumerate(res.blocks):
            if b.type == "ASSET":
                asset: Asset = self.blocks[idx]
                asset._post_update(b.id)
        # Set dto based on new URL
        self.url = res.url
        self.refresh()
        # add report to internal API handler for use by_datapane
        _report.append(self)
        if open:
            webbrowser.open_new_tab(self.web_url)
        log.info(f"Report published to Datapane as {self.web_url}")

    def save(self, path: str, headline: str = "Local Report", open: bool = False, **kwargs):
        """Save the report to a local HTML file"""
        from ..report_file_writer import ReportFileWriter

        self.last_saved = path
        # Don't change the blocks class variable as this would prioritise local properties over the DTO
        local_blocks = deepcopy(self.blocks)
        # local_assets is used to clean up any temp files once assets are encoded
        local_assets: t.List[Asset] = []

        for idx, b in enumerate(local_blocks):
            if isinstance(b, Asset):
                local_assets.append(b)
                # Mimic the lifecycle of a remote asset by setting these properties which are normally set in DRF
                b.id = idx
                b.content_type = guess_type(b.file)
        writer = ReportFileWriter(*local_blocks, headline=headline, **kwargs)
        writer.write(path)
        if open:
            webbrowser.open_new_tab(path)

    def preview(self, width: int = 600, height: int = 500):
        """ Preview the report inside IPython notebooks in browser """
        if is_jupyter():
            from IPython.display import IFrame

            # Remove the previous temp report if it's been generated
            if self.tmp_report and self.tmp_report.exists():
                self.tmp_report.unlink()

            # We need to copy the report HTML to a local temp file,
            # as most browsers block iframes to absolute local paths.
            tmpfile = DPTmpFile(ext=".html")
            if self.last_saved:
                # Copy to tmp file if already saved
                shutil.copy(self.last_saved, tmpfile.name)
            else:
                # Else save directly to tmp file
                self.save(path=tmpfile.name)
            self.tmp_report = tmpfile.file

            # NOTE - iframe must be relative path
            iframe_src = self.tmp_report.relative_to(Path(".").absolute())
            return IFrame(src=str(iframe_src), width=width, height=height)
