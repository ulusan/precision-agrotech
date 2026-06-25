# tarla-ai

Ankara/Bala bölgesinde kışlık ekmeklik buğday yetiştiren pilot tarla için geliştirilmiş
hassas tarım karar destek sistemi.

Drone görüntüsü, toprak analizi, sulama suyu kalitesi ve hava durumu verilerini bir araya
getirerek tarlada ne zaman ne yapılması gerektiğini söyler. Veri yoksa uydurmaz — boş bırakır.

**Pilot tarla:** Bahçekaradalak köyü, Bala/Ankara — 39.51563 N, 33.21366 E
**Donanım:** DJI Mavic 3 Enterprise (RGB + termal) · Sentinel-2 uydu kapsaması

---

## Ne Yapar?

| Sekme | Ne gösterir |
|---|---|
| **Ne Yapmalı?** | Bugünden hasada kadar tarla yol haritası — ekim, gübreleme, sulama zamanlaması |
| **Hava** | Open-Meteo'dan çekilen pilot tarla hava verisi (canlı) |
| **Toprak** | Referans eşik tablosu + yüklenen PDF analizi yorumu |
| **Su** | Kuyu suyu kalitesi (pH 5.84, EC 2.90) FAO eşikleriyle |
| **Drone** | Yüklenen GeoTIFF'ten NDVI/NDRE/CWSI/termal indeksler |
| **Fenoloji** | BBCH takvimi, büyüme dönemi hesaplama |

Tüm eşikler Bala/Haymana bölgesi saha verisiyle kalibre edilmiştir
(`docs/references/INDEX.md`).

---

## Kurulum

### Gereksinimler

