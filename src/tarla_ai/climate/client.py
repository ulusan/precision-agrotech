"""Open-Meteo API istemcisi — ücretsiz, API key gerektirmez.

Konum bazlı çalışır: çağıran enlem/boylam verir, veri o noktanın grid
hücresinden gelir. İki uç nokta:
  - Arşiv (geçmiş, ERA5):     https://archive-api.open-meteo.com/v1/archive
  - Tahmin (önümüzdeki gün):  https://api.open-meteo.com/v1/forecast

Sağlamlık için:
  - Her iki uç nokta da timeout + tekrar (retry) ile çağrılır.
  - Tahmin uç noktası ek olarak weather_code ve yağış ihtimali verir.
  - Geçmiş + tahmin tarih bazında çakışmadan birleştirilir (geçmiş öncelikli).
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta

from tarla_ai.climate.models import DailyWeather
from tarla_ai.climate.reference import TIMEZONE

_ARCHIVE_BASE = "https://archive-api.open-meteo.com/v1/archive"
_FORECAST_BASE = "https://api.open-meteo.com/v1/forecast"

# Her iki uç noktada da ortak istenen günlük değişkenler.
_COMMON_DAILY = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",
    "rain_sum",
    "snowfall_sum",
    "precipitation_hours",
    "relative_humidity_2m_mean",
    "wind_speed_10m_max",
    "wind_gusts_10m_max",
    "et0_fao_evapotranspiration",
]
# Yalnız tahmin uç noktasında anlamlı olanlar.
_FORECAST_EXTRA = ["weather_code", "precipitation_probability_max"]

_TIMEOUT = 25
_RETRIES = 3


def _get_json(base_url: str, params: dict[str, object]) -> dict:  # type: ignore[type-arg]
    """JSON çek; geçici ağ hatalarında birkaç kez tekrar dene."""
    url = base_url + "?" + urllib.parse.urlencode(params)
    last_err: Exception | None = None
    for attempt in range(_RETRIES):
        try:
            with urllib.request.urlopen(url, timeout=_TIMEOUT) as resp:
                return json.loads(resp.read())  # type: ignore[no-any-return]
        except (urllib.error.URLError, TimeoutError) as exc:
            last_err = exc
            if attempt < _RETRIES - 1:
                time.sleep(1.5 * (attempt + 1))  # artan bekleme
    raise ValueError(f"Open-Meteo API erişim hatası ({_RETRIES} deneme): {last_err}")


def _parse(raw: dict) -> list[DailyWeather]:  # type: ignore[type-arg]
    daily = raw.get("daily", {})
    dates = daily.get("time", [])
    n = len(dates)

    def col(name: str) -> list:  # type: ignore[type-arg]
        values: list = daily.get(name, [None] * n)  # type: ignore[type-arg]
        return values

    t_max  = col("temperature_2m_max")
    t_min  = col("temperature_2m_min")
    t_mean = col("temperature_2m_mean")
    precip = col("precipitation_sum")
    rain   = col("rain_sum")
    snow   = col("snowfall_sum")
    p_hrs  = col("precipitation_hours")
    hum    = col("relative_humidity_2m_mean")
    wind   = col("wind_speed_10m_max")
    gust   = col("wind_gusts_10m_max")
    et0    = col("et0_fao_evapotranspiration")
    wcode  = col("weather_code")
    pprob  = col("precipitation_probability_max")

    return [
        DailyWeather(
            date=date.fromisoformat(d),
            temp_max=t_max[i],
            temp_min=t_min[i],
            temp_mean=t_mean[i],
            precipitation_mm=precip[i],
            rain_mm=rain[i],
            snowfall_cm=snow[i],
            precipitation_hours=p_hrs[i],
            humidity_pct=hum[i],
            wind_max_kmh=wind[i],
            wind_gust_kmh=gust[i],
            et0_mm=et0[i],
            weather_code=wcode[i],
            precip_probability=pprob[i],
        )
        for i, d in enumerate(dates)
    ]


def fetch_historical(lat: float, lon: float, start: date, end: date) -> list[DailyWeather]:
    """Arşiv API: start..end (dahil) arası geçmiş günler."""
    yesterday = date.today() - timedelta(days=1)
    end = min(end, yesterday)  # arşiv en fazla dünü kapsar
    if end < start:
        return []
    raw = _get_json(_ARCHIVE_BASE, {
        "latitude":   lat,
        "longitude":  lon,
        "start_date": start.isoformat(),
        "end_date":   end.isoformat(),
        "daily":      ",".join(_COMMON_DAILY),
        "timezone":   TIMEZONE,
    })
    return _parse(raw)


def fetch_forecast(lat: float, lon: float, days: int = 16) -> list[DailyWeather]:
    """Tahmin API: bugünden itibaren `days` günlük tahmin (en çok 16)."""
    raw = _get_json(_FORECAST_BASE, {
        "latitude":      lat,
        "longitude":     lon,
        "daily":         ",".join(_COMMON_DAILY + _FORECAST_EXTRA),
        "forecast_days": min(days, 16),
        "timezone":      TIMEZONE,
    })
    return _parse(raw)


def fetch_season(
    lat: float, lon: float, season_start: date, forecast_days: int = 16
) -> list[DailyWeather]:
    """Sezon başından bugüne geçmiş + önümüzdeki günlerin tahmini, birleşik.

    Tarih bazında çakışma olursa geçmiş (ölçülmüş) veri korunur.
    Geçmiş veri henüz yoksa yalnız tahmin döner.
    """
    historical = fetch_historical(lat, lon, season_start, date.today())
    forecast   = fetch_forecast(lat, lon, forecast_days)

    seen: set[date] = {d.date for d in historical}
    combined = list(historical)
    combined.extend(d for d in forecast if d.date not in seen)
    return sorted(combined, key=lambda d: d.date)
