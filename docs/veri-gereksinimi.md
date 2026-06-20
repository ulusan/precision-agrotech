# Veri Gereksinimi — Pilot Tarla (Ankara/Bala, Kıraç Ekmeklik Buğday)

> Bu doküman tek pilot tarla için **minimum veri sözleşmesidir**. Sistem referans/karar-destek
> üretir; **kesin karar vermez**. Hiçbir aşamada dummy/varsayılan/ortalama değerle boşluk
> doldurulmaz — **eksik veri = "veri yok"** olarak gösterilir.
>
> Kapsam: Ekim · Gübreleme · İlaçlama · Sulama · Hasat zamanı · Toprak sağlığı ·
> Drone'dan stres/hastalık/yabancı ot tespiti. **MVP dışı:** çoklu tarla, kullanıcı
> yönetimi, simülasyon, tahminsel senaryo.

## Gerçekçi doğruluk hedefi

"%100 doğruluk" tarımsal karar sistemlerinde mümkün değildir ve bu sistemin amacı da
değildir. Doğru hedef **"karar verilebilir kalitede, izlenebilir veri"**: her çıktı ham
veriye ve açık hesaba dayanır, eşikler literatürdendir ve saha ile kalibre edilmelidir.

---

## 1. Toprak Analizi — Alanlar

Kod ([src/tarla_ai/soil/parsing.py](../src/tarla_ai/soil/parsing.py)) 14 parametreyi
çıkarabiliyor; referans eşikleri [src/tarla_ai/soil/reference.py](../src/tarla_ai/soil/reference.py).

### Zorunlu (bunlar yoksa gübre/kireç kararı üretilemez)

| Parametre | Birim | Yöntem | Neden zorunlu |
|---|---|---|---|
| pH | — | 1:2.5 sulu | Besin alınabilirliğinin ana kapısı |
| Organik Madde | % | Walkley-Black | Azot mineralizasyon tabanı |
| Toplam Azot (N) | % | Kjeldahl | Azot programının temeli |
| Alınabilir Fosfor (P₂O₅) | kg/da | **Olsen** | Taban gübre dozu |
| Alınabilir Potasyum (K₂O) | kg/da | Amonyum asetat | K kararı |
| Kireç (CaCO₃) | % | Scheibler | Zn/Fe/P bağlanmasının ana nedeni |
| Çinko (Zn) | mg/kg | **DTPA** | Bölgede en yaygın eksiklik |

### Opsiyonel (varsa yorumlanır, yoksa o satır "veri yok")

EC/Tuzluluk (dS/m) · Kalsiyum (ppm) · Magnezyum (ppm) · Demir/DTPA · Bakır/DTPA ·
Mangan/DTPA · Bor (sıcak su) · CEC (me/100g) · Tekstür (kum/silt/kil %)

### Numune alma (zorunlu kural)
- **Derinlik:** 0–30 cm (buğday kök bölgesi), sabit.
- **Kompozit numune:** Parselde zikzak 15–20 alt-noktayı karıştır → tek numune.
- **Zaman:** Ekim öncesi.

---

## 2. Laboratuvar Sonucu — Format

| Kural | Değer |
|---|---|
| Birincil format | **Makine-okunur PDF** (metin katmanlı). Taranmış/görüntü PDF parse EDİLEMEZ. |
| Yöntem etiketi | Olsen / DTPA / amonyum asetat raporda açıkça yazmalı (eşikler buna bağlı). |
| Birim | Rapor birimi referans tablosuyla aynı olmalı: P/K → **kg/da**, mikro → **mg/kg**. |
| Ondalık ayraç | Virgül veya nokta — ikisi de okunur. |

> Kod birim dönüşümü yapmaz. Farklı birimdeki bir değer yanlış yorumlanır.

---

## 3–6. Drone Görüntüleri

**Gerçek donanım: DJI Mavic 3 Enterprise** = RGB + Termal (LWIR 8–14µm) + RTK.
**Multispektral (NIR) bant YOKTUR.**

| Soru | MVP cevabı |
|---|---|
| RGB yeterli mi / multispektral gerekli mi? | **RGB + Termal yeterli.** NDVI/NDRE multispektral drone yerine **Sentinel-2'den** alınır (ücretsiz, 5 gün revizit). Multispektral drone MVP'de **gereksiz**. |
| Çözünürlük (GSD) | Stres/yatma/genel: **~2–3 cm/px.** Yabancı ot / hastalık: **≤1.5 cm/px.** |
| Uçuş yüksekliği | Mavic 3E için ~2.5 cm/px ≈ **80–90 m AGL.** Sınır: ≤120 m. Tek değişken GSD'dir. |
| Dosya formatı | **Georeferanslı GeoTIFF (.tif/.tiff).** RGB = 3 bant; Termal = 1 bant, **°C.** |

### Kodun raster tipini tanıması
[src/tarla_ai/core/raster.py](../src/tarla_ai/core/raster.py) `detect_raster_type`:
- 1 bant + değer 0–100 (°C) veya 200–400 (K) → **THERMAL**
- 3+ bant → **RGB**
- Aksi → **UNKNOWN** (işlenmez)

> Termal dosya **kalibre °C** olarak export edilmeli. Ham 16-bit DN olursa UNKNOWN olur.

### Drone'dan üretilen metrikler (gerçek, uydurma yok)
- **RGB** → VARI, TGI, ExG (görünür-bant vejetasyon indeksleri). *NDVI değildir.*
- **Termal** → CWSI (su stresi) + stres oranı. Homojen sahnede (min≈max) CWSI hesaplanamaz → `None`.

### Uçuş SOP'u
- Saat: **10:00 öncesi veya 15:00 sonrası** (öğle gölge/yansıma gürültüsü).
- Her uçuşta **reflektans kalibrasyon plakası** + **RTK açık**.
- Örtüşme: ön **%80**, yan **%70**.

---

## 7. Tarla Sınırı
- **GeoJSON veya Shapefile**, tek poligon.
- CRS: **WGS84 (EPSG:4326)** — config varsayılanı.

---

## 8. Meteorolojik Veri
MVP için **zorunlu değil.** İsteğe bağlı zenginleştirme: günlük yağış + min/max sıcaklık +
(çiçeklenmede) nem. Tahmin/simülasyon kurulmaz.

---

## 9. Eksik Veri Davranışı (Hata Toleransı)

| Durum | Davranış |
|---|---|
| Toprak parametresi parse edilemedi | Tabloda **"veri yok"**, o parametre için karar üretilmez. |
| Zorunlu 7 alandan biri eksik | İlgili karar bloğu (ör. azot programı) **açılmaz**. |
| Drone dosyası UNKNOWN | İşlenmez; kullanıcıya **neden** söylenir (ör. "termal °C değil"). |
| Homojen/dejenere termal | Çökmez; CWSI = `None`. |
| Her durumda | **Dummy/varsayılan/ortalama ile boşluk DOLDURULMAZ.** |

---

## Özet — Pilot için minimum paket
1. Ekim öncesi toprak analizi PDF'i (7 zorunlu alan, Olsen + DTPA, makine-okunur).
2. Mavic 3E ile RGB + Termal(°C) GeoTIFF, ~2.5 cm/px, sabah/öğleden sonra, kalibrasyonlu.
3. Sentinel-2 (NDVI/NDRE için).
4. Tarla sınırı GeoJSON (WGS84).
