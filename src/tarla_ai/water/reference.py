"""Sulama suyu kalite referansları + kalıcı kuyu suyu kaydı.

İki ayrı şey içerir:

1. WATER_REFERENCE — sulama suyu parametrelerinin yorumlama eşikleri
   (FAO-29 Ayers & Westcot sulama suyu kalite kılavuzu + USDA tuzluluk
   sınıflandırması C1–C4). Buğday/arpa tuzluluk toleransı dahil.

2. WELL_WATER_BASELINE — pilot tarlanın KALICI kuyu suyu kaydı
   (data/uploads/water/su-analiz.pdf, Ankara Üniv. Ziraat Fak.,
   Rapor No TAR-2024-0004, onay 07.05.2024). Bu kayıt değişmez
   referans katmandır; ölçülmeyen parametreler None'dur ve uydurulmaz.

Kaynaklar: FAO Irrigation and Drainage Paper 29 (Ayers & Westcot, 1985),
USDA Handbook 60 tuzluluk sınıfları, Maas-Hoffman bitki tuz toleransı.
"""

from __future__ import annotations

from dataclasses import dataclass

from tarla_ai.water.parsing import WaterReport


@dataclass(frozen=True)
class WaterReference:
    """Tek bir sulama suyu parametresinin yorumlama eşiği.

    ok_max:    bu değere kadar sorun yok (None ise alt-iyi yok)
    caution:   (caution_low, caution_high) artan kısıtlama / dikkat bandı
    severe_min: bu değerin ÜSTÜ şiddetli kısıtlama (None ise üst sınır yok)
    """

    name: str
    unit: str
    ok_max: float | None
    caution_low: float
    caution_high: float
    severe_min: float | None
    note: str


# ── FAO-29 sulama suyu yorumlama eşikleri ───────────────────────────────────
WATER_REFERENCE: list[WaterReference] = [
    WaterReference(
        "pH", "—", 7.0, 6.5, 8.4, 8.5,
        "FAO normal aralık 6.5–8.4. 5.84 hafif asidik; tek başına bitkiye "
        "zarar vermez ama kalkerli İç Anadolu toprağında büyük ölçüde "
        "tamponlanır. Damla sulamada düşük pH boruları aşındırabilir.",
    ),
    WaterReference(
        "EC (Tuzluluk)", "dS/m", 0.7, 0.7, 3.0, 3.0,
        "FAO: <0.7 kısıtlama yok, 0.7–3.0 hafif-orta kısıtlama, >3.0 şiddetli. "
        "Ölçülen 2.90 dS/m orta-şiddetli sınırında (USDA C3-C4). Buğday eşik "
        "tuzluluğu ECe 6 dS/m, arpa 8 dS/m — bitki toleranslı ama tekrarlı "
        "sulamada toprakta tuz birikir.",
    ),
    WaterReference(
        "SAR (Sodyum Adsorpsiyon Oranı)", "—", 3.0, 3.0, 9.0, 9.0,
        "Toprak yapısı/geçirgenlik riski. <3 düşük, 3–9 orta, >9 yüksek "
        "(kil dispersiyonu, geçirgenlik kaybı). BU SUDA ÖLÇÜLMEDİ — Na, Ca, "
        "Mg gerektirir. Bölgede sodyum-bikarbonat kökenli kuyular yaygın "
        "olduğundan ölçülmesi kritik.",
    ),
    WaterReference(
        "Sodyum (Na)", "mg/L", 70.0, 70.0, 200.0, 200.0,
        "Damla/yağmurlama ile yaprak yanması ve toprak yapısı riski. "
        "FAO yüzey sulamada SAR ile, yağmurlamada >70 mg/L dikkat. "
        "BU SUDA ÖLÇÜLMEDİ.",
    ),
    WaterReference(
        "Klorür (Cl)", "mg/L", 140.0, 140.0, 350.0, 350.0,
        "Toksik iyon. FAO: <140 kısıtlama yok, 140–350 orta, >350 şiddetli "
        "(yaprak yanması). BU SUDA ÖLÇÜLMEDİ.",
    ),
    WaterReference(
        "Bikarbonat (HCO₃)", "mg/L", 90.0, 90.0, 500.0, 520.0,
        "Yüksek HCO₃ Ca'yı çöktürüp SAR'ı yükseltir, damlatıcı tıkar, yaprakta "
        "beyaz leke yapar. FAO: <90 sorunsuz, >520 şiddetli. BU SUDA ÖLÇÜLMEDİ.",
    ),
    WaterReference(
        "Bor (B)", "mg/L", 0.7, 0.7, 2.0, 2.0,
        "Dar güvenli aralıklı toksik element. Buğday/arpa orta toleranslı "
        "(~2 mg/L'ye kadar). FAO sulama suyu üst sınırı genelde 0.7–3.0. "
        "BU SUDA ÖLÇÜLMEDİ — İç Anadolu'da yer yer bor fazlalığı görülür.",
    ),
]


# ── Kalıcı kuyu suyu kaydı (data/uploads/water/su-analiz.pdf) ───────────────
# Ankara Üniversitesi Ziraat Fakültesi, Rapor No TAR-2024-0004, onay 07.05.2024.
# Müşteri: Abdullah Ulusan, Üçem Köyü, Bala/Ankara.
# Yalnızca pH ve EC ölçülmüştür; diğer parametreler raporda YOK = None.
WELL_WATER_REPORT_META: dict[str, str] = {
    "kaynak": "Kuyu (pilot tarla tek sulama kaynağı)",
    "konum": "Ankara · Bala · Üçem Köyü",
    "laboratuvar": "Ankara Üniv. Ziraat Fak. Toprak Bilimi ve Bitki Besleme",
    "rapor_no": "TAR-2024-0004",
    "onay_tarihi": "2024-05-07",
    "kapsam": "Yalnızca pH + EC ölçüldü; iyon/SAR/bor analizi yapılmadı",
}

WELL_WATER_BASELINE: WaterReport = WaterReport(
    ph=5.84,
    ec_ds_m=2.90,
    # Aşağıdakiler raporda ÖLÇÜLMEDİ — None bırakılır, uydurulmaz:
    sar=None,
    sodium_mg_l=None,
    chloride_mg_l=None,
    bicarbonate_mg_l=None,
    carbonate_mg_l=None,
    boron_mg_l=None,
    calcium_mg_l=None,
    magnesium_mg_l=None,
    sulfate_mg_l=None,
    nitrate_mg_l=None,
)
