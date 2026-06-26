"""Ekmeklik buğday çeşit önerileri.

Kaynaklar:
- TARM Çeşit Kataloğu 2025 (Tarla Bitkileri Merkez Araştırma Enstitüsü, Ankara)
- TARM Çeşit Kataloğu 2014 (Gıda Tarım ve Hayvancılık Bakanlığı / TARM, Ankara)
- Tekcan Tohum ürün sayfası (Hamza çeşidi)

Pilot tarla: Bahçekaradalak / Bala / Ankara — kıraç, killi-tınlı, İç Anadolu step iklimi.
Hiçbir değer uydurulmaz; kaynakta olmayan alan "—" gösterilir.
"""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from tarla_ai.ui.components.explainer_box import render_explainer
from tarla_ai.ui.html import section_head, th, tip, tip_attr

# ── Veri modeli ────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class VarietyInfo:
    name: str
    tescil: str          # tescil yılı
    verim_kuru: str      # kuru şartlar kg/da
    verim_sulu: str      # sulu/destek şartlar kg/da
    protein: str         # % protein
    hektolitre: str      # kg/hl
    kisa_dayaniklilik: str   # soğuğa/kışa
    kuraklik: str            # kurağa
    sari_pas: str            # sarı pas durumu
    tavsiye_bolge: str
    tarimsal: str        # kısa özellik özeti
    kaynak: str
    uyumluluk_skoru: int    # 1-5 (pilot tarla için)
    uyumluluk_not: str


# ── Çeşit verileri — TARM 2025 ekmeklik buğday sayfaları ─────────────────────

