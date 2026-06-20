"""Thin orchestrator — UI/CLI ortak giriş yüzeyi."""

from tarla_ai.analysis.dto import DroneAnalysis, ParamStatus, SoilAnalysis
from tarla_ai.drone.analysis import analyze_scene as analyze_imagery_bytes
from tarla_ai.soil.analysis import interpret_soil
from tarla_ai.soil.parsing import parse_soil_pdf_bytes as analyze_soil_bytes

__all__ = [
    "analyze_imagery_bytes",
    "analyze_soil_bytes",
    "interpret_soil",
    "DroneAnalysis",
    "SoilAnalysis",
    "ParamStatus",
]
