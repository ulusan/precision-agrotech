"""Sulama suyu yorumlama — WaterReport → WaterAnalysis DTO.

soil/analysis.py ile simetrik. Her ölçülen parametre FAO eşikleriyle
karşılaştırılır; ölçülmeyenler "veri yok" olarak ayrı raporlanır (uydurulmaz).
"""

from __future__ import annotations

from dataclasses import dataclass

from tarla_ai.water.parsing import WaterReport
from tarla_ai.water.reference import WATER_REFERENCE, WaterReference

# WaterReference.name → WaterReport alan adı
_REPORT_FIELD_MAP: dict[str, str] = {
    "pH":                              "ph",
    "EC (Tuzluluk)":                   "ec_ds_m",
    "SAR (Sodyum Adsorpsiyon Oranı)":  "sar",
    "Sodyum (Na)":                     "sodium_mg_l",
    "Klorür (Cl)":                     "chloride_mg_l",
    "Bikarbonat (HCO₃)":               "bicarbonate_mg_l",
    "Bor (B)":                         "boron_mg_l",
}

# Yorumlama durumu sınıfları (soil ile aynı renk sözlüğüne map'lenir)
STATUS_OK = "uygun"
STATUS_CAUTION = "dikkat"
STATUS_SEVERE = "kısıtlı"
STATUS_UNKNOWN = "veri yok"


@dataclass(frozen=True)
class WaterParamStatus:
    """Tek bir su parametresinin ölçüm vs. FAO eşiği sonucu."""

    name: str
    unit: str
    value: float | None       # None ise ölçülmedi
    status: str               # uygun | dikkat | kısıtlı | veri yok
    note: str


@dataclass(frozen=True)
class WaterAnalysis:
    """Sulama suyunun yorumlanmış kalite özeti."""

    results: tuple[WaterParamStatus, ...]
    measured: tuple[WaterParamStatus, ...]    # value is not None olanlar
    unmeasured: tuple[WaterParamStatus, ...]  # value is None olanlar
    ok_count: int
    caution_count: int
    severe_count: int

    @property
    def overall(self) -> str:
        """Genel uygunluk: ölçülenlerin en kötüsü."""
        if self.severe_count > 0:
            return STATUS_SEVERE
        if self.caution_count > 0:
            return STATUS_CAUTION
        if self.ok_count > 0:
            return STATUS_OK
        return STATUS_UNKNOWN


def _classify(value: float, ref: WaterReference) -> str:
    if ref.severe_min is not None and value > ref.severe_min:
        return STATUS_SEVERE
    if value > ref.caution_low:
        return STATUS_CAUTION
    return STATUS_OK


def interpret_water(report: WaterReport) -> WaterAnalysis:
    """WaterReport'u WATER_REFERENCE ile karşılaştır, WaterAnalysis döndür."""
    results: list[WaterParamStatus] = []
    for ref in WATER_REFERENCE:
        field = _REPORT_FIELD_MAP.get(ref.name)
        if field is None:
            continue
        value = getattr(report, field, None)
        if value is None:
            results.append(WaterParamStatus(
                name=ref.name, unit=ref.unit, value=None,
                status=STATUS_UNKNOWN, note=ref.note,
            ))
            continue
        results.append(WaterParamStatus(
            name=ref.name, unit=ref.unit, value=value,
            status=_classify(value, ref), note=ref.note,
        ))

    measured = tuple(r for r in results if r.value is not None)
    unmeasured = tuple(r for r in results if r.value is None)

    return WaterAnalysis(
        results=tuple(results),
        measured=measured,
        unmeasured=unmeasured,
        ok_count=sum(1 for r in measured if r.status == STATUS_OK),
        caution_count=sum(1 for r in measured if r.status == STATUS_CAUTION),
        severe_count=sum(1 for r in measured if r.status == STATUS_SEVERE),
    )