VARIETIES: list[VarietyInfo] = [
    # ── HAMZA (Tekcan Tohum — özel sektör) ─────────────────────────────────
    VarietyInfo(
        name="HAMZA",
        tescil="—",
        verim_kuru="350–500",
        verim_sulu="500–650",
        protein="%12–14",
        hektolitre="78–82",
        kisa_dayaniklilik="Yüksek",
        kuraklik="Yüksek",
        sari_pas="Toleranslı",
        tavsiye_bolge="İç Anadolu kuru ve yarı kuru alanlar",
        tarimsal=(
            "Kışlık, alternatif gelişme. Kışa ve kurağa dayanıklı. "
            "Yatmaya dayanıklı, sap sağlam. Tane dökmeyen. "
            "Orta-geç olgunlaşma."
        ),
        kaynak="Tekcan Tohum ürün sayfası",
        uyumluluk_skoru=5,
        uyumluluk_not=(
            "Bala/Ankara kuru şartlarına doğrudan önerilen çeşit. "
            "İç Anadolu kıraç bölgesi için üretici tarafından özellikle tavsiye edilmektedir."
        ),
    ),
    # ── BAYRAM (TARM 2020) ────────────────────────────────────────────────
    VarietyInfo(
        name="BAYRAM",
        tescil="2020",
        verim_kuru="450–550",
        verim_sulu="600–753",
        protein="%14.5–17.6",
        hektolitre="69.6–75.4",
        kisa_dayaniklilik="Yüksek",
        kuraklik="Yüksek",
        sari_pas="Toleranslı",
        tavsiye_bolge="İç ve Geçit Bölgelerin kıraç, yarı taban ve taban alanları",
        tarimsal=(
            "Kışlık, başaklanma zamanı erkenci. Orta-uzun boylu, kılçıklı beyaz başaklı, "
            "beyaz taneli. Soğuğa ve kurağa dayanıklı, kardeşlenmesi yüksek, yatmaya "
            "dayanıklı, tane dökmeyen. 1. sınıf ekmeklik kalite. "
            "Sedimantasyon 58–70 ml, alveograf enerjisi 247–333 J, gluten %34.4–44.9. "
            "Tescil denemelerinde en yüksek verim 752.9 kg/da, ortalama 560 kg/da."
        ),
        kaynak="TARM Kataloğu 2025 + TK Tohum (tktohum.com.tr)",
        uyumluluk_skoru=5,
        uyumluluk_not=(
            "Tarım Kredi ve TARM çift onaylı — İç ve Geçit kıraç için birinci öncelik. "
            "En yüksek protein oranı (%14.5–17.6) + 1. sınıf ekmeklik kalite. "
            "Tescil denemelerinde ortalama 560 kg/da, tepe 752.9 kg/da. "
            "Bala kıraç koşulları için en güçlü aday."
        ),
    ),
    # ── SELAMİBEY (TARM 2020) ────────────────────────────────────────────
    VarietyInfo(
        name="SELAMİBEY",
        tescil="2020",
        verim_kuru="450–550",
        verim_sulu="600–750",
        protein="%12.9–14.7",
        hektolitre="67.2–77.8",
        kisa_dayaniklilik="Yüksek",
        kuraklik="Yüksek",
        sari_pas="Orta dayanıklı",
        tavsiye_bolge="Orta Anadolu ve Geçit Kuşağı — kıraç, yarı taban ve taban",
        tarimsal=(
            "Alternatif gelişme, orta geç. Soğuğa ve kurağa dayanıklı, "
            "kardeşlenmesi ve su kullanım etkinliği yüksek. Yatmaya dayanıklı, "
            "tane dökmeyen."
        ),
        kaynak="TARM Çeşit Kataloğu 2025",
        uyumluluk_skoru=5,
        uyumluluk_not=(
            "Bayram ile eşit kuru verim bandı. Su kullanım etkinliği yüksek olması "
            "kıraç koşullar için kritik avantaj."
        ),
    ),
    # ── FAZILBEY (TARM 2020) ─────────────────────────────────────────────
    VarietyInfo(
        name="FAZILBEY",
        tescil="2020",
        verim_kuru="375–450",
        verim_sulu="500–600",
        protein="%10–12",
        hektolitre="71.0–76.3",
        kisa_dayaniklilik="Yüksek",
        kuraklik="Yüksek",
        sari_pas="Toleranslı",
        tavsiye_bolge="Orta Anadolu ve Geçit Kuşağı — kıraç, yarı taban ve taban",
        tarimsal=(
            "Alternatif gelişme, orta erkenci. Soğuğa ve kurağa dayanıklı, "
            "su kullanım etkinliği yüksek, yatmaya dayanıklı, tane dökmeyen."
        ),
        kaynak="TARM Çeşit Kataloğu 2025",
        uyumluluk_skoru=4,
        uyumluluk_not=(
            "İyi kuru verim, ancak protein oranı düşük (%10-12). "
            "Ekmeklik kalite öncelikli değilse güçlü alternatif."
        ),
    ),
    # ── KÜRŞAD (TARM 2020) ────────────────────────────────────────────────
    VarietyInfo(
        name="KÜRŞAD",
        tescil="2020",
        verim_kuru="350–450",
        verim_sulu="450–550",
        protein="%15.3–16.0",
        hektolitre="69.9–78.9",
        kisa_dayaniklilik="Yüksek",
        kuraklik="Yüksek",
        sari_pas="Orta dayanıklı",
        tavsiye_bolge="Orta Anadolu ve Geçit Kuşağı — kıraç, yarı taban ve taban",
        tarimsal=(
            "Alternatif gelişme, geç başaklanma. Soğuğa ve kurağa dayanıklı, "
            "su kullanım etkinliği ve gübreye tepkisi yüksek, yatmaya dayanıklı. "
            "Alveograf enerjisi 301–456 J — çok güçlü ekmeklik kalitesi."
        ),
        kaynak="TARM Çeşit Kataloğu 2025",
        uyumluluk_skoru=4,
        uyumluluk_not=(
            "En yüksek protein oranlarından biri (%15-16). "
            "Ekmeklik kalite ve güçlü gluten arıyorsanız ideal. "
            "Geç başaklanma yağışlı yıllarda avantaj sağlar."
        ),
    ),
    # ── ŞANLI (TARM 2016) ────────────────────────────────────────────────
    VarietyInfo(
        name="ŞANLI",
        tescil="2016",
        verim_kuru="400–540",
        verim_sulu="600–750",
        protein="%12.4–16.8",
        hektolitre="77.4–82.2",
        kisa_dayaniklilik="Yüksek",
        kuraklik="Yüksek",
        sari_pas="Orta dayanıklı",
        tavsiye_bolge="İç Anadolu ve Geçit Kuşağı — taban ve yarı taban",
        tarimsal=(
            "Alternatif gelişme, orta erkenci. Soğuğa, kurağa ve yatmaya "
            "dayanıklı. Gübreye tepkisi yüksek, yüksek tane ve sap verimine sahip."
        ),
        kaynak="TARM Çeşit Kataloğu 2025",
        uyumluluk_skoru=4,
        uyumluluk_not=(
            "Geniş verim bandı ve yüksek hektolitre. Taban/yarı taban alanlar için "
            "daha iyi; Bala kıraç bölgelerde orta öncelik."
        ),
    ),
    # ── AYTEN ABLA (TARM 2019) ────────────────────────────────────────────
    VarietyInfo(
        name="AYTEN ABLA",
        tescil="2019",
        verim_kuru="300–450",
        verim_sulu="600–750",
        protein="%12.3–16.4",
        hektolitre="76.1–80.7",
        kisa_dayaniklilik="Yüksek",
        kuraklik="Yüksek",
        sari_pas="Orta dayanıklı",
        tavsiye_bolge="Orta Anadolu ve Geçit Kuşağı — kıraç, yarı taban ve taban",
        tarimsal=(
            "Orta erkenci. Soğuğa ve kurağa dayanıklı, kardeşlenmesi yüksek, "
            "yatmaya dayanıklı, tane dökmeyen."
        ),
        kaynak="TARM Çeşit Kataloğu 2025",
        uyumluluk_skoru=4,
        uyumluluk_not=(
            "Orta Anadolu kıraç için tescilli. Alveograf enerjisi 167–280 J, "
            "orta-iyi ekmeklik kalitesi."
        ),
    ),
    # ── ÇAVUŞ (TARM 2019) ─────────────────────────────────────────────────
    VarietyInfo(
        name="ÇAVUŞ",
        tescil="2019",
        verim_kuru="280–450",
        verim_sulu="450–650",
        protein="%14.0–16.8",
        hektolitre="75.8–79.6",
        kisa_dayaniklilik="Yüksek",
        kuraklik="Yüksek",
        sari_pas="Toleranslı",
        tavsiye_bolge="Orta Anadolu ve Geçit Kuşağı — kıraç, yarı taban ve taban",
        tarimsal=(
            "Soğuğa ve kurağa dayanıklı, kardeşlenmesi yüksek, yatmaya dayanıklı. "
            "1. sınıf sert kaliteli. Alveograf enerjisi 300–538 J — çok güçlü gluten."
        ),
        kaynak="TARM Çeşit Kataloğu 2025",
        uyumluluk_skoru=4,
        uyumluluk_not=(
            "En güçlü gluten kalitelerinden biri (W: 300-538 J). "
            "Yüksek protein ve sert tane. Kuru verim Bayram'dan biraz düşük."
        ),
    ),
    # ── DEMİRHAN (TARM 2019) ──────────────────────────────────────────────
    VarietyInfo(
        name="DEMİRHAN",
        tescil="2019",
        verim_kuru="250–380",
        verim_sulu="400–500",
        protein="%14.3–15.8",
        hektolitre="75.6–79.5",
        kisa_dayaniklilik="Yüksek",
        kuraklik="Yüksek",
        sari_pas="Dayanıklı",
        tavsiye_bolge="Orta Anadolu ve Geçit Kuşağı — kıraç, yarı taban ve taban",
        tarimsal=(
            "Alternatif gelişme, orta erkenci. Soğuğa ve kurağa dayanıklı, "
            "su kullanım etkinliği yüksek, yatmaya dayanıklı."
        ),
        kaynak="TARM Çeşit Kataloğu 2025",
        uyumluluk_skoru=3,
        uyumluluk_not=(
            "Sarı pasa dayanıklı (diğerleri toleranslı/orta). "
            "Verim diğerlerine göre daha düşük. Hastalık baskısı yüksek yıllarda öne çıkar."
        ),
    ),
    # ── AYAZ (TARM 2020) ──────────────────────────────────────────────────
    VarietyInfo(
        name="AYAZ",
        tescil="2020",
        verim_kuru="300–400",
        verim_sulu="450–550",
        protein="%15–16.2",
        hektolitre="69.9–76.1",
        kisa_dayaniklilik="Yüksek",
        kuraklik="Yüksek",
        sari_pas="Toleranslı",
        tavsiye_bolge="Orta Anadolu ve Geçit Kuşağı — kıraç, yarı taban ve taban",
        tarimsal=(
            "Orta geç. Soğuğa ve kurağa dayanıklı, kardeşlenmesi yüksek, "
            "yatmaya dayanıklı, tane dökmeyen."
        ),
        kaynak="TARM Çeşit Kataloğu 2025",
        uyumluluk_skoru=3,
        uyumluluk_not=(
            "Yüksek protein (%15-16.2) ancak hektolitre görece düşük. "
            "Verim potansiyeli orta — kalite öncelikli parseller için düşünülebilir."
        ),
    ),
    # ── ERBAŞ (TARM 2021) ─────────────────────────────────────────────────
    VarietyInfo(
        name="ERBAŞ",
        tescil="2021",
        verim_kuru="250–450",
        verim_sulu="500–700",
        protein="%15.4–16.6",
        hektolitre="72.1–80.3",
        kisa_dayaniklilik="Yüksek",
        kuraklik="Yüksek",
        sari_pas="Orta hassas",
        tavsiye_bolge="Orta Anadolu ve Geçit Kuşağı — kıraç, yarı taban ve taban",
        tarimsal=(
            "Alternatif gelişme, erkenci. Soğuğa ve kurağa dayanıklı, "
            "su kullanım etkinliği ve gübreye tepkisi yüksek, yatmaya dayanıklı. "
            "Kırmızı taneli."
        ),
        kaynak="TARM Çeşit Kataloğu 2025",
        uyumluluk_skoru=3,
        uyumluluk_not=(
            "Sarı pasa orta hassas — ilaçlama gerekebilir. "
            "Kuru verim bandı geniş (250-450), ortalama yıllarda 350 civarı beklenir."
        ),
    ),
    # ── KARACAKURT (TARM 2022) ────────────────────────────────────────────
    VarietyInfo(
        name="KARACAKURT",
        tescil="2022",
        verim_kuru="300–450",
        verim_sulu="500–700",
        protein="%15.0–15.9",
        hektolitre="80.1–82.0",
        kisa_dayaniklilik="Yüksek",
        kuraklik="Yüksek",
        sari_pas="Orta dayanıklı",
        tavsiye_bolge="Orta Anadolu ve Geçit Kuşağı — kıraç, yarı taban ve taban",
        tarimsal=(
            "Alternatif gelişme, orta erkenci. Soğuğa ve kurağa dayanıklı, "
            "su kullanım etkinliği ve gübreye tepkisi yüksek, yatmaya dayanıklı."
        ),
        kaynak="TARM Çeşit Kataloğu 2025",
        uyumluluk_skoru=4,
        uyumluluk_not=(
            "En yüksek hektolitre ağırlığı (80-82 kg/hl). "
            "2022 tescilli — yeni ve modern çeşit. Yüksek protein + yüksek hektolitre kombinasyonu güçlü."
        ),
    ),
    # ── BALKIR (TARM 2022) ────────────────────────────────────────────────
    VarietyInfo(
        name="BALKIR",
        tescil="2022",
        verim_kuru="250–450",
        verim_sulu="500–600",
        protein="%14.6–14.7",
        hektolitre="76.4–77.5",
        kisa_dayaniklilik="Yüksek",
        kuraklik="Yüksek",
        sari_pas="Orta dayanıklı",
        tavsiye_bolge="Orta Anadolu ve Geçit Kuşağı — kıraç, yarı taban ve taban",
        tarimsal=(
            "Alternatif gelişme, orta erkenci. Soğuğa ve kurağa dayanıklı, "
            "su kullanım etkinliği ve gübreye tepkisi yüksek, yatmaya dayanıklı."
        ),
        kaynak="TARM Çeşit Kataloğu 2025",
        uyumluluk_skoru=3,
        uyumluluk_not=(
            "2022 tescilli, modern çeşit. Orta verim bandı, dengeli protein. "
            "Karacakurt ile aynı yıl — Karacakurt hektolitresi daha yüksek."
        ),
    ),
    # ── DEMİR-2000 (TARM 2000) ────────────────────────────────────────────
    VarietyInfo(
        name="DEMİR-2000",
        tescil="2000",
        verim_kuru="350–400",
        verim_sulu="500–600",
        protein="%10–17.5",
        hektolitre="73.4–81.8",
        kisa_dayaniklilik="Yüksek",
        kuraklik="Yüksek",
        sari_pas="Orta hassas",
        tavsiye_bolge="İç Anadolu ve Geçit Kuşağı — yarı taban ve taban",
        tarimsal=(
            "Alternatif gelişme, orta geç. Soğuğa, kurağa ve yatmaya "
            "dayanıklı. Gübreye tepkisi yüksek. Kırmızı sert taneli."
        ),
        kaynak="TARM Çeşit Kataloğu 2025",
        uyumluluk_skoru=3,
        uyumluluk_not=(
            "Kanıtlanmış çeşit (25 yıllık). Sarı pasa orta hassas — "
            "Bala'da hastalık baskısı varsa ilaçlama gerekir. Taban için daha uygun."
        ),
    ),
    # ── TOSUNBEY (TARM 2004) ─────────────────────────────────────────────
    VarietyInfo(
        name="TOSUNBEY",
        tescil="2004",
        verim_kuru="300–400",
        verim_sulu="450–600",
        protein="%12–16.5",
        hektolitre="70.9–81",
        kisa_dayaniklilik="Yüksek",
        kuraklik="Yüksek",
        sari_pas="Orta hassas",
        tavsiye_bolge="İç Anadolu ve Geçit Kuşağı — yarı taban ve taban",
        tarimsal=(
            "Alternatif gelişme, soğuğa, kurağa ve yatmaya dayanıklı. "
            "1. sınıf ekmeklik kalitesi. 25 Ekim–25 Kasım ekim zamanı."
        ),
        kaynak="TARM Çeşit Kataloğu 2025",
        uyumluluk_skoru=3,
        uyumluluk_not=(
            "Uzun yıllardır İç Anadolu'da yaygın kullanılan güvenilir çeşit. "
            "Sarı pasa orta hassas, ilaçlama önerilir. Ekim zamanı biraz geç (25 Eki–25 Kas)."
        ),
    ),
    # ── BAYRAKTAR-2000 (TARM 2000) ────────────────────────────────────────
    VarietyInfo(
        name="BAYRAKTAR-2000",
        tescil="2000",
        verim_kuru="350–400",
        verim_sulu="—",
        protein="%10–14.5",
        hektolitre="70.4–81.8",
        kisa_dayaniklilik="Yüksek",
        kuraklik="Yüksek",
        sari_pas="Toleranslı",
        tavsiye_bolge="İç Anadolu ve Geçit Kuşağı — marjinal, kıraç ve yarı taban",
        tarimsal=(
            "Kışlık, erkenci. Erkencilik nedeniyle ilkbaharda gelen kuraklıktan "
            "az etkilenir. Yatmaya dayanıklı, harman kalitesi iyi."
        ),
        kaynak="TARM Kataloğu 2025 + 2014",
        uyumluluk_skoru=3,
        uyumluluk_not=(
            "Erkenci olması kıraç Bala için avantaj (don risksiz dolgunlaşır). "
            "Protein oranı düşük (%10-14.5). Sürme/rastık için tohum ilaçlaması zorunlu."
        ),
    ),
    # ── GÜN-91 (TARM 1991) — 2014 kataloğu ──────────────────────────────────
    VarietyInfo(
        name="GÜN-91",
        tescil="1991",
        verim_kuru="350–400",
        verim_sulu="—",
        protein="—",
        hektolitre="76–79",
        kisa_dayaniklilik="Yüksek",
        kuraklik="Yüksek",
        sari_pas="Hassas",
        tavsiye_bolge="İç Anadolu ve Geçit Kuşağı — yarı taban ve taban",
        tarimsal=(
            "Alternatif gelişme, kışlık. Soğuğa, kışa ve kurağa dayanıklı, "
            "kardeşlenmesi yüksek, gübreye tepkisi iyi, yatma görülmeyen, "
            "harman kalitesi iyi. Alveograf W 220–300, sedimantasyon 35–40."
        ),
        kaynak="TARM Çeşit Kataloğu 2014",
        uyumluluk_skoru=3,
        uyumluluk_not=(
            "30+ yıllık kanıtlanmış çeşit. Sarı pasa hassas — Bala'da "
            "tohum ilaçlaması ve gerektiğinde fungisit zorunlu. "
            "Yeni nesil çeşitler (Bayram, Selamibey) verim açısından üstün."
        ),
    ),
    # ── İKİZCE-96 (TARM 1996) — 2014 kataloğu ───────────────────────────────
    VarietyInfo(
        name="İKİZCE-96",
        tescil="1996",
        verim_kuru="300–350",
        verim_sulu="—",
        protein="%12–14",
        hektolitre="79–81",
        kisa_dayaniklilik="Çok Yüksek",
        kuraklik="Yüksek",
        sari_pas="Hassas",
        tavsiye_bolge="İç Anadolu — yüksek rakım, soğuğun problem olduğu kıraç/yarı taban",
        tarimsal=(
            "Alternatif gelişme. Soğuğa ve kışa karşı İç Anadolu çeşitlerinden "
            "daha dayanıklı. Gübreye tepkisi yüksek, tane dökmeyen, harman "
            "kalitesi iyi. Alveograf W 175–250, sedimantasyon 34–50."
        ),
        kaynak="TARM Çeşit Kataloğu 2014",
        uyumluluk_skoru=3,
        uyumluluk_not=(
            "Olağanüstü soğuğa dayanıklılık — şiddetli kış riski olan yıllarda "
            "güvenlik çeşidi. Sarı pasa hassas, ilaçlama gerektirir. "
            "Verim potansiyeli yeni çeşitlerin gerisinde."
        ),
    ),
    # ── LÜTFİBEY (TARM 2010) — 2014 kataloğu ────────────────────────────────
    VarietyInfo(
        name="LÜTFİBEY",
        tescil="2010",
        verim_kuru="300–350",
        verim_sulu="—",
        protein="—",
        hektolitre="77–80",
        kisa_dayaniklilik="Yüksek",
        kuraklik="Yüksek",
        sari_pas="Dayanıklı",
        tavsiye_bolge="İç Anadolu ve Geçit Kuşağı — kıraç ve yarı taban",
        tarimsal=(
            "Kışlık gelişme. İlkbahar gelişmesi çok iyi — yabancı otlarla "
            "rekabeti oldukça güçlü. Soğuğa, kışa ve kurağa dayanıklı, "
            "kardeşlenmesi yüksek, gübreye tepkisi iyi, yatma görülmeyen."
        ),
        kaynak="TARM Çeşit Kataloğu 2014",
        uyumluluk_skoru=3,
        uyumluluk_not=(
            "Sarı pasa dayanıklı — ilaç tasarrufu. İlkbahar rekabet gücü "
            "yabancı ot baskısı olan parseller için avantaj. "
            "Verim potansiyeli yeni nesil çeşitlerin altında."
        ),
    ),
    # ── KENANBEY (TARM 2009) — 2014 kataloğu ────────────────────────────────
    VarietyInfo(
        name="KENANBEY",
        tescil="2009",
        verim_kuru="350–400",
        verim_sulu="—",
        protein="%12–14",
        hektolitre="76–81",
        kisa_dayaniklilik="Yüksek",
        kuraklik="Yüksek",
        sari_pas="Dayanıklı",
        tavsiye_bolge="İç Anadolu ve Geçit Kuşağı — kıraç ve yarı taban",
        tarimsal=(
            "Alternatif gelişme, orta geç. Soğuk ve kurağa dayanıklı, su "
            "kullanım etkinliği ve gübreye reaksiyonu oldukça iyi, tane "
            "dökmeyen, harman kalitesi iyi. İç Anadolu'nun tamamına adapte."
        ),
        kaynak="TARM Çeşit Kataloğu 2014",
        uyumluluk_skoru=3,
        uyumluluk_not=(
            "Sarı pasa dayanıklı — ilaç tasarrufu sağlar. "
            "Su kullanım etkinliği kıraç için kritik avantaj. "
            "Verim potansiyeli yeni nesil çeşitlerin biraz gerisinde."
        ),
    ),
]

