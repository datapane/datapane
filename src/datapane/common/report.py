import dataclasses as dc
import re
import typing as t

import importlib_resources as ir
from lxml import etree
from lxml.etree import DocumentInvalid
from micawber import ProviderException, bootstrap_basic, cache

from datapane.client import DPError
from datapane.common import HTML

from .utils import log

local_report_def = ir.files("datapane.resources.report_def")
rng_validator = etree.RelaxNG(file=str(local_report_def / "full_schema.rng"))

dp_namespace: str = "https://datapane.com/schemas/report/1/"


def is_valid_id(id: str) -> bool:
    """(cached) regex to check for a xsd:ID name"""
    return re.fullmatch(r"^[a-zA-Z_][\w.-]*$", id) is not None


def validate_report_doc(
    xml_str: t.Optional[str] = None, xml_doc: t.Optional[etree.Element] = None, quiet: bool = False
) -> bool:
    """Validate the model against the schema, throws an etree.DocumentInvalid if not"""
    assert xml_str or xml_doc
    if xml_str:
        xml_doc = etree.fromstring(xml_str)

    try:
        rng_validator.assertValid(xml_doc)
        return True
    except DocumentInvalid:
        if not xml_str:
            xml_str = etree.tounicode(xml_doc, pretty_print=True)
        if not quiet:
            log.error(f"Error validating report document:\n\n{xml_str}")
        raise


def conv_attrib(v: t.Any) -> t.Optional[str]:
    """
    Convert a value to a str for use as an ElementBuilder attribute
    - also handles None to a string for optional field values
    """
    # TODO - use a proper serialisation framework here / lxml features
    if v is None:
        return v
    v1 = str(v)
    return v1.lower() if isinstance(v, bool) else v1


def conv_attribs(**attribs: t.Any) -> t.Dict[str, str]:
    # convert attributes, dropping None values
    # TODO - uncomment when 3.8+ only
    # self.attributes = {str(k): v1 for (k, v) in kwargs.items() if (v1 := _conv_attrib(v)) is not None}
    return {str(k): conv_attrib(v) for (k, v) in attribs.items() if conv_attrib(v) is not None}


providers = bootstrap_basic(cache=cache.Cache())


@dc.dataclass(frozen=True)
class Embedded:
    html: HTML
    title: str
    provider: str


def get_embed_url(url: str, width: int = 960, height: int = 540) -> Embedded:
    """Return html for an embeddable URL"""
    try:
        r = providers.request(url, maxwidth=width, maxheight=height)
        return Embedded(html=r["html"], title=r.get("title", "Title"), provider=r.get("provider_name", "Embedding"))
    except ProviderException:
        raise DPError(f"No embed provider found for URL '{url}'")