- Python 3.11+
- [uv](https://astral.sh/uv) paket yöneticisi

### 1. Repoyu klonla

```bash
git clone <repo-url>
cd precision-agrotech
```

### 2. Bağımlılıkları kur

```bash
uv sync
```

> GDAL/PROJ sistem kütüphaneleri yoksa `uv sync` takılabilir.
> Bu durumda Docker'a geç — aşağıya bak.

### 3. Kendi analiz dosyalarını yerleştir

Repo'da sadece klasör iskeleti gelir; kişisel analiz dosyaları git'e girmez.

```
data/uploads/
├── soil/     ← toprak analizi PDF'ini buraya koy
├── water/    ← su analizi PDF'ini buraya koy  (su-analiz.pdf zaten burada)
└── drone/    ← drone GeoTIFF'ini buraya koy
```

> `data/uploads/water/su-analiz.pdf` pilot tarlanın kuyu suyu analizidir
> (Ankara Üniv. Ziraat Fak., Rapor TAR-2024-0004). Bu dosya git'e girmez,
> yerel olarak saklanır.

### 4. Testleri çalıştır

```bash
uv run pytest
```

Tüm testler geçiyorsa kurulum tamamdır.

### 5. Dashboard'u başlat

```bash
uv run streamlit run app.py
```

Tarayıcıda `http://localhost:8501` açılır.

---

## Docker (GDAL sorunu varsa)

```bash
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml up
```

---

## CLI — Drone Pipeline

Drone GeoTIFF'lerini `data/uploads/drone/` altına koy, sonra:

```bash
# RGB → VARI / TGI / ExG indeksleri
uv run tarla rgb-indices data/uploads/drone/rgb.tif --out-dir data/processed

# Termal → CWSI su stresi haritası
uv run tarla cwsi data/uploads/drone/thermal.tif \
    --t-wet 18.5 --t-dry 32.0 \
    --out data/processed/cwsi.tif
```

---

## Proje Yapısı

```
precision-agrotech/
│
├── app.py                        # Streamlit giriş noktası
│
├── src/tarla_ai/                 # Ana paket
│   ├── config.py                 # Tüm dizin yolları tek yerden (Settings)
│   │
│   ├── core/                     # Domain'den bağımsız yardımcılar
│   │   ├── errors.py
│   │   ├── math.py
│   │   └── raster.py             # GeoTIFF oku/yaz
│   │
│   ├── soil/                     # Toprak analizi
│   │   ├── reference.py          # Eşikler — Bala/Haymana kalibreli
│   │   ├── parsing.py            # PDF → SoilReport
│   │   ├── analysis.py           # SoilReport → yorumlanmış sonuç
│   │   └── validation.py
│   │
│   ├── water/                    # Sulama suyu
│   │   ├── reference.py          # FAO eşikleri + kuyu suyu kaydı
│   │   ├── parsing.py            # PDF → WaterReport
│   │   ├── analysis.py
│   │   └── validation.py
│   │
│   ├── drone/                    # Drone görüntü analizi
│   │   ├── analysis.py
│   │   └── indices/              # NDVI, NDRE, VARI, TGI, CWSI, stress
│   │
│   ├── climate/                  # Hava verisi (Open-Meteo)
│   │   ├── client.py
│   │   ├── models.py
│   │   ├── analysis.py
│   │   ├── charts.py
│   │   ├── labels.py
│   │   └── reference.py          # Pilot tarla koordinatı
│   │
│   ├── agronomy/                 # BBCH fenoloji + büyüme dönemleri
│   │
│   ├── advisory/                 # Karar destek motoru
│   │   ├── models.py             # OperationAdvice veri modeli
│   │   └── engine.py             # Tüm domainleri birleştirir
│   │
│   ├── rules/                    # Kural tabanlı eşikler (NDRE, CWSI, pH)
│   │
│   └── ui/                       # Streamlit arayüzü
│       ├── app.py                # Sekme düzeni
│       ├── theme.py / html.py
│       └── components/           # Her sekme için ayrı bileşen
│
├── tests/                        # 70+ pytest testi
│
├── data/
│   ├── uploads/                  # Kişisel analiz dosyaları (git'e girmez)
│   │   ├── soil/                 # Toprak analizi PDF
│   │   ├── water/                # Su analizi PDF  ← su-analiz.pdf burada
│   │   └── drone/                # Drone GeoTIFF
│   └── processed/                # CLI çıktıları (git'e girmez)
│
├── docs/
│   └── references/               # Bilimsel kaynak belgeler (git'e girer)
│       ├── INDEX.md              # Hangi PDF ne için, kodda nerede
│       ├── Toprak_Analizleri_ve_Yorumlanmasi.pdf
│       ├── Toprak Uygulama.pdf
│       ├── Ankara_Universitesi_Ziraat_Fakultesi_Haymana_Arast.pdf
│       └── ulusan-agrotech-solutions.pdf
│
├── docker/
├── pyproject.toml
└── uv.lock                       # Commit edilir — sürüm kilidi
```

### Domain Örüntüsü

Her domain aynı yapıyı izler:

```
domain/
├── reference.py   # eşikler ve sabitler — dış bağımlılık yok
├── parsing.py     # ham veri (PDF/bytes/API) → DTO
├── analysis.py    # DTO → yorumlanmış sonuç
└── validation.py  # giriş doğrulama
```

`advisory/engine.py` tüm domain çıktılarını birleştirip `OperationAdvice` listesi üretir.
`ui/` sadece gösterir — iş mantığı içermez.

### Temel İlkeler

- **Uydurma yasağı:** ölçülmeyen parametre `None` döner, asla tahmin üretilmez
- **Saf fonksiyonlar:** indeks hesaplamaları girdiyi mutate etmez, yeni nesne döndürür
- **Tek kaynak:** tüm dizin yolları `config.py`'den, tüm eşikler `*/reference.py`'den

---

## Yol Haritası

| Faz | Kapsam |
|---|---|
| **0–1** *(şu an)* | Veri pipeline + kural tabanlı karar destek |
| 2 | Klasik ML — verim tahmini (xgboost, scikit-learn) |
| 3 | DL — segmentasyon + production API (pytorch, fastapi) |
| 4 | Spatiotemporal + "öğrenen tarla" (xarray, zarr) |
