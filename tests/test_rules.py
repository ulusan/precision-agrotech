"""Kural tabanli karar motoru testleri."""

from __future__ import annotations

from tarla_ai.rules import evaluate_ndre, evaluate_soil_ph
from tarla_ai.rules.engine import Severity


class TestNdreRule:
    def test_low_ndre_triggers_action(self) -> None:
        rec = evaluate_ndre(0.15)
        assert rec.severity is Severity.ACTION
        assert rec.topic == "azot"
        assert "VRA" in rec.message

    def test_sufficient_ndre_ok(self) -> None:
        rec = evaluate_ndre(0.45)
        assert rec.severity is Severity.OK

    def test_boundary_exactly_threshold_is_ok(self) -> None:
        # esige esit -> eksik DEGIL (strict <)
        rec = evaluate_ndre(0.2)
        assert rec.severity is Severity.OK


class TestSoilPhRule:
    def test_low_ph_warning(self) -> None:
        rec = evaluate_soil_ph(5.2)
        assert rec.severity is Severity.WARNING
        assert "asidik" in rec.message.lower() or "kire" in rec.message.lower()

    def test_high_ph_warning(self) -> None:
        rec = evaluate_soil_ph(8.1)
        assert rec.severity is Severity.WARNING

    def test_healthy_ph_ok(self) -> None:
        rec = evaluate_soil_ph(6.8)
        assert rec.severity is Severity.OK

    def test_recommendation_is_immutable(self) -> None:
        import dataclasses

        import pytest

        rec = evaluate_soil_ph(6.8)
        with pytest.raises(dataclasses.FrozenInstanceError):
            rec.value = 99.9  # type: ignore[misc]
