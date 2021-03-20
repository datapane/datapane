import re
import typing as t

import importlib_resources as ir
from lxml import etree
from lxml.etree import DocumentInvalid

from .utils import log

local_report_def = ir.files("datapane.resources.report_def")
rng_validator = etree.RelaxNG(file=str(local_report_def / "full_schema.rng"))

dp_namespace: str = "https://datapane.com/schemas/report/1/"

# regex to check for a xsd:ID name
re_xml_id = re.compile(r"^[a-zA-Z_][\w.-]*$")


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
