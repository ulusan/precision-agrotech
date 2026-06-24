"""Bala (Ankara) konumları, sezon dönem pencereleri ve sade-dil açıklamaları.

Pilot tarla = Bahçekaradalak (kullanıcının verdiği tam arazi koordinatı).
Diğer mahalleler (Üçem/Karadalak/Boyalık) seçilebilir; hepsi birbirine
birkaç km uzaklıkta olduğu için hava değerleri birbirine çok yakın çıkar —
hava bölgeseldir. Yine de her konum kendi grid hücresinden sorgulanır.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Location:
    """Hava verisi çekilecek bir konum (mahalle/arazi)."""

    key: str
    label: str       # arayüzde görünen ad
    lat: float
    lon: float
    note: str        # kısa açıklama (pilot tarlaya göre konum)


# Sıralama önemli: ilk eleman varsayılan (pilot tarla).
LOCATIONS: list[Location] = [
    Location(
        "pilot", "🎯 Pilot Tarla — Bahçekaradalak",
        39.515633, 33.213664,
        "Asıl arazi. Tüm tarım kararları bu noktanın havasına göre verilir.",
    ),
    Location(
        "ucem", "🏠 Üçem (köy / ev)",
        39.560188, 33.215805,
        "Yaşadığınız köy — pilot tarlanın yaklaşık 5 km kuzeyi.",
    ),
    Location(
        "karadalak", "Karadalak (köy merkezi)",
        39.506542, 33.186378,
        "Bahçe Karadalak köy merkezi — pilot tarlanın yaklaşık 2,5 km güneybatısı.",
    ),
    Location(
        "boyalik", "Boyalık",
        39.567673, 33.236252,
        "Büyük Boyalık — pilot tarlanın yaklaşık 6 km kuzeydoğusu.",
    ),
]

DEFAULT_LOCATION: Location = LOCATIONS[0]


def location_by_key(key: str) -> Location:
    """Anahtara göre konumu döndür; bulunamazsa pilot tarlayı."""
    for loc in LOCATIONS:
        if loc.key == key:
            return loc
    return DEFAULT_LOCATION


TIMEZONE: str = "Europe/Istanbul"

# ── Sezon takvimi — 2025-2026 kışlık ekmeklik buğday (Ankara/Bala) ───────────
# (dönem adı, BBCH kodu, başlangıç, bitiş). Fenoloji yıla göre ±10 gün kayar.
STAGE_WINDOWS: list[tuple[str, str, date, date]] = [
    ("Çimlenme / Çıkış",           "00–10", date(2025, 10, 5),  date(2025, 11, 10)),
    ("Kardeşlenme",                 "20–29", date(2025, 11, 10), date(2026, 2, 28)),
    ("Sapa Kalkma",                 "30–39", date(2026, 3, 1),   date(2026, 4, 15)),
    ("Bayrak Yaprak / Başaklanma",  "37–51", date(2026, 4, 15),  date(2026, 5, 20)),
    ("Çiçeklenme",                  "60–69", date(2026, 5, 20),  date(2026, 6, 10)),
    ("Tane Dolumu",                 "70–89", date(2026, 6, 10),  date(2026, 7, 10)),
    ("Hasat",                       "89",    date(2026, 7, 10),  date(2026, 7, 25)),
]

# Dönem boyunca toprağa düşmesi gereken en az yağış (mm) — kıraç koşul referansı.
STAGE_MIN_RAIN_MM: dict[str, float] = {
    "Çimlenme / Çıkış":            30.0,
    "Kardeşlenme":                 60.0,
    "Sapa Kalkma":                 70.0,
    "Bayrak Yaprak / Başaklanma":  45.0,
    "Çiçeklenme":                  30.0,
    "Tane Dolumu":                 25.0,
    "Hasat":                        5.0,
}

# Stres eşikleri
FROST_THRESHOLD_C: float = 0.0     # gece en düşük sıcaklık bunun altındaysa: don
HEAT_THRESHOLD_C: float = 30.0     # gündüz en yüksek sıcaklık bunun üstündeyse: sıcak stresi
RAINY_DAY_MM: float = 1.0          # bir günü "yağışlı" saymak için en az yağış

# GDD (büyüme gün dereceleri) taban sıcaklığı — kışlık buğday için standart 0°C.
GDD_BASE_C: float = 0.0
# Buğdayın ekimden hasada kabaca biriktirmesi gereken GDD aralığı (referans).
GDD_TARGET_MIN: float = 2000.0
GDD_TARGET_MAX: float = 2300.0
