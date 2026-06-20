"""Toprak PDF parse mantığı testleri — gerçekçi lab metin formatları.

PDF render'ı değil, metin çıkarım regex'leri test edilir (fitz'siz, hızlı).
"""

from __future__ import annotations

from tarla_ai.soil.parsing import SoilReport, _extract_fields


def _parse(text: str) -> SoilReport:
    return SoilReport(raw_text=text, **_extract_fields(text))


class TestPhosphorusPotassium:
    def test_parenthesized_oxide_form(self) -> None:
        # "Fosfor (P2O5): 5,2" — düz ASCII parantezli oksit formu
        report = _parse("Fosfor (P2O5): 5,2\nPotasyum (K2O): 38")
        assert report.phosphorus_kg_ha == 5.2
        assert report.potassium_kg_ha == 38.0

    def test_unicode_subscript_oxide_form(self) -> None:
        # "P₂O₅ 9.1" — Unicode alt-simge
        report = _parse("P₂O₅ 9.1\nK₂O 40")
        assert report.phosphorus_kg_ha == 9.1
        assert report.potassium_kg_ha == 40.0


class TestLime:
    def test_caco3_variants(self) -> None:
        assert _parse("Kireç (CaCO3): 22,5 %").caco3_pct == 22.5
        assert _parse("CaCO₃ 15").caco3_pct == 15.0


class TestCommaDecimal:
    def test_turkish_comma_decimal(self) -> None:
        report = _parse("pH: 7,8\nÇinko (Zn): 0,38")
        assert report.ph == 7.8
        assert report.zinc_mg_kg == 0.38


class TestMissingFieldsAreNone:
    def test_unmatched_fields_stay_none(self) -> None:
        report = _parse("pH: 7.2")
        assert report.ph == 7.2
        assert report.phosphorus_kg_ha is None
        assert report.boron_mg_kg is None
