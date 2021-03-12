import typing as t

import importlib_resources as ir
from lxml import etree

from .utils import log

local_report_def = ir.files("datapane.resources.report_def")
rng_validator = etree.RelaxNG(file=str(local_report_def / "full_schema.rng"))

dp_namespace: str = "https://datapane.com/schemas/report/1/"


def _log_validation_error(xml_str, xml_doc):
    if not xml_str:
        xml_str = etree.tounicode(xml_doc, pretty_print=True)
    log.error("Error validating report document:")
    log.error(xml_str)


def validate_report_doc(
    xml_str: t.Optional[str] = None, xml_doc: t.Optional[etree.Element] = None, raise_exception: bool = True
) -> bool:
    """Validate the model against the schema"""
    # get the doc
    if xml_str:
        xml_doc = etree.fromstring(xml_str)
    # TODO - should remove this debug log at some point
    # if log.isEnabledFor(logging.DEBUG):
    #     log.debug(f"Validating\n{etree.tounicode(xml_doc, pretty_print=True)}")

    # NOTE - this is messy, but works... :)
    if raise_exception:
        try:
            rng_validator.assertValid(xml_doc)
            return True
        except Exception:
            _log_validation_error(xml_str, xml_doc)
            raise
    else:
        if rng_validator.validate(xml_doc):
            return True
        else:
            _log_validation_error(xml_str, xml_doc)
            return False
