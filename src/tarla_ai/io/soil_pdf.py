"""Toprak analiz PDF'inden parametre değerlerini çıkarır.

TSGM/TAGEM ve diğer Türk laboratuvar formatlarını destekler.
Regex tabanlı çıkarım; tanımlanamayan değerler None döner.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import fitz  # pymupdf


@dataclass
class SoilReport:
    """Toprak analizi sonuçları. Tanımlanamayan parametreler None."""

    ph: float | None = None
    organic_matter_pct: float | None = None
    total_n_pct: float | None = None
    phosphorus_kg_ha: float | None = None
    potassium_kg_ha: float | None = None
    ec_ds_m: float | None = None          # tuzluluk
    calcium_meq: float | None = None
    magnesium_meq: float | None = None
    zinc_mg_kg: float | None = None
    iron_mg_kg: float | None = None
    copper_mg_kg: float | None = None
    manganese_mg_kg: float | None = None
    boron_mg_kg: float | None = None
    cec_meq: float | None = None          # katyon değişim kapasitesi
    sand_pct: float | None = None
    silt_pct: float | None = None
    clay_pct: float | None = None
    raw_text: str = field(default="", repr=False)


# ── Regex desenleri ────────────────────────────────────────────────────────
# Her desen: (alan_adı, regex_pattern)
# Sayı grubu: (\d+[.,]\d+|\d+)  →  ondalık virgül veya nokta
_N = r"(\d+[.,]\d+|\d+)"

_PATTERNS: list[tuple[str, str]] = [
    # pH
    ("ph",              rf"pH\s*[:\-]?\s*{_N}"),
    ("ph",              rf"Toprak\s+pH\s*[:\-]?\s*{_N}"),
    ("ph",              rf"pH\s+değeri\s*[:\-]?\s*{_N}"),

    # Organik madde
    ("organic_matter_pct", rf"[Oo]rganik\s+[Mm]adde\s*[:\-%]?\s*{_N}"),
    ("organic_matter_pct", rf"O\.M\.\s*[:\-%]?\s*{_N}"),
    ("organic_matter_pct", rf"OM\s*[:\-%]?\s*{_N}"),

    # Toplam azot
    ("total_n_pct",     rf"[Tt]oplam\s+[Aa]zot\s*[:\-%]?\s*{_N}"),
    ("total_n_pct",     rf"Total\s+N\s*[:\-%]?\s*{_N}"),
    ("total_n_pct",     rf"N\s+\(%\)\s*[:\-]?\s*{_N}"),

    # Fosfor
    ("phosphorus_kg_ha", rf"[Ff]osfor\s*(?:\(P₂O₅\)|P2O5|P)?\s*[:\-]?\s*{_N}"),
    ("phosphorus_kg_ha", rf"P(?:₂O₅|2O5)\s*[:\-]?\s*{_N}"),
    ("phosphorus_kg_ha", rf"Alınabilir\s+P\s*[:\-]?\s*{_N}"),

    # Potasyum
    ("potassium_kg_ha", rf"[Pp]otasyum\s*(?:\(K₂O\)|K2O|K)?\s*[:\-]?\s*{_N}"),
    ("potassium_kg_ha", rf"K(?:₂O|2O)\s*[:\-]?\s*{_N}"),
    ("potassium_kg_ha", rf"Alınabilir\s+K\s*[:\-]?\s*{_N}"),

    # EC / Tuzluluk
    ("ec_ds_m",         rf"EC\s*[:\-]?\s*{_N}"),
    ("ec_ds_m",         rf"[Ee]lektrik(?:sel)?\s+[İi]letkenlik\s*[:\-]?\s*{_N}"),
    ("ec_ds_m",         rf"[Tt]uzluluk\s*[:\-]?\s*{_N}"),

    # Kalsiyum
    ("calcium_meq",     rf"[Kk]alsiyum\s*(?:\(Ca\))?\s*[:\-]?\s*{_N}"),
    ("calcium_meq",     rf"Ca\s*[:\-]?\s*{_N}"),

    # Magnezyum
    ("magnesium_meq",   rf"[Mm]agnezyum\s*(?:\(Mg\))?\s*[:\-]?\s*{_N}"),
    ("magnesium_meq",   rf"Mg\s*[:\-]?\s*{_N}"),

    # Çinko
    ("zinc_mg_kg",      rf"[Çç]inko\s*(?:\(Zn\))?\s*[:\-]?\s*{_N}"),
    ("zinc_mg_kg",      rf"Zn\s*[:\-]?\s*{_N}"),

    # Demir
    ("iron_mg_kg",      rf"[Dd]emir\s*(?:\(Fe\))?\s*[:\-]?\s*{_N}"),
    ("iron_mg_kg",      rf"Fe\s*[:\-]?\s*{_N}"),

    # Bakır
    ("copper_mg_kg",    rf"[Bb]akır\s*(?:\(Cu\))?\s*[:\-]?\s*{_N}"),
    ("copper_mg_kg",    rf"Cu\s*[:\-]?\s*{_N}"),

    # Mangan
    ("manganese_mg_kg", rf"[Mm]angan\s*(?:\(Mn\))?\s*[:\-]?\s*{_N}"),
    ("manganese_mg_kg", rf"Mn\s*[:\-]?\s*{_N}"),

    # Bor
    ("boron_mg_kg",     rf"[Bb]or\s*(?:\(B\))?\s*[:\-]?\s*{_N}"),
    ("boron_mg_kg",     rf"\bB\b\s*[:\-]?\s*{_N}"),

    # CEC
    ("cec_meq",         rf"CEC\s*[:\-]?\s*{_N}"),
    ("cec_meq",         rf"[Kk]atyon\s+[Dd]eğişim\s+[Kk]apasitesi\s*[:\-]?\s*{_N}"),
    ("cec_meq",         rf"KDK\s*[:\-]?\s*{_N}"),

    # Tekstür
    ("sand_pct",        rf"[Kk]um\s*[:\-%]?\s*{_N}"),
    ("silt_pct",        rf"[Ss]ilt\s*[:\-%]?\s*{_N}"),
    ("clay_pct",        rf"[Kk]il\s*[:\-%]?\s*{_N}"),
]


def _to_float(s: str) -> float:
    return float(s.replace(",", "."))


def parse_soil_pdf(path: Path | str) -> SoilReport:
    """PDF toprak analiz raporunu oku ve SoilReport döndür.

    Args:
        path: PDF dosya yolu.

    Returns:
        SoilReport — tanımlanamayan alanlar None.
    """
    doc = fitz.open(str(path))
    text = "\n".join(page.get_text() for page in doc)
    doc.close()

    report = SoilReport(raw_text=text)

    for field_name, pattern in _PATTERNS:
        if getattr(report, field_name) is not None:
            continue  # zaten bulundu
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            try:
                setattr(report, field_name, _to_float(m.group(1)))
            except ValueError:
                pass

    return report


def parse_soil_pdf_bytes(data: bytes) -> SoilReport:
    """Streamlit UploadedFile.read() gibi bytes verisinden parse et."""
    doc = fitz.open(stream=data, filetype="pdf")
    text = "\n".join(page.get_text() for page in doc)
    doc.close()

    report = SoilReport(raw_text=text)

    for field_name, pattern in _PATTERNS:
        if getattr(report, field_name) is not None:
            continue
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            try:
                setattr(report, field_name, _to_float(m.group(1)))
            except ValueError:
                pass

    return report
