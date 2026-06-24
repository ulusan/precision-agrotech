"""Büyüme dönemi bazında iklim agregasyonu ve stres tespiti."""

from __future__ import annotations

from datetime import date, timedelta

from tarla_ai.climate.models import (
    DailyWeather,
    MonthlyTotals,
    SeasonSummary,
    StageWeatherSummary,
)
from tarla_ai.climate.reference import (
    FROST_THRESHOLD_C,
    GDD_BASE_C,
    HEAT_THRESHOLD_C,
    RAINY_DAY_MM,
    STAGE_WINDOWS,
)


def _avg(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def daily_mean_temp(d: DailyWeather) -> float | None:
    """Gün ortalama sıcaklığı: API mean varsa onu, yoksa (max+min)/2."""
    if d.temp_mean is not None:
        return d.temp_mean
    if d.temp_max is not None and d.temp_min is not None:
        return (d.temp_max + d.temp_min) / 2
    return None


def cumulative_rain(days: list[DailyWeather]) -> list[tuple[date, float, bool]]:
    """(tarih, kümülatif yağış mm, tahmin_mi) — sezon başından artarak."""
    out, total = [], 0.0
    today = date.today()
    for d in sorted(days, key=lambda x: x.date):
        total += d.precipitation_mm or 0.0
        out.append((d.date, round(total, 1), d.date > today))
    return out


def cumulative_gdd(
    days: list[DailyWeather], base: float = GDD_BASE_C
) -> list[tuple[date, float, bool]]:
    """(tarih, kümülatif GDD, tahmin_mi) — büyüme gün dereceleri, taban=base."""
    out, total = [], 0.0
    today = date.today()
    for d in sorted(days, key=lambda x: x.date):
        tm = daily_mean_temp(d)
        if tm is not None:
            total += max(0.0, tm - base)
        out.append((d.date, round(total, 0), d.date > today))
    return out


def monthly_breakdown(days: list[DailyWeather]) -> list[MonthlyTotals]:
    """Ölçülmüş günlerin ay ay toplamları (tahmin günleri hariç)."""
    today = date.today()
    past = [d for d in days if d.date <= today]
    keys = sorted({(d.date.year, d.date.month) for d in past})
    out: list[MonthlyTotals] = []
    for y, m in keys:
        md = [d for d in past if d.date.year == y and d.date.month == m]
        rain = sum(d.rain_mm or 0.0 for d in md)
        snow_w = sum(max(0.0, (d.precipitation_mm or 0.0) - (d.rain_mm or 0.0)) for d in md)
        tmax = [d.temp_max for d in md if d.temp_max is not None]
        tmin = [d.temp_min for d in md if d.temp_min is not None]
        out.append(MonthlyTotals(
            year=y, month=m,
            rain_mm=round(rain, 1),
            snow_water_mm=round(snow_w, 1),
            snow_cm=round(sum(d.snowfall_cm or 0.0 for d in md), 1),
            tmax_avg=round(_avg(tmax), 1),
            tmin_avg=round(_avg(tmin), 1),
            et0_mm=round(sum(d.et0_mm or 0.0 for d in md), 1),
        ))
    return out


def season_summary(days: list[DailyWeather]) -> SeasonSummary:
    """Sezon başından bugüne ölçülmüş günlere dayalı buğday iklim özeti."""
    today = date.today()
    past = [d for d in days if d.date <= today]
    if not past:
        return SeasonSummary(today, today, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    precip = [d.precipitation_mm or 0.0 for d in past]
    tmins = [d.temp_min for d in past if d.temp_min is not None]
    tmaxs = [d.temp_max for d in past if d.temp_max is not None]
    hums = [d.humidity_pct for d in past if d.humidity_pct is not None]
    winds = [d.wind_max_kmh for d in past if d.wind_max_kmh is not None]

    total_rain = sum(precip)
    total_et0 = sum(d.et0_mm or 0.0 for d in past)
    gdd = cumulative_gdd(past)[-1][1] if past else 0.0

    vern = 0
    for d in past:
        if d.date.month in (11, 12, 1, 2):
            tm = daily_mean_temp(d)
            if tm is not None and 0.0 <= tm <= 10.0:
                vern += 1

    return SeasonSummary(
        start=past[0].date, end=past[-1].date, day_count=len(past),
        total_rain_mm=round(total_rain, 1),
        rainy_days=sum(1 for v in precip if v >= RAINY_DAY_MM),
        total_snow_cm=round(sum(d.snowfall_cm or 0.0 for d in past), 1),
        total_et0_mm=round(total_et0, 1),
        water_deficit_mm=round(total_et0 - total_rain, 1),
        total_gdd=round(gdd, 0),
        frost_days=sum(1 for t in tmins if t < FROST_THRESHOLD_C),
        heat_days=sum(1 for t in tmaxs if t > HEAT_THRESHOLD_C),
        min_temp_c=round(min(tmins), 1) if tmins else 0.0,
        max_temp_c=round(max(tmaxs), 1) if tmaxs else 0.0,
        vernalization_days=vern,
        avg_humidity_pct=round(_avg(hums)),
        max_wind_kmh=round(max(winds), 1) if winds else 0.0,
    )


def analyze_by_stage(days: list[DailyWeather]) -> list[StageWeatherSummary]:
    """Her büyüme dönemi için iklim özeti hesapla.

    Dönemde henüz veri yoksa (gelecek dönem) has_data=False döner.
    None ölçümler toplama katılmaz.
    """
    lookup: dict[date, DailyWeather] = {d.date: d for d in days}
    summaries: list[StageWeatherSummary] = []

    for name, bbch, start, end in STAGE_WINDOWS:
        stage_days: list[DailyWeather] = []
        cur = start
        while cur <= end:
            if cur in lookup:
                stage_days.append(lookup[cur])
            cur += timedelta(days=1)

        if not stage_days:
            summaries.append(StageWeatherSummary(
                stage_name=name, bbch=bbch, start_date=start, end_date=end,
                day_count=0, total_rain_mm=0.0, total_rain_only_mm=0.0,
                total_snow_cm=0.0, rainy_days=0, avg_temp_c=0.0,
                avg_humidity_pct=0.0, max_wind_kmh=0.0, total_et0_mm=0.0,
                water_deficit_mm=0.0, frost_days=0, heat_days=0, has_data=False,
            ))
            continue

        precip_vals = [d.precipitation_mm for d in stage_days if d.precipitation_mm is not None]
        rain_vals   = [d.rain_mm for d in stage_days if d.rain_mm is not None]
        snow_vals   = [d.snowfall_cm for d in stage_days if d.snowfall_cm is not None]
        tmax_vals   = [d.temp_max for d in stage_days if d.temp_max is not None]
        tmin_vals   = [d.temp_min for d in stage_days if d.temp_min is not None]
        tmean_vals  = [d.temp_mean for d in stage_days if d.temp_mean is not None]
        hum_vals    = [d.humidity_pct for d in stage_days if d.humidity_pct is not None]
        wind_vals   = [d.wind_max_kmh for d in stage_days if d.wind_max_kmh is not None]
        et0_vals    = [d.et0_mm for d in stage_days if d.et0_mm is not None]

        total_rain = sum(precip_vals)
        total_et0  = sum(et0_vals)
        # Ortalama sıcaklık: API mean varsa onu, yoksa (max+min)/2
        avg_temp = _avg(tmean_vals) if tmean_vals else (_avg(tmax_vals) + _avg(tmin_vals)) / 2

        summaries.append(StageWeatherSummary(
            stage_name=name, bbch=bbch, start_date=start, end_date=end,
            day_count=len(stage_days),
            total_rain_mm=round(total_rain, 1),
            total_rain_only_mm=round(sum(rain_vals), 1),
            total_snow_cm=round(sum(snow_vals), 1),
            rainy_days=sum(1 for v in precip_vals if v >= RAINY_DAY_MM),
            avg_temp_c=round(avg_temp, 1),
            avg_humidity_pct=round(_avg(hum_vals)),
            max_wind_kmh=round(max(wind_vals), 1) if wind_vals else 0.0,
            total_et0_mm=round(total_et0, 1),
            water_deficit_mm=round(total_et0 - total_rain, 1),
            frost_days=sum(1 for t in tmin_vals if t < FROST_THRESHOLD_C),
            heat_days=sum(1 for t in tmax_vals if t > HEAT_THRESHOLD_C),
            has_data=True,
        ))

    return summaries


def current_stage_name(today: date | None = None) -> str | None:
    """Verilen tarihe (varsayılan: bugün) göre aktif büyüme dönemi adı."""
    if today is None:
        today = date.today()
    for name, _bbch, start, end in STAGE_WINDOWS:
        if start <= today <= end:
            return name
    return None
