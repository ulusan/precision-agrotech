"""Sulama suyu raporu doğrulama — tam sulama kararı için yeterli mi?

soil/validation.py ile simetrik. Eksik veri uydurulmaz; hangi parametrenin
eksik olduğu açıkça raporlanır.

Ayrım:
- MINIMUM alanlar (pH, EC): bunlar olmadan hiçbir yorum yapılamaz.
- TAM alanlar: tuzluluk + sodisite + toksisite riskinin TAM değerlendirmesi
  için gereken set (SAR, Na, Cl, HCO₃, B). Eksikse karar "ihtiyatlı" moda düşer.
"""

from __future__ import annotations

from dataclasses import dataclass

from tarla_ai.water.parsing import WaterReport

# pH + EC olmadan hiçbir değerlendirme yapılamaz.
MINIMUM_FIELDS: tuple[tuple[str, str], ...] = (
    ("ph",      "pH"),
    ("ec_ds_m", "EC (Tuzluluk)"),
)

# Toprak yapısı + toksisite riskinin tam değerlendirmesi için gereken set.
FULL_ASSESSMENT_FIELDS: tuple[tuple[str, str], ...] = (
    ("sar",              "SAR"),
    ("sodium_mg_l",      "Sodyum (Na)"),
    ("chloride_mg_l",    "Klorür (Cl)"),
    ("bicarbonate_mg_l", "Bikarbonat (HCO₃)"),
    ("boron_mg_l",       "Bor (B)"),
)


@dataclass(frozen=True)
class WaterValidation:
    """Sulama suyu raporunun karar-yeterlilik sonucu."""

    has_minimum: bool                    # pH + EC var mı?
    is_full_assessment: bool             # tam risk değerlendirmesi mümkün mü?
    missing_minimum: tuple[str, ...]
    missing_full: tuple[str, ...]        # eksik tam-değerlendirme alanları

    @property
    def missing_full_count(self) -> int:
        return len(self.missing_full)


def validate_water(report: WaterReport) -> WaterValidation:
    """WaterReport'un minimum ve tam-değerlendirme alanlarını kontrol et."""
    missing_min = [
        label for fname, label in MINIMUM_FIELDS
        if getattr(report, fname, None) is None
    ]
    missing_full = [
        label for fname, label in FULL_ASSESSMENT_FIELDS
        if getattr(report, fname, None) is None
    ]

    return WaterValidation(
        has_minimum=len(missing_min) == 0,
        is_full_assessment=len(missing_full) == 0,
        missing_minimum=tuple(missing_min),
        missing_full=tuple(missing_full),
    )
