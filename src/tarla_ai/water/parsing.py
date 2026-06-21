"""Sulama suyu analiz PDF'inden parametre değerlerini çıkarır.

Türk laboratuvar formatlarını (Ankara Üniv. Ziraat Fak. dahil) destekler.
Regex tabanlı çıkarım; tanımlanamayan değerler None döner.

Mevcut kuyu raporu yalnızca pH + EC içerir; ancak detaylı rapor geldiğinde
(SAR, Na, Cl, HCO₃, B...) aynı parser onları da okuyabilsin diye alanlar
şimdiden tanımlıdır. Okunamayan alan None kalır — uydurulmaz.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import fitz  # pymupdf


@dataclass(frozen=True)
class WaterReport:
    """Sulama suyu analiz sonuçları. Tanımlanamayan parametreler None.

    EC dS/m; iyonlar mg/L (aksi belirtilmedikçe). SAR birimsiz.
    """

    ph: float | None = None
    ec_ds_m: float | None = None
    sar: float | None = None              # sodyum adsorpsiyon oranı
    sodium_mg_l: float | None = None      # Na⁺
    chloride_mg_l: float | None = None    # Cl⁻
    bicarbonate_mg_l: float | None = None # HCO₃⁻
    carbonate_mg_l: float | None = None   # CO₃²⁻
    boron_mg_l: float | None = None       # B
    calcium_mg_l: float | None = None     # Ca²⁺
    magnesium_mg_l: float | None = None   # Mg²⁺
    sulfate_mg_l: float | None = None     # SO₄²⁻
    nitrate_mg_l: float | None = None     # NO₃⁻
    raw_text: str = field(default="", repr=False)


# ── Regex desenleri ────────────────────────────────────────────────────────
# Sayı grubu: ondalık virgül veya nokta.
_N = r"(\d+[.,]\d+|\d+)"

_PATTERNS: list[tuple[str, str]] = [
    # pH
    ("ph",               rf"pH\s*[:\-]?\s*{_N}"),
    ("ph",               rf"pH\s+değeri\s*[:\-]?\s*{_N}"),

    # EC / Elektriksel İletkenlik
    # "elektriksel iletkenliği 2,90 dS/m" → ek (-i/-ği) ve araya giren kelimeleri
    # tolere et; sayıdan hemen sonra dS/m gelmesi EC olduğunu doğrular.
    ("ec_ds_m",          rf"[Ee]lektrik(?:sel)?\s+[İi]letkenli\w*\b[^0-9]*?{_N}\s*dS/m"),
    ("ec_ds_m",          rf"[Ee]lektrik(?:sel)?\s+[İi]letkenli\w*\s*[:\-]?\s*{_N}"),
    ("ec_ds_m",          rf"EC\b\s*[:\-]?\s*{_N}"),
    ("ec_ds_m",          rf"{_N}\s*dS/m"),

    # SAR
    ("sar",              rf"SAR\s*[:\-]?\s*{_N}"),
    ("sar",              rf"[Ss]odyum\s+[Aa]dsorpsiyon\s+[Oo]ranı\s*[:\-]?\s*{_N}"),

    # Sodyum (Na)
    ("sodium_mg_l",      rf"[Ss]odyum\s*(?:\(Na\))?\s*[:\-]?\s*{_N}"),
    ("sodium_mg_l",      rf"\bNa\b\s*[:\-]?\s*{_N}"),

    # Klorür (Cl)
    ("chloride_mg_l",    rf"[Kk]lor(?:ür|id)\s*(?:\(Cl\))?\s*[:\-]?\s*{_N}"),
    ("chloride_mg_l",    rf"\bCl\b\s*[:\-]?\s*{_N}"),

    # Bikarbonat (HCO3)
    ("bicarbonate_mg_l", rf"[Bb]ikarbonat\s*(?:\(HCO₃\)|\(HCO3\))?\s*[:\-]?\s*{_N}"),
    ("bicarbonate_mg_l", rf"HCO[₃3]\s*[:\-]?\s*{_N}"),

    # Karbonat (CO3)
    ("carbonate_mg_l",   rf"[Kk]arbonat\s*(?:\(CO₃\)|\(CO3\))?\s*[:\-]?\s*{_N}"),
    ("carbonate_mg_l",   rf"CO[₃3]\s*[:\-]?\s*{_N}"),

    # Bor (B)
    ("boron_mg_l",       rf"[Bb]or\s*(?:\(B\))?\s*[:\-]?\s*{_N}"),
    ("boron_mg_l",       rf"\bB\b\s*[:\-]?\s*{_N}"),

    # Kalsiyum / Magnezyum / Sülfat / Nitrat
    ("calcium_mg_l",     rf"[Kk]alsiyum\s*(?:\(Ca\))?\s*[:\-]?\s*{_N}"),
    ("calcium_mg_l",     rf"\bCa\b\s*[:\-]?\s*{_N}"),
    ("magnesium_mg_l",   rf"[Mm]agnezyum\s*(?:\(Mg\))?\s*[:\-]?\s*{_N}"),
    ("magnesium_mg_l",   rf"\bMg\b\s*[:\-]?\s*{_N}"),
    ("sulfate_mg_l",     rf"[Ss][üu]lfat\s*(?:\(SO₄\)|\(SO4\))?\s*[:\-]?\s*{_N}"),
    ("sulfate_mg_l",     rf"SO[₄4]\s*[:\-]?\s*{_N}"),
    ("nitrate_mg_l",     rf"[Nn]itrat\s*(?:\(NO₃\)|\(NO3\))?\s*[:\-]?\s*{_N}"),
    ("nitrate_mg_l",     rf"NO[₃3]\s*[:\-]?\s*{_N}"),
]


def _to_float(s: str) -> float:
    return float(s.replace(",", "."))


def _extract_fields(text: str) -> dict:
    """PDF metninden tüm alanları çıkar, dict olarak döndür."""
    fields: dict = {}
    for field_name, pattern in _PATTERNS:
        if field_name in fields:
            continue
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            try:
                fields[field_name] = _to_float(m.group(1))
            except ValueError:
                pass
    return fields


def parse_water_pdf(path: Path | str) -> WaterReport:
    """PDF sulama suyu analiz raporunu oku ve WaterReport döndür."""
    doc = fitz.open(str(path))
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return WaterReport(raw_text=text, **_extract_fields(text))


def parse_water_pdf_bytes(data: bytes) -> WaterReport:
    """Streamlit UploadedFile.read() gibi bytes verisinden parse et."""
    doc = fitz.open(stream=data, filetype="pdf")
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return WaterReport(raw_text=text, **_extract_fields(text))
