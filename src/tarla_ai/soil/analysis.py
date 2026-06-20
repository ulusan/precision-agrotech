"""Toprak analizi yorumlama — SoilReport → SoilAnalysis DTO."""

from __future__ import annotations

from dataclasses import dataclass

from tarla_ai.soil.parsing import SoilReport
from tarla_ai.soil.reference import SOIL_REFERENCE, SoilReference


@dataclass(frozen=True)
class ParamStatus:
    """Tek bir toprak parametresinin ölçüm vs. referans sonucu."""

    name: str
    unit: str
    value: float
    status: str   # "düşük" | "ideal" | "yüksek"
    note: str


@dataclass(frozen=True)
class SoilAnalysis:
    """Toprak analizinin yorumlanmış özeti."""

    results: tuple[ParamStatus, ...]
    low_count: int
    ideal_count: int
    high_count: int


_REPORT_FIELD_MAP: dict[str, str] = {
    "pH":                          "ph",
    "Organik Madde":               "organic_matter_pct",
    "Toplam Azot":                 "total_n_pct",
    "Alınabilir Fosfor (P₂O₅)":   "phosphorus_kg_ha",
    "Alınabilir Potasyum (K₂O)":  "potassium_kg_ha",
    "EC / Tuzluluk":               "ec_ds_m",
    "Kireç (CaCO₃)":              "caco3_pct",
    "Kalsiyum (Ca)":               "calcium_meq",
    "Magnezyum (Mg)":              "magnesium_meq",
    "Çinko (Zn)":                  "zinc_mg_kg",
    "Demir (Fe)":                  "iron_mg_kg",
    "Bakır (Cu)":                  "copper_mg_kg",
    "Mangan (Mn)":                 "manganese_mg_kg",
    "Bor (B)":                     "boron_mg_kg",
    "Katyon Değişim Kap. (CEC)":   "cec_meq",
}


def _classify(value: float, ref: SoilReference) -> str:
    if ref.low_max is not None and value < ref.low_max:
        return "düşük"
    if ref.high_min is not None and value > ref.high_min:
        return "yüksek"
    return "ideal"


def interpret_soil(report: SoilReport) -> SoilAnalysis:
    """SoilReport'u SOIL_REFERENCE ile karşılaştır, SoilAnalysis döndür."""
    results = []
    for ref in SOIL_REFERENCE:
        field = _REPORT_FIELD_MAP.get(ref.name)
        if field is None:
            continue
        value = getattr(report, field, None)
        if value is None:
            continue
        status = _classify(value, ref)
        results.append(ParamStatus(
            name=ref.name,
            unit=ref.unit,
            value=value,
            status=status,
            note=ref.note,
        ))

    low = sum(1 for r in results if r.status == "düşük")
    high = sum(1 for r in results if r.status == "yüksek")
    ideal = sum(1 for r in results if r.status == "ideal")

    return SoilAnalysis(
        results=tuple(results),
        low_count=low,
        ideal_count=ideal,
        high_count=high,
    )
