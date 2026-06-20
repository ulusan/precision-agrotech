"""Toprak parametresi referans aralıkları — Ankara/Bala kıraç ekmeklik buğday.

Kaynaklar: TAGEM gübre tavsiye sistemi, Toprak Gübre ve Su Kaynakları Merkez
Araştırma Enstitüsü, MEGEP toprak verimlilik standartları, FAO buğday besleme
kılavuzları, Lindsay-Norvell DTPA kritik düzeyleri.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SoilReference:
    """Tek bir toprak parametresinin referans aralığı.

    low_max:  bu değerin ALTI düşük/yetersiz (None ise alt sınır yok)
    ideal:    (ideal_low, ideal_high) yeterli aralık
    high_min: bu değerin ÜSTÜ yüksek/fazla (None ise üst sınır yok)
    """

    name: str
    unit: str
    low_max: float | None
    ideal_low: float
    ideal_high: float
    high_min: float | None
    note: str


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
