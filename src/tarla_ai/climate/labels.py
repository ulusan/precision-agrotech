"""Sade-dil açıklamaları — hiç tarım/hava bilmeyen biri için.

Her kısaltma ve terim burada günlük dille açıklanır. UI bu metinleri
tooltip ve açıklama kutularında kullanır; tek noktadan yönetilir.
"""

from __future__ import annotations

# ── Terim ve kısaltma sözlüğü (tooltip metinleri) ────────────────────────────
GLOSSARY: dict[str, str] = {
    "yagis": (
        "Yağış = gökten düşen su (yağmur + kar erimesi). Birimi milimetredir (mm). "
        "1 mm yağış, her 1 metrekareye 1 litre su düşmesi demektir. "
        "Örnek: 10 mm yağış = 1 m²'lik toprağa 10 litre su."
    ),
    "yagmur": (
        "Yağmur = sıvı halde düşen su. Kar değil. Buğday için en doğrudan işe "
        "yarayan yağıştır; hemen toprağa girer."
    ),
    "kar": (
        "Kar = donmuş yağış. Birimi santimetredir (cm). Kar kışın toprağı bir "
        "battaniye gibi örter, genç buğdayı dondan korur; eridiğinde toprağa su olur."
    ),
    "sicaklik": (
        "Günün en düşük (gece) ve en yüksek (gündüz) hava sıcaklığı. Buğdayın "
        "büyüme hızını ve don/sıcak stresi riskini belirler."
    ),
    "nem": (
        "Bağıl nem = havadaki su buharı oranı (%). %100 hava suya doymuş demektir. "
        "Düşük nem (örn. %30) hava çok kuru → toprak ve bitki hızlı su kaybeder. "
        "Yüksek nem + ılık hava ise mantar hastalıkları için elverişlidir."
    ),
    "ruzgar": (
        "En yüksek rüzgâr hızı (km/saat). Kuvvetli rüzgâr toprağı ve bitkiyi "
        "kurutur, ilaçlama/gübre serpmeyi zorlaştırır, sıcak günlerde su kaybını artırır."
    ),
    "et0": (
        "ET₀ (buharlaşma-terleme) = topraktan ve bitkiden havaya uçup giden su "
        "miktarı (mm). Hava ne kadar sıcak, kuru ve rüzgârlıysa ET₀ o kadar yüksek "
        "olur — yani toprak o kadar hızlı kurur. Bitkinin 'su iştahı' gibi düşünün."
    ),
    "su_dengesi": (
        "Su dengesi = Buharlaşma (ET₀) − Yağış. Toprağa giren su mu fazla, yoksa "
        "havaya uçan su mu fazla onu gösterir. Sonuç ARTI ise toprak kuruyor "
        "(su açığı var, sulama gerekebilir); EKSİ ise yağış buharlaşmadan fazla, "
        "toprak nemli demektir."
    ),
    "don": (
        "Don = gece sıcaklığın 0 °C'nin altına inmesi. Bitkinin içindeki su donar, "
        "hücreler zarar görür. Çiçeklenme döneminde dane bağlamayı bozabilir; "
        "kışın hafif don kardeşlenmeyi pek etkilemez."
    ),
    "sicak_stresi": (
        "Sıcak stresi = gündüz sıcaklığın 30 °C'yi aşması. Bu sıcaklarda buğday "
        "tanesini tam dolduramaz, verim ve tane ağırlığı düşer. Özellikle tane "
        "dolum döneminde zararlıdır."
    ),
    "bbch": (
        "BBCH = buğdayın gelişim aşamalarını sayıyla kodlayan uluslararası ölçek. "
        "00 = ekim/tohum, 89 = hasat olgunluğu. Aradaki numaralar kardeşlenme, "
        "sapa kalkma, başaklanma gibi dönemleri gösterir."
    ),
    "yagisli_gun": (
        "Yağışlı gün = o gün en az 1 mm yağış düşen gün. Yağışın kaç güne "
        "yayıldığını gösterir — aynı su, çok güne yayılınca toprağa daha iyi işler."
    ),
    "kumulatif": (
        "Kümülatif = toplana toplana giden. Kümülatif yağış eğrisi, sezon başından "
        "o güne kadar düşen TÜM yağışın toplamını gösterir; sürekli yükselir."
    ),
}

# ── WMO hava durumu kodu → Türkçe açıklama + emoji ───────────────────────────
# Open-Meteo "weather_code" alanı (yalnız tahminde gelir).
WEATHER_CODES: dict[int, tuple[str, str]] = {
    0:  ("☀️", "Açık"),
    1:  ("🌤️", "Az bulutlu"),
    2:  ("⛅", "Parçalı bulutlu"),
    3:  ("☁️", "Çok bulutlu / kapalı"),
    45: ("🌫️", "Sisli"),
    48: ("🌫️", "Kırağılı sis"),
    51: ("🌦️", "Hafif çisenti"),
    53: ("🌦️", "Çisenti"),
    55: ("🌧️", "Yoğun çisenti"),
    56: ("🌧️", "Donan çisenti"),
    57: ("🌧️", "Yoğun donan çisenti"),
    61: ("🌦️", "Hafif yağmur"),
    63: ("🌧️", "Yağmur"),
    65: ("🌧️", "Kuvvetli yağmur"),
    66: ("🌧️", "Donan yağmur"),
    67: ("🌧️", "Kuvvetli donan yağmur"),
    71: ("🌨️", "Hafif kar"),
    73: ("🌨️", "Kar"),
    75: ("❄️", "Yoğun kar"),
    77: ("🌨️", "Kar taneleri"),
    80: ("🌦️", "Hafif sağanak"),
    81: ("🌧️", "Sağanak"),
    82: ("⛈️", "Şiddetli sağanak"),
    85: ("🌨️", "Hafif kar sağanağı"),
    86: ("❄️", "Yoğun kar sağanağı"),
    95: ("⛈️", "Gök gürültülü fırtına"),
    96: ("⛈️", "Dolulu fırtına"),
    99: ("⛈️", "Şiddetli dolulu fırtına"),
}


def weather_text(code: int | None) -> tuple[str, str]:
    """WMO koduna göre (emoji, açıklama). Bilinmeyen kod için nötr değer."""
    if code is None:
        return ("", "—")
    return WEATHER_CODES.get(int(code), ("🌡️", "Bilinmiyor"))
