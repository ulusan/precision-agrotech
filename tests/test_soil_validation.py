"""validate_soil testleri — zorunlu alan kontrolü, uydurma yok."""

from __future__ import annotations

from tarla_ai.soil.parsing import SoilReport
from tarla_ai.soil.validation import REQUIRED_FIELDS, validate_soil


def _full_report() -> SoilReport:
    """Tüm zorunlu alanları dolu, geçerli bir rapor."""
    return SoilReport(
        ph=7.4,
        organic_matter_pct=1.8,
        total_n_pct=0.09,
        phosphorus_kg_ha=6.5,
        potassium_kg_ha=35.0,
        caco3_pct=18.0,
        zinc_mg_kg=0.45,
    )


class TestValidateSoil:
    def test_full_report_is_decision_ready(self) -> None:
        result = validate_soil(_full_report())
        assert result.is_decision_ready is True
        assert result.missing_required == ()
        assert result.missing_count == 0
        assert len(result.present_required) == len(REQUIRED_FIELDS)

    def test_empty_report_lists_all_missing(self) -> None:
        result = validate_soil(SoilReport())
        assert result.is_decision_ready is False
        assert result.missing_count == len(REQUIRED_FIELDS)
        assert result.present_required == ()

    def test_single_missing_field_blocks_readiness(self) -> None:
        report = _full_report()
        # Çinkoyu çıkar (frozen dataclass → yeni kopya, mutasyon yok)
        report = SoilReport(**{**report.__dict__, "zinc_mg_kg": None})
        result = validate_soil(report)
        assert result.is_decision_ready is False
        assert "Çinko (Zn, DTPA)" in result.missing_required
        assert result.missing_count == 1

    def test_zero_value_counts_as_present(self) -> None:
        # 0.0 geçerli bir ölçümdür (None değil) → mevcut sayılmalı
        report = SoilReport(**{**_full_report().__dict__, "phosphorus_kg_ha": 0.0})
        result = validate_soil(report)
        assert result.is_decision_ready is True
