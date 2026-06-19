"""Kural tabanli karar motoru (Belge Bolum 5.1 - ilk asama)."""

from tarla_ai.rules.engine import Recommendation, evaluate_ndre, evaluate_soil_ph
from tarla_ai.rules.thresholds import (
    NITROGEN_NDRE_THRESHOLD,
    SOIL_PH_HEALTHY_MAX,
    SOIL_PH_HEALTHY_MIN,
)

__all__ = [
    "Recommendation",
    "evaluate_ndre",
    "evaluate_soil_ph",
    "NITROGEN_NDRE_THRESHOLD",
    "SOIL_PH_HEALTHY_MIN",
    "SOIL_PH_HEALTHY_MAX",
]
