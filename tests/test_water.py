"""Sulama suyu domain testleri — parse, doğrulama, yorumlama, baseline.

İlke testi: ölçülmeyen parametre asla "güvenli" sayılmaz; "veri yok" döner.
"""

from __future__ import annotations

from tarla_ai.water.analysis import (
    STATUS_CAUTION,
    STATUS_OK,
    STATUS_SEVERE,
    STATUS_UNKNOWN,
    interpret_water,
)
from tarla_ai.water.parsing import WaterReport, parse_water_pdf_bytes
from tarla_ai.water.reference import WELL_WATER_BASELINE, WELL_WATER_REPORT_META
from tarla_ai.water.validation import FULL_ASSESSMENT_FIELDS, validate_water


def _build_pdf_bytes(text: str) -> bytes:
    """Verilen metni içeren tek sayfalık PDF bytes üretir."""
    import fitz

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    data = doc.tobytes()
    doc.close()
    return data


class TestWellWaterBaseline:
    def test_baseline_matches_report(self) -> None:
        assert WELL_WATER_BASELINE.ph == 5.84
        assert WELL_WATER_BASELINE.ec_ds_m == 2.90

    def test_unmeasured_params_are_none_not_zero(self) -> None:
        # Kritik ilke: ölçülmeyen değer None, 0 değil.
        for fname in ("sar", "sodium_mg_l", "chloride_mg_l",
                      "bicarbonate_mg_l", "boron_mg_l"):
            assert getattr(WELL_WATER_BASELINE, fname) is None

    def test_meta_records_provenance(self) -> None:
        assert WELL_WATER_REPORT_META["rapor_no"] == "TAR-2024-0004"
        assert "pH + EC" in WELL_WATER_REPORT_META["kapsam"]


class TestValidateWater:
    def test_baseline_has_minimum_but_not_full(self) -> None:
        v = validate_water(WELL_WATER_BASELINE)
        assert v.has_minimum is True
        assert v.is_full_assessment is False
        assert v.missing_full_count == len(FULL_ASSESSMENT_FIELDS)

    def test_missing_ph_blocks_minimum(self) -> None:
        report = WaterReport(ec_ds_m=2.9)
        v = validate_water(report)
        assert v.has_minimum is False
        assert "pH" in v.missing_minimum

    def test_full_report_is_full_assessment(self) -> None:
        report = WaterReport(
            ph=7.0, ec_ds_m=0.6, sar=2.0, sodium_mg_l=50.0,
            chloride_mg_l=100.0, bicarbonate_mg_l=80.0, boron_mg_l=0.5,
        )
        v = validate_water(report)
        assert v.is_full_assessment is True
        assert v.missing_full == ()


class TestInterpretWater:
    def test_baseline_ec_is_caution_or_severe(self) -> None:
        a = interpret_water(WELL_WATER_BASELINE)
        ec = next(r for r in a.results if r.name.startswith("EC"))
        assert ec.value == 2.90
        # 2.90 caution bandında (0.7–3.0), severe sınırı 3.0
        assert ec.status == STATUS_CAUTION

    def test_unmeasured_params_marked_unknown(self) -> None:
        a = interpret_water(WELL_WATER_BASELINE)
        sar = next(r for r in a.results if r.name.startswith("SAR"))
        assert sar.value is None
        assert sar.status == STATUS_UNKNOWN
        assert len(a.unmeasured) >= 4

    def test_measured_and_unmeasured_partition(self) -> None:
        a = interpret_water(WELL_WATER_BASELINE)
        assert len(a.measured) == 2  # pH + EC
        assert all(r.value is not None for r in a.measured)
        assert all(r.value is None for r in a.unmeasured)

    def test_overall_reflects_worst_measured(self) -> None:
        a = interpret_water(WELL_WATER_BASELINE)
        # pH dikkat (5.84 < 6.5 alt, ama biz üst-bant sınıflıyoruz),
        # EC dikkat → genel dikkat (severe yok)
        assert a.overall in (STATUS_CAUTION, STATUS_SEVERE)

    def test_clean_water_is_ok(self) -> None:
        report = WaterReport(ph=7.0, ec_ds_m=0.5)
        a = interpret_water(report)
        ec = next(r for r in a.results if r.name.startswith("EC"))
        assert ec.status == STATUS_OK

    def test_severe_ec(self) -> None:
        report = WaterReport(ph=7.0, ec_ds_m=4.5)
        a = interpret_water(report)
        ec = next(r for r in a.results if r.name.startswith("EC"))
        assert ec.status == STATUS_SEVERE
        assert a.severe_count >= 1


class TestParseWaterPdf:
    def test_parses_ph_and_ec(self) -> None:
        # Not: fitz.insert_text Türkçe 'İ'yi bozabildiğinden EC: formu kullanılır;
        # gerçek lab PDF'inde metin katmanı 'İletkenlik' olarak doğru gelir.
        pdf = _build_pdf_bytes("pH: 5,84\nEC: 2,90 dS/m")
        report = parse_water_pdf_bytes(pdf)
        assert report.ph == 5.84
        assert report.ec_ds_m == 2.90

    def test_missing_fields_stay_none(self) -> None:
        pdf = _build_pdf_bytes("pH: 6,5")
        report = parse_water_pdf_bytes(pdf)
        assert report.ph == 6.5
        assert report.sar is None
        assert report.boron_mg_l is None

    def test_parses_extended_params_when_present(self) -> None:
        pdf = _build_pdf_bytes(
            "pH: 7,2\nEC: 1,1\nSAR: 4,5\nKlorür: 120\nBor: 0,8"
        )
        report = parse_water_pdf_bytes(pdf)
        assert report.sar == 4.5
        assert report.chloride_mg_l == 120
        assert report.boron_mg_l == 0.8
