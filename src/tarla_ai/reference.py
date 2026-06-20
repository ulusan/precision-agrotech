"""Referans değerler — Ankara/Bala, İç Anadolu kıraç ekmeklik buğday.

Bu değerler ölçüm değil, REFERANS aralıklarıdır. Toprak analizi ve drone
görüntüleri elde edildiğinde, ölçülen değerler bu aralıklarla karşılaştırılır.

Kaynaklar: TAGEM gübre tavsiye sistemi, Toprak Gübre ve Su Kaynakları Merkez
Araştırma Enstitüsü, MEGEP toprak verimlilik standartları, FAO buğday besleme
kılavuzları, Lindsay-Norvell DTPA kritik düzeyleri.

İç Anadolu kıraç koşulu esas alınmıştır: yüksek kireç, düşük organik madde,
hafif alkali pH, yaygın çinko eksikliği.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SoilReference:
    """Tek bir toprak parametresinin referans aralığı.

    low_max:  bu değerin ALTI düşük/yetersiz (None ise alt sınır yok)
    ideal:    (alt, üst) yeterli aralık
    high_min: bu değerin ÜSTÜ yüksek/fazla (None ise üst sınır yok)
    """

    name: str
    unit: str
    low_max: float | None
    ideal_low: float
    ideal_high: float
    high_min: float | None
    note: str


# ── TABLO 1 — Toprak besin elementi referans aralıkları ──────────────────────
SOIL_REFERENCE: list[SoilReference] = [
    SoilReference("pH", "—", 6.5, 6.5, 7.8, 8.0,
                  "Bölge tipik 7.5–8.2 hafif alkali. Buğday için sorun değil; "
                  "pH > 7.8'de Zn, Fe, Mn ve P alınabilirliği düşer."),
    SoilReference("Organik Madde", "%", 2.0, 2.0, 3.0, 4.0,
                  "İç Anadolu tipik %1–2 (düşük). Anız ve ahır gübresi ile "
                  "artırmak verimi belirgin yükseltir."),
    SoilReference("Toplam Azot", "%", 0.09, 0.09, 0.17, 0.17,
                  "Organik madde ile paralel; kıraçta genelde düşük (~0.05–0.09). "
                  "Azot gübrelemesi bu nedenle kritik."),
    SoilReference("Alınabilir Fosfor (P₂O₅)", "kg/da", 6.0, 6.0, 9.0, 9.0,
                  "Olsen yöntemi. Çok az <3, az 3–6, yeterli 6–9, yüksek >9. "
                  "Kıraçta sıklıkla orta-düşük; tüm P ekimle taban verilmeli."),
    SoilReference("Alınabilir Potasyum (K₂O)", "kg/da", 30.0, 30.0, 40.0, 40.0,
                  "Amonyum asetat yöntemi. İç Anadolu kil mineralojisi nedeniyle "
                  "genelde yeterli–yüksek; ek K çoğunlukla gerekmez."),
    SoilReference("Kalsiyum (Ca)", "ppm", 1150.0, 2850.0, 6000.0, 6000.0,
                  "Kalkerli topraklarda Ca daima yüksek/bol — eksiklik beklenmez."),
    SoilReference("Magnezyum (Mg)", "ppm", 50.0, 160.0, 480.0, 480.0,
                  "Genelde yeterli; aşırı Ca, Mg ve K alımını baskılayabilir."),
    SoilReference("EC / Tuzluluk", "dS/m", None, 0.0, 2.0, 4.0,
                  "Kıraç topraklarda genelde <1 dS/m, sorun değil. >4 tuzlu kabul edilir."),
    SoilReference("Kireç (CaCO₃)", "%", 1.0, 1.0, 15.0, 15.0,
                  "İç Anadolu tipik %10–25 (yüksek/çok kireçli) — Zn, Fe ve P "
                  "bağlanmasının ana nedeni."),
    SoilReference("Çinko (Zn)", "mg/kg", 0.5, 0.5, 1.0, 1.0,
                  "DTPA. Kritik düzey 0.5 ppm. İç Anadolu kalkerli topraklarda Zn "
                  "eksikliği ÇOK YAYGIN — çinkolu gübre (ZnSO₄ ~2–3 kg/da) önerilir."),
    SoilReference("Demir (Fe)", "mg/kg", 4.5, 4.5, 10.0, 10.0,
                  "DTPA. Kritik düzey 4.5 ppm. Yüksek pH/kireçte alınabilirlik düşer."),
    SoilReference("Bakır (Cu)", "mg/kg", 0.2, 0.2, 1.0, 1.0,
                  "DTPA. Kritik düzey 0.2 ppm. Eksiklik bölgede nadirdir."),
    SoilReference("Mangan (Mn)", "mg/kg", 1.0, 1.0, 14.0, 14.0,
                  "DTPA. Kritik düzey 1.0 ppm; alkali toprakta sınırda olabilir."),
    SoilReference("Bor (B)", "mg/kg", 0.5, 0.5, 1.0, 2.0,
                  "Sıcak su yöntemi. İç Anadolu'da yer yer B fazlalığı/toksisitesi "
                  "görülür; >2 ppm dikkat. Buğday bora orta duyarlıdır."),
    SoilReference("Katyon Değişim Kap. (CEC)", "me/100g", 12.0, 12.0, 25.0, 25.0,
                  "Kil + kireç nedeniyle İç Anadolu'da genelde orta-yüksek (15–30)."),
]


@dataclass(frozen=True)
class GrowthStage:
    """BBCH büyüme döneminde buğdayın besin/su ihtiyacı."""

    donem: str
    bbch: str
    n_seviye: str        # azot ihtiyaç düzeyi
    n_doz: str           # önerilen kg N/da (kıraç)
    su_ihtiyaci: str
    note: str


# ── TABLO 2 — BBCH dönemlerine göre N/su ihtiyacı (kıraç ekmeklik buğday) ─────
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


# ── Toplam azot özeti (kıraç ekmeklik buğday) ────────────────────────────────
NITROGEN_SUMMARY = {
    "taban_N_kgda": "~3 kg N/da (ekimle DAP)",
    "ust_gubre_kurac": "3–7 kg N/da (kardeşlenme + sapa kalkma, parçalı)",
    "toplam_N_kurac": "6–10 kg N/da",
    "P2O5_taban": "6–8 kg/da (tümü ekimle)",
    "not": "Üst gübre, ilkbahar yağışıyla senkronize 2–3 parçaya bölünerek verilir. "
           "Su kıraçta verimi belirleyen 1. faktördür; aşırı N kuraklıkta zarar verir.",
}
