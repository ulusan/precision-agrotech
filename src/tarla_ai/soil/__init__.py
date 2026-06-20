"""Soil domain — toprak analizi parse + referans + yorum."""

from tarla_ai.soil.analysis import ParamStatus, SoilAnalysis, interpret_soil
from tarla_ai.soil.parsing import SoilReport, parse_soil_pdf, parse_soil_pdf_bytes
from tarla_ai.soil.reference import SOIL_REFERENCE, SoilReference
from tarla_ai.soil.validation import REQUIRED_FIELDS, SoilValidation, validate_soil

__all__ = [
    "SoilReport", "parse_soil_pdf", "parse_soil_pdf_bytes",
    "SoilReference", "SOIL_REFERENCE",
    "ParamStatus", "SoilAnalysis", "interpret_soil",
    "SoilValidation", "validate_soil", "REQUIRED_FIELDS",
]
