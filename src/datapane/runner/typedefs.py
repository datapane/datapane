import dataclasses as dc
import json
from typing import List, Optional, TextIO

from datapane.common import Hash


@dc.dataclass
class RunResult:
    # TODO - this should be encrypted using django.sign - however is a hashid for now...
    report_id: Optional[str] = None
    script_result: Optional[str] = None
    output: Optional[str] = None
    cacheable: bool = False
    # used for GC - tho could get by xpath
    cas_refs: List[Hash] = dc.field(default_factory=list)
    asset_ids: List[int] = dc.field(default_factory=list)

    def to_json(self, stream: TextIO):
        json.dump(dc.asdict(self), stream)


@dc.dataclass
class ErrorResult:
    error: str
    error_detail: str = ""
    output: Optional[str] = None
    debug: Optional[str] = None

    def to_json(self, stream: TextIO):
        json.dump(dc.asdict(self), stream)
