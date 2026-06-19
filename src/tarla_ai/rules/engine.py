"""Kural tabanli karar uretimi (Belge Bolum 5.1).

Esik degerleri dogrudan oneriye donusturur. Phase 2'de makine ogrenmesi bu
katmanin uzerine gelir; ilk sezon kararlari buradan uretilir.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from tarla_ai.rules.thresholds import (
    NITROGEN_NDRE_THRESHOLD,
    SOIL_PH_HEALTHY_MAX,
    SOIL_PH_HEALTHY_MIN,
)


class Severity(StrEnum):
    """Oneri ciddiyet seviyesi."""

    OK = "ok"
    WARNING = "warning"
    ACTION = "action"


@dataclass(frozen=True)
class Recommendation:
    """Tek bir kural degerlendirme sonucu (immutable).

    Attributes:
        topic: Konu (orn. "azot", "pH").
        severity: Ciddiyet.
        message: Insan-okunur aciklama (cifci arayuzunde gosterilir).
        value: Degerlendirilen olcum degeri.
    """

    topic: str
    severity: Severity
    message: str
    value: float


def evaluate_ndre(
    ndre_value: float, threshold: float = NITROGEN_NDRE_THRESHOLD
) -> Recommendation:
    """NDRE degerine gore azot durumu onerisi (Belge 9.4).

    NDRE < esik -> azot eksikligi -> gubreleme onerisi.
    """
    if ndre_value < threshold:
        return Recommendation(
            topic="azot",
            severity=Severity.ACTION,
            message=(
                f"NDRE={ndre_value:.3f} < {threshold}: azot eksikligi sinyali. "
                "Degisken dozlu (VRA) ust gubreleme degerlendir."
            ),
            value=ndre_value,
        )
    return Recommendation(
        topic="azot",
        severity=Severity.OK,
        message=f"NDRE={ndre_value:.3f}: azot durumu yeterli.",
        value=ndre_value,
    )


def evaluate_soil_ph(
    ph: float,
    healthy_min: float = SOIL_PH_HEALTHY_MIN,
    healthy_max: float = SOIL_PH_HEALTHY_MAX,
) -> Recommendation:
    """Toprak pH degerine gore oneri (Belge 5.1)."""
    if ph < healthy_min:
        return Recommendation(
            topic="pH",
            severity=Severity.WARNING,
            message=f"pH={ph:.1f} dusuk (asidik). Kireçleme degerlendir.",
            value=ph,
        )
    if ph > healthy_max:
        return Recommendation(
            topic="pH",
            severity=Severity.WARNING,
            message=f"pH={ph:.1f} yuksek (alkali). Besin alimini kontrol et.",
            value=ph,
        )
    return Recommendation(
        topic="pH",
        severity=Severity.OK,
        message=f"pH={ph:.1f}: saglikli aralikta.",
        value=ph,
    )
