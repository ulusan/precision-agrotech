"""Toprak parametresi referans aralıkları — Ankara/Bala kıraç ekmeklik buğday.

Pilot tarla: Bahçekaradalak köyü, Bala/Ankara (39.51563 N, 33.21366 E).

Kaynaklar:
  [1] Ülgen & Yurtsever 1974/1995 — Türkiye Gübre ve Gübreleme Rehberi
  [2] Richards 1954 — pH/EC standartları
  [3] Hızalan & Ünal 1966 — Kireç sınıflandırması
  [4] Lindsay & Norvell 1978 — DTPA Fe kritik düzeyleri
  [5] Silanpää 1990 — N/P/K/Zn/Mn/B dünya gübreleme çalışması
  [6] Wolf 1971 — B Azomethin-H yöntemi
  [7] Follett 1969 — Cu yeterlilik eşiği
  [8] Soba ve ark. 2015 — Haymana A.Ü. Çiftliği toprak verimliliği
      (Bala'nın komşusu; 65 örnek; Fe/Mn/B tüm parsellerde yetersiz)
  [9] Toprak Analizleri ve Yorumlanması, Dr. Elif Öztürk,
      Karadeniz TARE, 2021 — resmi Türk sınıflandırma tabloları
  [10] İç Anadolu bölge haritalaması — DergiPark 2019

Bölgesel zemin: hafif alkalin (pH 7.5-8.5), yüksek kireçli (%16-39 CaCO₃),
ağır bünyeli (kil > %45), organik maddece fakir, Fe/Mn/B kronik yetersiz.
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
    SoilReference("pH", "—", 6.5, 6.5, 7.8, 8.5,
                  "Richards 1954 [2]: 6.5–7.5 nötr, 7.5–8.5 hafif alkalin, >8.5 kuvvetli alkalin. "
                  "Haymana/Bala bölgesi tipik 7.9–8.7 (Soba ve ark. 2015 [8]: min 7.90, maks 8.68). "
                  "pH > 7.8'de Zn, Fe, Mn ve P alınabilirliği belirgin düşer; yüksek kireç ana etken."),

    SoilReference("Organik Madde", "%", 2.0, 2.0, 3.0, 5.15,
                  "Ülgen-Yurtsever 1974 [1]: <1.0 çok az, 1.0–2.0 az, 2.0–3.0 orta, >3.0 yüksek. "
                  "Haymana çiftlik topraklarının %88'i 1.0–2.0 g/kg bandında (az sınıfı). "
                  "Bahçekaradalak bölgesinde %1.0–1.8 aralığı tipiktir. "
                  "2–3 ton/da iyi kompostlanmış çiftlik gübresi (Rosen ve ark. 1999) önerilir."),

    SoilReference("Toplam Azot", "%", 0.09, 0.09, 0.25, 0.50,
                  "Silanpää 1990 [5]: <0.045 çok az, 0.045–0.09 az, 0.09–0.17 orta, 0.17–0.32 yüksek. "
                  "Haymana'da toprakların %85.9'u 0.09–0.17 g/kg (orta) sınıfında. "
                  "Organik madde ile doğrudan bağlantılı; kıraçta ekimde azot takviyesi kritik."),

    SoilReference("Alınabilir Fosfor (P₂O₅)", "kg/da", 6.0, 6.0, 9.0, 12.0,
                  "Olsen yöntemi, Ülgen-Yurtsever 1995 [1]: <3 çok az, 3–6 az, 6–9 orta, 9–12 yüksek. "
                  "Silanpää [5] mg/kg: <2.5 çok az, 2.5–8 az, 8–25 yeterli. "
                  "Haymana'da parsellerin %58.9'u az sınıfı (2.5–8 mg/kg). "
                  "Bala örnek raporu: 2.5 kg/da — çok az. Taban gübresi olarak DAP önerilir."),

    SoilReference("Alınabilir Potasyum (K₂O)", "kg/da", 30.0, 30.0, 40.0, 40.0,
                  "Ülgen-Yurtsever 1995 [1], amonyum asetat yöntemi. "
                  "Silanpää [5] me/100g: <0.13 çok az, 0.13–0.28 az, 0.28–0.74 yeterli. "
                  "Haymana'nın %68.2'si 0.28–0.74 me/100g (yeterli). "
                  "İç Anadolu kil mineralojisi nedeniyle K genelde yeterli; ek K çoğunlukla gerekmez."),

    SoilReference("Kalsiyum (Ca)", "ppm", 714.0, 1430.0, 2860.0, None,
                  "Ülgen-Yurtsever [1] mg/kg: <714 çok düşük, 714–1430 düşük, 1430–2860 orta, >2860 yüksek. "
                  "Kalkerli Haymana/Bala topraklarında Ca daima yüksek/bol — eksiklik beklenmez."),

    SoilReference("Magnezyum (Mg)", "ppm", 54.0, 115.0, 480.0, None,
                  "Ülgen-Yurtsever [1] mg/kg: <54 çok düşük, 54–115 düşük, >115 orta/yüksek. "
                  "Bölgede genelde yeterli; aşırı Ca, Mg alımını baskılayabilir."),

    SoilReference("EC / Tuzluluk", "dS/m", None, 0.0, 4.0, 8.0,
                  "Richards 1954 [2] saturasyon çamuru: 0–2 tuzsuz, 2–4 hafif, 4–8 orta, >8 kuvvetli. "
                  "Haymana: min 0.27, maks 1.70 dS/m — tüm parseller tuzsuz sınıfında. "
                  "Bala bölgesinde tuzluluk sorunu beklenmez."),

    SoilReference("Kireç (CaCO₃)", "%", 1.0, 1.0, 15.0, 25.0,
                  "Hızalan-Ünal 1966 [3]: <0.2 kireçsiz, 0.2–0.4 az, 0.4–0.8 orta, 0.8–1.5 kireçli, >1.5 çok kireçli. "
                  "Haymana: min %16.5, maks %38.8 — tüm parseller çok kireçli [8]. "
                  "Yüksek kireç; P, Fe, Zn ve Mn bağlanmasının birincil nedenidir. "
                  "Bala örnek raporu: %6.5 (orta kireçli bandın üst sınırı)."),

    SoilReference("Çinko (Zn)", "mg/kg", 0.7, 0.7, 2.4, 8.0,
                  "Silanpää 1990 [5] DTPA: <0.2 çok az, 0.2–0.7 az, 0.7–2.4 yeterli, 2.4–8 fazla. "
                  "Haymana: toprakların %16.5'i az sınıfı (0.2–0.7), %83'ü yeterli (0.7–2.4) [8]. "
                  "Kireç-Zn negatif korelasyonu saptanmıştır (r=-0.259). "
                  "Bala örnek raporu: 0.6 ppm → az sınıfı. ZnSO₄ uygulaması önerilir."),

    SoilReference("Demir (Fe)", "mg/kg", 2.5, 4.5, 10.0, 10.0,
                  "Lindsay-Norvell 1978 [4] DTPA: <2.5 az, 2.5–4.5 orta, >4.5 yeterli. "
                  "Bölgesel kanıt [8]: Bala çevresindeki Haymana çiftliğinde tüm parsellerde "
                  "Fe yetersiz (maks 2.4 mg/kg) — yüksek kireç ve alkali pH'nın tipik sonucu. "
                  "Pilot tarlanın Fe değeri toprak analizi yüklenince bu eşikle yorumlanır. "
                  "Şelatlı Fe yapraktan uygulaması en etkili yöntemdir."),

    SoilReference("Bakır (Cu)", "mg/kg", 0.2, 0.2, 1.5, 3.0,
                  "Follett 1969 [7] DTPA: <0.2 yetersiz, ≥0.2 yeterli. "
                  "Haymana'da Cu yeterli sınıfında; kireç-Cu negatif korelasyon (r=-0.250) [8]. "
                  "Bölgede eksiklik nadir; izleme yeterli."),

    SoilReference("Mangan (Mn)", "mg/kg", 4.0, 14.0, 50.0, 170.0,
                  "Silanpää 1990 [5] DTPA: <4 az, 4–14 düşük, 14–50 yeterli, 50–170 fazla. "
                  "Bölgesel kanıt [8]: Bala çevresindeki Haymana çiftliğinde tüm parsellerde "
                  "Mn yetersiz (maks 4.7 mg/kg) — alkali kireçli toprakların kronik sorunu. "
                  "Pilot tarlanın Mn değeri toprak analizi yüklenince bu eşikle yorumlanır."),

    SoilReference("Bor (B)", "mg/kg", 0.5, 1.0, 2.4, 5.0,
                  "Wolf 1971 [6] sıcak su: <0.4 çok az, 0.5–0.9 az, 1.0–2.4 yeterli, 2.5–4.9 fazla, >5.0 çok fazla. "
                  "Bölgesel kanıt [8]: Bala çevresindeki Haymana çiftliğinde parsellerin %95.9'u "
                  "az/çok az sınıfında (<0.9 mg/kg). "
                  "Pilot tarlanın B değeri toprak analizi yüklenince bu eşikle yorumlanır. "
                  "Buğday bora orta duyarlı; boraks veya Solubor yapraktan uygulanabilir."),

    SoilReference("Katyon Değişim Kap. (CEC)", "me/100g", 12.0, 12.0, 25.0, 25.0,
                  "Kil + kireç nedeniyle İç Anadolu/Haymana topraklarında genelde orta-yüksek (15–30 me/100g). "
                  "Ağır bünyeli (kil > %45) yapı yüksek CEC sağlar [8]."),
]
