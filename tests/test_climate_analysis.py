"""İklim analizi saf fonksiyon testleri — sentetik veri, ağ yok."""

from __future__ import annotations

from datetime import date

from tarla_ai.climate.analysis import (
    cumulative_gdd,
    cumulative_rain,
    daily_mean_temp,
    monthly_breakdown,
    season_summary,
)
from tarla_ai.climate.models import DailyWeather


def mk(
    d: date, tmax: float, tmin: float, *,
    rain: float = 0.0, rain_only: float | None = None,
    snow: float = 0.0, et0: float = 0.0,
    hum: float | None = None, wind: float | None = None,
) -> DailyWeather:
    return DailyWeather(
        date=d, temp_max=tmax, temp_min=tmin, temp_mean=(tmax + tmin) / 2,
        precipitation_mm=rain, rain_mm=rain if rain_only is None else rain_only,
        snowfall_cm=snow, precipitation_hours=None, humidity_pct=hum,
        wind_max_kmh=wind, wind_gust_kmh=None, et0_mm=et0,
    )


# Geçmiş tarihler (gerçek bugüne göre hep "ölçüm") → deterministik.
_D = [date(2025, 11, 1), date(2025, 11, 2), date(2025, 12, 1)]


class TestCumulative:
    def test_cumulative_rain_accumulates(self) -> None:
        days = [mk(_D[0], 8, 2, rain=10), mk(_D[1], 9, 1, rain=0),
                mk(_D[2], 7, 0, rain=5)]
        cum = cumulative_rain(days)
        assert [v for _, v, _ in cum] == [10.0, 10.0, 15.0]
        assert all(not fc for _, _, fc in cum)  # hepsi geçmiş

    def test_cumulative_gdd_base_zero_clips_negative(self) -> None:
        # ort. sıcaklık: 10, 20, -5 → katkı: 10, 20, 0 → kümülatif 10, 30, 30
        days = [mk(_D[0], 15, 5), mk(_D[1], 25, 15), mk(_D[2], -2, -8)]
        cum = cumulative_gdd(days)
        assert [v for _, v, _ in cum] == [10.0, 30.0, 30.0]


class TestMonthly:
    def test_monthly_breakdown_splits_by_month(self) -> None:
        days = [mk(_D[0], 8, 2, rain=10), mk(_D[1], 9, 1, rain=4),
                mk(_D[2], 7, 0, rain=6, snow=3)]
        months = monthly_breakdown(days)
        assert len(months) == 2
        kasim = months[0]
        assert kasim.month == 11
        assert kasim.rain_mm == 14.0
        aralik = months[1]
        assert aralik.month == 12
        assert aralik.snow_cm == 3.0


class TestSeasonSummary:
    def test_counts_frost_and_heat(self) -> None:
        days = [
            mk(_D[0], 32, 10, rain=2),   # heat (max>30)
            mk(_D[1], 12, -2, rain=0),   # frost (min<0)
            mk(_D[2], 5, 1, rain=20),
        ]
        s = season_summary(days)
        assert s.heat_days == 1
        assert s.frost_days == 1
        assert s.total_rain_mm == 22.0
        assert s.rainy_days == 2  # 2mm ve 20mm (>=1mm)
        assert s.min_temp_c == -2.0
        assert s.max_temp_c == 32.0

    def test_empty_is_safe(self) -> None:
        s = season_summary([])
        assert s.day_count == 0
        assert s.total_rain_mm == 0


class TestMeanTemp:
    def test_prefers_api_mean(self) -> None:
        d = mk(date(2025, 11, 1), 20, 10)  # mean=15
        assert daily_mean_temp(d) == 15.0
