"""Katmanlar arası frozen DTO sözleşmesi.

DroneAnalysis ve SoilAnalysis burada re-export edilir;
UI ve CLI bu modülden import eder — domain paketlerine doğrudan bağlanmaz.
"""

from __future__ import annotations

from tarla_ai.drone.analysis import DroneAnalysis
from tarla_ai.soil.analysis import ParamStatus, SoilAnalysis

__all__ = ["DroneAnalysis", "SoilAnalysis", "ParamStatus"]
