"""Toprak raporu doğrulama — karar üretmeye yeterli mi?

docs/veri-gereksinimi.md §1 ve §9 ile birebir aynı kuralları kodda uygular.
Eksik veri = uydurma DEĞİL: hangi zorunlu alanın eksik olduğunu açıkça raporlar.
"""

from __future__ import annotations

from dataclasses import dataclass

from tarla_ai.soil.parsing import SoilReport

# docs/veri-gereksinimi.md §1 "Zorunlu" tablosuyla birebir.
# (SoilReport alan adı, insan-okur etiket)
REQUIRED_FIELDS: tuple[tuple[str, str], ...] = (
    ("ph",               "pH"),
    ("organic_matter_pct", "Organik Madde"),
    ("total_n_pct",      "Toplam Azot (N)"),
    ("phosphorus_kg_ha", "Alınabilir Fosfor (P₂O₅)"),
    ("potassium_kg_ha",  "Alınabilir Potasyum (K₂O)"),
    ("caco3_pct",        "Kireç (CaCO₃)"),
    ("zinc_mg_kg",       "Çinko (Zn, DTPA)"),
)


@dataclass(frozen=True)
class SoilValidation:
    """Toprak raporunun karar-yeterlilik sonucu."""

    is_decision_ready: bool
    missing_required: tuple[str, ...]   # eksik zorunlu alanların etiketleri
    present_required: tuple[str, ...]   # mevcut zorunlu alanların etiketleri

    @property
    def missing_count(self) -> int:
        return len(self.missing_required)


def validate_soil(report: SoilReport) -> SoilValidation:
    """SoilReport'un zorunlu alanlarını kontrol et.

    is_decision_ready, ancak TÜM zorunlu alanlar dolu (None değil) ise True olur.
    Hiçbir alan uydurulmaz; sadece varlık/yokluk raporlanır.
    """
    missing: list[str] = []
    present: list[str] = []
    for field_name, label in REQUIRED_FIELDS:
        value = getattr(report, field_name, None)
        if value is None:
            missing.append(label)
        else:
            present.append(label)

    return SoilValidation(
        is_decision_ready=len(missing) == 0,
        missing_required=tuple(missing),
        present_required=tuple(present),
    )
