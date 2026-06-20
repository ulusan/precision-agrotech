"""Soil domain — toprak analizi parse + referans + yorum."""

from tarla_ai.soil.analysis import ParamStatus, SoilAnalysis, interpret_soil
from tarla_ai.soil.parsing import SoilReport, parse_soil_pdf, parse_soil_pdf_bytes
from tarla_ai.soil.reference import SOIL_REFERENCE, SoilReference

__all__ = [
    "SoilReport", "parse_soil_pdf", "parse_soil_pdf_bytes",
    "SoilReference", "SOIL_REFERENCE",
    "ParamStatus", "SoilAnalysis", "interpret_soil",
]