# ── Puan → renk ───────────────────────────────────────────────────────────────

_SCORE_COLOR = {
    5: "var(--ag-accent)",
    4: "#4a90d9",
    3: "var(--ag-amber)",
    2: "var(--ag-red)",
    1: "var(--ag-red)",
}

_SCORE_LABEL = {
    5: "⭐⭐⭐⭐⭐  Çok Uyumlu",
    4: "⭐⭐⭐⭐    Uyumlu",
    3: "⭐⭐⭐      Orta Uyumlu",
    2: "⭐⭐         Düşük Uyum",
    1: "⭐            Önerilmez",
}

_SCORE_TIP = (
    "Pilot tarlanın koşullarına (Bala/Ankara kıraç, killi-tınlı, İç Anadolu step iklimi) "
    "göre uyumluluk değerlendirmesi. TARM katalog verileri ve üretici teknik belgelerine dayanır."
)

# ── Render ─────────────────────────────────────────────────────────────────────

def render_variety_panel() -> None:
    """Ekmeklik buğday çeşit önerileri sekmesini çizer."""
    st.markdown(
        section_head("Ekmeklik Buğday Çeşit Önerileri — Bala/Ankara Kıraç"),
        unsafe_allow_html=True,
    )

    render_explainer(
        "Bu panel ne anlatıyor?",
        "Pilot tarlanızın koşullarına (Bala/Ankara, kıraç, killi-tınlı toprak, "
        "İç Anadolu step iklimi) göre <b>en uyumlu ekmeklik buğday çeşitlerini</b> "
        "karşılaştırır. Veriler <b>TARM Çeşit Kataloğu 2025</b> ve "
        "<b>TARM Çeşit Kataloğu 2014</b> (Tarla Bitkileri Merkez Araştırma Enstitüsü, Ankara) "
        "ile Tekcan Tohum üretici belgelerine dayanır. "
        "Uyumluluk skoru tarla şartlarınıza özgü değerlendirmedir; "
        "kesin çeşit seçimi için yerel tarım danışmanına da danışmanız önerilir.",
        icon="🌾",
        legend=(
            ("var(--ag-accent)", "⭐⭐⭐⭐⭐ Çok uyumlu"),
            ("#4a90d9", "⭐⭐⭐⭐ Uyumlu"),
            ("var(--ag-amber)", "⭐⭐⭐ Orta uyumlu"),
        ),
    )

    # Sıralama: uyumluluk skoru azalan, aynı skorda isim artan
    sorted_varieties = sorted(VARIETIES, key=lambda v: (-v.uyumluluk_skoru, v.name))

    # Tablo
    rows = ""
    for v in sorted_varieties:
        score_color = _SCORE_COLOR.get(v.uyumluluk_skoru, "inherit")
        score_label = _SCORE_LABEL.get(v.uyumluluk_skoru, "—")
        score_pill = (
            f"<span class='stage-pill has-tip' "
            f"data-tip=\"{tip_attr(v.uyumluluk_not)}\" "
            f"style='border:1px solid {score_color};color:{score_color};"
            f"white-space:nowrap'>{score_label}</span>"
        )
        tarimsal_tip = tip(v.tarimsal, v.name)
        kaynak_html = f"<span style='font-size:10px;opacity:0.5'>{v.kaynak}</span>"
        rows += (
            f"<tr>"
            f"  <td><b>{tarimsal_tip}</b>"
            f"      <div style='font-size:10px;opacity:0.4;margin-top:2px'>{v.tescil}</div></td>"
            f"  <td class='ref-ideal' style='white-space:nowrap'>{v.verim_kuru}</td>"
            f"  <td class='ref-ideal' style='white-space:nowrap'>{v.verim_sulu}</td>"
            f"  <td style='white-space:nowrap'>{v.protein}</td>"
            f"  <td style='white-space:nowrap'>{v.hektolitre}</td>"
            f"  <td style='white-space:nowrap'>{v.kisa_dayaniklilik}</td>"
            f"  <td style='white-space:nowrap'>{v.sari_pas}</td>"
            f"  <td>{score_pill}</td>"
            f"  <td class='ref-note'>{kaynak_html}<br>"
            f"      <span style='font-size:11px'>{v.tavsiye_bolge}</span></td>"
            f"</tr>"
        )

    st.markdown(
        "<table class='ref-table'><thead><tr>"
        + th("Çeşit (Tescil)", "Çeşit adı ve tescil yılı. Üzerine gelerek tarımsal özellikler.", "14%")
        + th("Kuru Verim (kg/da)", "Kıraç/yağışa dayalı koşullarda beklenen verim aralığı.", "10%")
        + th("Sulu Verim (kg/da)", "Destek sulama veya taban alan koşullarında verim.", "10%")
        + th("Protein (%)", "Tane protein oranı — ekmeklik kalite göstergesi.", "8%")
        + th("Hektolitre (kg/hl)", "Dane dolgunluğu ve ağırlık göstergesi.", "9%")
        + th("Kış/Soğuk", "Kışa ve soğuğa dayanıklılık.", "7%")
        + th("Sarı Pas", "Sarı pas hastalığına karşı direnç durumu.", "8%")
        + th("Uyumluluk", _SCORE_TIP, "14%")
        + th("Kaynak / Tavsiye Bölge", "Veri kaynağı ve tavsiye edilen bölge.", "20%")
        + f"</tr></thead><tbody>{rows}</tbody></table>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="ag-cap">'
        f'Toplam {len(VARIETIES)} ekmeklik buğday çeşidi · '
        f'Çok uyumlu: {sum(1 for v in VARIETIES if v.uyumluluk_skoru == 5)} · '
        f'Uyumlu: {sum(1 for v in VARIETIES if v.uyumluluk_skoru == 4)} · '
        f'Orta: {sum(1 for v in VARIETIES if v.uyumluluk_skoru == 3)}. '
        'Kaynak: TARM Çeşit Kataloğu 2025 · TARM Çeşit Kataloğu 2014 '
        '(TAGEM/Tarla Bitkileri Merkez Araştırma Enstitüsü, Ankara) '
        '+ Tekcan Tohum ürün sayfası (Hamza). '
        'Uyumluluk skoru Bala/Ankara kıraç şartlarına göre değerlendirilmiştir. '
        'Kesin çeşit seçimi için yerel tarım danışmanına başvurunuz.'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Detay kartları — yüksek uyumlu çeşitler ───────────────────────────
    st.markdown("<div style='margin-top:32px'></div>", unsafe_allow_html=True)
    st.markdown(
        section_head("Öne Çıkan Çeşitler — Bala Kıraç İçin Detaylı Değerlendirme"),
        unsafe_allow_html=True,
    )

    top5 = [v for v in sorted_varieties if v.uyumluluk_skoru >= 4]
    cols = st.columns(min(len(top5), 3))
    for i, v in enumerate(top5):
        col = cols[i % 3]
        score_color = _SCORE_COLOR.get(v.uyumluluk_skoru, "inherit")
        score_label = _SCORE_LABEL.get(v.uyumluluk_skoru, "—")
        col.markdown(
            f'<div class="ag-card" style="border-left:3px solid {score_color}">'
            f'  <div style="font-size:13px;font-weight:700;margin-bottom:4px">{v.name}</div>'
            f'  <div style="font-size:10px;opacity:0.5;margin-bottom:8px">'
            f'    {v.kaynak} · Tescil: {v.tescil}</div>'
            f'  <div style="font-size:11px;line-height:1.7">'
            f'    <b>Kuru verim:</b> {v.verim_kuru} kg/da<br>'
            f'    <b>Protein:</b> {v.protein}<br>'
            f'    <b>Hektolitre:</b> {v.hektolitre} kg/hl<br>'
            f'    <b>Sarı pas:</b> {v.sari_pas}'
            f'  </div>'
            f'  <div style="font-size:11px;margin-top:10px;padding-top:8px;'
            f'              border-top:1px solid var(--ag-line);opacity:0.75">'
            f'    {v.uyumluluk_not}'
            f'  </div>'
            f'  <div style="margin-top:8px">'
            f'    <span style="font-size:10px;color:{score_color};font-weight:600">'
            f'    {score_label}</span>'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True,
        )
