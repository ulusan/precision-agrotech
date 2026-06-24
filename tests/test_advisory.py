"""Öneri motoru testleri — zaman penceresi mantığı + çıktı yapısı."""

from __future__ import annotations

from datetime import date

from tarla_ai.advisory.engine import _urgency, all_advice
from tarla_ai.advisory.models import Urgency
from tests.test_climate_analysis import mk


class TestUrgencyWindow:
    start = date(2026, 3, 1)
    end = date(2026, 4, 15)

    def test_within_window_is_now(self) -> None:
        assert _urgency(self.start, self.end, date(2026, 3, 20)) is Urgency.NOW

    def test_just_before_is_soon(self) -> None:
        assert _urgency(self.start, self.end, date(2026, 2, 20)) is Urgency.SOON

    def test_far_before_is_info(self) -> None:
        assert _urgency(self.start, self.end, date(2025, 12, 1)) is Urgency.INFO

    def test_after_is_done(self) -> None:
        assert _urgency(self.start, self.end, date(2026, 6, 1)) is Urgency.DONE


class TestAllAdvice:
    def _days(self) -> list:
        # Birkaç sentetik gün — motor çökmeden 5 öneri üretmeli.
        return [
            mk(date(2025, 10, 10), 20, 8, rain=5, et0=3),
            mk(date(2025, 11, 15), 10, 2, rain=12, et0=1),
            mk(date(2026, 3, 10), 14, 4, rain=8, et0=3, wind=12),
            mk(date(2026, 5, 1), 22, 9, rain=3, et0=4, hum=70),
        ]

    def test_starts_with_preparation(self) -> None:
        adv = all_advice(self._days())
        keys = [a.key for a in adv]
        assert keys == ["hazirlik", "ekim", "gubre", "ilac", "sulama", "hasat"]
        # Serüven hazırlıkla başlar ve hazırlık "şu an" yapılır.
        assert adv[0].urgency is Urgency.NOW

    def test_each_has_headline_and_four_sources(self) -> None:
        for a in all_advice(self._days()):
            assert a.headline
            assert a.urgency_label
            # Her aşamada dört kaynak da temsil edilir (su/toprak/drone/hava).
            srcs = {s.source for s in a.source_actions}
            assert srcs == {"su", "toprak", "drone", "hava"}

    def test_no_soil_marks_toprak_unavailable(self) -> None:
        adv = {a.key: a for a in all_advice(self._days(), has_soil=False)}
        soil_sa = next(s for s in adv["gubre"].source_actions if s.source == "toprak")
        assert soil_sa.available is False
        assert soil_sa.missing_note  # yüklenince notu var, uydurma değer yok

    def test_soil_uploaded_marks_available(self) -> None:
        from tarla_ai.soil.parsing import SoilReport
        soil = SoilReport(ph=7.8, total_n_pct=0.06, phosphorus_kg_ha=4.0,
                          zinc_mg_kg=0.3, organic_matter_pct=1.5)
        adv = {a.key: a for a in all_advice(self._days(), has_soil=True, soil=soil)}
        soil_sa = next(s for s in adv["gubre"].source_actions if s.source == "toprak")
        assert soil_sa.available is True
        # Ölçülen gerçek değer eyleme yansımış olmalı (azot %0.06 düşük).
        assert soil_sa.toprak_action is not None and "azot" in soil_sa.toprak_action.lower()

    def test_water_uses_real_well_ec_not_hardcoded(self) -> None:
        # Su kaynağı değeri gerçek kuyu kaydından (EC 2.90) gelmeli.
        adv = {a.key: a for a in all_advice(self._days())}
        su = next(s for s in adv["sulama"].source_actions if s.source == "su")
        assert su.value_used is not None and "2.90" in su.value_used


class TestNextSowing:
    def test_before_october_is_this_year(self) -> None:
        from tarla_ai.advisory.engine import next_sowing_date
        assert next_sowing_date(date(2026, 6, 24)) == date(2026, 10, 1)

    def test_after_october_is_next_year(self) -> None:
        from tarla_ai.advisory.engine import next_sowing_date
        assert next_sowing_date(date(2026, 11, 5)) == date(2027, 10, 1)
