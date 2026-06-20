"""Büyüme dönemleri ve azot özeti — kıraç ekmeklik buğday."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GrowthStage:
    """BBCH büyüme döneminde buğdayın besin/su ihtiyacı."""

    donem: str
    bbch: str
    n_seviye: str
    n_doz: str
    su_ihtiyaci: str
    note: str


GROWTH_STAGES: list[GrowthStage] = [
    GrowthStage("Çimlenme / Çıkış", "00–10", "Düşük", "~3 kg N/da (taban)",
                "Düşük–Orta",
                "Taban: ~3 kg N/da (DAP) + tüm P₂O₅ (6–8 kg/da) ekimle. "
                "Çinko eksikse çinkolu DAP kullan."),
    GrowthStage("Kardeşlenme", "20–29", "Yüksek", "2–4 kg N/da (1. üst gübre)",
                "Orta",
                "Kardeş sayısını (verim bileşeni) belirler. Kıraçta ilkbahar yağışı "
                "öncesi/erken uygula ki kök bölgesine insin."),
    GrowthStage("Sapa Kalkma", "30–39", "Yüksek–Pik", "2–3 kg N/da (2. üst gübre)",
                "Yüksek (en kritik su dönemi)",
                "Azot alımı hızla artar; başak/başakçık sayısını belirler. "
                "Bu dönemdeki kuraklık verimi en çok düşürür."),
    GrowthStage("Bayrak Yaprak / Başaklanma", "37–51", "Yüksek (alım piki)",
                "Topraktan ek N yok",
                "Yüksek",
                "Azot alımı en üst düzeyde. Yapraktan üre/Zn takviyesi protein ve "
                "tane için yararlı."),
    GrowthStage("Çiçeklenme", "60–69", "Orta", "Opsiyonel yaprak N",
                "Yüksek (su stresine çok hassas)",
                "Döllenme dönemi; su stresi tane tutumunu düşürür. Geç N protein/"
                "kaliteyi artırır."),
    GrowthStage("Tane Dolumu", "70–89", "Düşük–Orta", "Protein için yaprak üre olabilir",
                "Orta–Yüksek (sonra azalır)",
                "Geç dönem N → tane protein/sertlik. Dolum sonunda su ihtiyacı düşer; "
                "aşırı geç su yatma riski yaratır."),
]

NITROGEN_SUMMARY: dict[str, str] = {
    "taban_N_kgda": "~3 kg N/da (ekimle DAP)",
    "ust_gubre_kurac": "3–7 kg N/da (kardeşlenme + sapa kalkma, parçalı)",
    "toplam_N_kurac": "6–10 kg N/da",
    "P2O5_taban": "6–8 kg/da (tümü ekimle)",
    "not": "Üst gübre, ilkbahar yağışıyla senkronize 2–3 parçaya bölünerek verilir. "
           "Su kıraçta verimi belirleyen 1. faktördür; aşırı N kuraklıkta zarar verir.",
}
