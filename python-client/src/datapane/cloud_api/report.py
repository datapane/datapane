"""
Datapane Reports Object

Describes the `Report` object
"""
from __future__ import annotations

import typing as t

from .dp_object import DPObjectRef


class CloudReport(DPObjectRef):
    """
    A Report that has been uploaded to datapane.com
    """

    # NOTE - uploading handled via the DPCloudUploader processor
    list_fields: t.List[str] = ["name", "web_url", "project"]
    endpoint: str = "/reports/"
