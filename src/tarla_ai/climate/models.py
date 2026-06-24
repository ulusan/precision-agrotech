"""İklim veri modelleri — günlük hava ve büyüme dönemi özeti."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DailyWeather:
    """Tek günün hava verisi (Open-Meteo'dan).

    Ölçülmeyen/gelmeyen alanlar None'dur — uydurulmaz.
    """

    date: date
    temp_max: float | None        # gündüz en yüksek (°C)
    temp_min: float | None        # gece en düşük (°C)
    temp_mean: float | None       # gün ortalaması (°C)
    precipitation_mm: float | None  # toplam yağış: yağmur + kar suyu (mm)
    rain_mm: float | None         # yalnız yağmur (mm)
    snowfall_cm: float | None     # kar (cm)
    precipitation_hours: float | None  # gün içinde yağışın sürdüğü saat
    humidity_pct: float | None    # gün ortalama bağıl nem (%)
    wind_max_kmh: float | None    # en yüksek rüzgâr (km/sa)
    wind_gust_kmh: float | None   # en yüksek rüzgâr hamlesi (km/sa)
    et0_mm: float | None          # FAO referans buharlaşma-terleme (mm)
    weather_code: int | None = None      # WMO hava durumu kodu (yalnız tahmin)
    precip_probability: float | None = None  # yağış ihtimali % (yalnız tahmin)

    @property
    def is_forecast(self) -> bool:
        from datetime import date as _date
        return self.date >= _date.today()


@dataclass(frozen=True)
class MonthlyTotals:
    """Bir takvim ayının iklim toplamları."""

    year: int
    month: int
    rain_mm: float        # yağmur
    snow_water_mm: float  # kar suyu eşdeğeri (toplam yağış − yağmur)
    snow_cm: float        # kar kalınlığı
    tmax_avg: float
    tmin_avg: float
    et0_mm: float


@dataclass(frozen=True)
class SeasonSummary:
    """Sezon başından bugüne (ölçülmüş günlere dayalı) buğday iklim özeti."""

    start: date
    end: date
    day_count: int
    total_rain_mm: float       # toplam yağış (yağmur + kar suyu)
    rainy_days: int
    total_snow_cm: float
    total_et0_mm: float
    water_deficit_mm: float    # et0 − yağış
    total_gdd: float           # taban 0°C, ekimden bugüne biriken sıcaklık
    frost_days: int            # gece < 0 °C
    heat_days: int             # gündüz > 30 °C
    min_temp_c: float
    max_temp_c: float
    vernalization_days: int    # Kas–Şub, gün ortalaması 0–10 °C
    avg_humidity_pct: float
    max_wind_kmh: float


@dataclass(frozen=True)
class StageWeatherSummary:
    """Bir büyüme dönemine ait toplanmış iklim özeti."""

    stage_name: str
    bbch: str
    start_date: date
    end_date: date
    day_count: int            # verisi olan gün sayısı
    total_rain_mm: float      # toplam yağış (yağmur + kar suyu)
    total_rain_only_mm: float # yalnız yağmur
    total_snow_cm: float      # toplam kar
    rainy_days: int           # ≥ 1 mm yağış düşen gün sayısı
    avg_temp_c: float
    avg_humidity_pct: float
    max_wind_kmh: float
    total_et0_mm: float       # FAO buharlaşma toplamı
    water_deficit_mm: float   # et0 − yağış; > 0 su açığı, < 0 yağış fazlası
    frost_days: int           # gece < 0 °C
    heat_days: int            # gündüz > 30 °C
    has_data: bool            # dönem için veri var mı
