import dataclasses as dc
import json
import math
import re
import typing as t
from collections.abc import Sized
from numbers import Number

import importlib_resources as ir
from lxml import etree
from lxml.etree import DocumentInvalid
from lxml.etree import _Element as ElementT
from micawber import ProviderException, bootstrap_basic, bootstrap_noembed, cache

from .dp_types import HTML, DPError, SSDict, log

local_view_resources = ir.files("datapane.resources.view_resources")
rng_validator = etree.RelaxNG(file=str(local_view_resources / "full_schema.rng"))

dp_namespace: str = "https://datapane.com/schemas/report/1/"
ViewXML = str


def load_doc(x: str) -> ElementT:
    parser = etree.XMLParser(strip_cdata=False, recover=True, remove_blank_text=True, remove_comments=True)
    return etree.fromstring(x, parser=parser)


def is_valid_id(id: str) -> bool:
    """(cached) regex to check for a xsd:ID name"""
    return re.fullmatch(r"^[a-zA-Z_][\w.-]*$", id) is not None


def validate_view_doc(
    xml_str: t.Optional[str] = None, xml_doc: t.Optional[ElementT] = None, quiet: bool = False
) -> bool:
    """Validate the model against the schema, throws an etree.DocumentInvalid if not"""
    assert xml_str or (xml_doc is not None)
    if xml_str:
        xml_doc = etree.fromstring(xml_str)

    try:
        rng_validator.assertValid(xml_doc)
        return True
    except DocumentInvalid:
        if not quiet:
            xml_str = xml_str if xml_str else etree.tounicode(xml_doc, pretty_print=True)
            log.error(f"Error validating report document:\n\n{xml_str}\n{rng_validator.error_log}\n")
        raise


def conv_attrib(v: t.Any) -> t.Optional[str]:
    """
    Convert a value to a str for use as an ElementBuilder attribute
    - also handles None to a string for optional field values
    """
    # TODO - use a proper serialisation framework here / lxml features
    if v is None:
        return v
    elif isinstance(v, Sized) and len(v) == 0:
        return None
    elif isinstance(v, str):
        return v
    elif isinstance(v, Number) and type(v) != bool:
        if math.isinf(v) and v > 0:
            return "INF"
        elif math.isinf(v) and v < 0:
            return "-INF"
        elif math.isnan(v):
            return "NaN"
        else:
            return str(v)
    else:
        return json.dumps(v)


def mk_attribs(**attribs: t.Any) -> SSDict:
    """convert attributes, dropping None and empty values"""
    return {str(k): v1 for (k, v) in attribs.items() if (v1 := conv_attrib(v)) is not None}


#####################################################################
# Embed Asset Helpers
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
    except ProviderException:
        # add noembed to the list and try again
        try:
            log.debug("Initialising NoEmbed OEmbed provider")
            bootstrap_noembed(registry=providers)
            r = providers.request(url, maxwidth=width, maxheight=height)
        except ProviderException:
            raise DPError(f"No embed provider found for URL '{url}' - is there an active internet connection?")

    return Embedded(html=r["html"], title=r.get("title", "Title"), provider=r.get("provider_name", "Embedding"))
