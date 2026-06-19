# tarla-ai

Yapay zeka destekli hassas tarim pilot projesi — bugday & arpa.
Donanim: **DJI Mavic 3 Enterprise** (RGB + termal LWIR + RTK) + **Sentinel-2** (multispektral kapsama).

> Bu repo, proje raporundaki (Ulusan AgroTech Solutions, 2026) pipeline ve karar
> destek mantiginin **Phase 0–1** iskeletidir. AI mantigi kameradan bagimsizdir;
> feature kaynaklari (drone/uydu) degisse de cekirdek ayni kalir.

## Hizli baslangic (macOS)

```bash
# 1) uv kur (henuz yoksa)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2) Bagimliliklari kur (uv Python 3.11'i kendisi indirir)
uv sync

# 3) Testleri calistir
uv run pytest

# 4) Sentetik uctan-uca demo
uv run python scripts/01_synthetic_demo.py
```

GDAL/PROJ sistem bagimliliklari yuzunden lokal `uv sync` takilirsa Docker'a gec:

```bash
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml run --rm tarla --help
```

## CLI

```bash
# Termal goruntuden su stresi (CWSI)
uv run tarla cwsi data/raw/thermal_2026-04-10.tif --t-wet 18.5 --t-dry 32.0 \
    --out data/processed/cwsi.tif

# RGB ortomosaikten vejetasyon indeksleri (VARI/TGI/ExG)
uv run tarla rgb-indices data/raw/rgb_orthomosaic.tif --out-dir data/processed
```

## Mimari

```
src/tarla_ai/
├── config.py        # Pydantic ayarlar + dizin yollari (tek kaynak)
├── io/raster.py     # GeoTIFF oku/yaz (rasterio sarmalayici, georef korur)
├── indices/
│   ├── spectral.py  # NDVI, NDRE, GNDVI, LCI  (Sentinel-2 / MS drone)
│   ├── rgb.py       # VARI, TGI, ExG          (Mavic 3 RGB)
│   ├── thermal.py   # CWSI su stresi          (Mavic 3 termal)
│   └── stress.py    # Cift onayli stres maskesi (termal + vigor)
├── rules/           # Kural tabanli karar motoru (Belge Bolum 5.1)
│   ├── thresholds.py
│   └── engine.py
└── cli.py
```

**Tasarim ilkesi:** indeks fonksiyonlari saf (girdiyi mutate etmez, yeni array
dondurur) ve deterministik — test edilebilir, pipeline'da guvenle zincirlenir.

## Yol haritasi (fazlar)

| Faz | Kapsam | Eklenecek |
|-----|--------|-----------|
| **0–1** *(bu repo)* | Veri pipeline + kural tabanli karar | rasterio, geopandas, pykrige |
| 2 | Klasik ML — verim tahmini | xgboost, scikit-learn, shap, optuna, duckdb, streamlit |
| 3 | DL — segmentasyon + production API | pytorch, segmentation-models-pytorch, fastapi, postgis |
| 4 | Spatiotemporal + "ogrenen tarla" | xarray, zarr, pytorch-lightning, celery, redis |

## Notlar

- **Esik degerleri** (`rules/thresholds.py`) literatur referansidir; saha
  kosullarina gore kalibre edilmeli (Belge son notu).
- **Reflektans kalibrasyonu** her drone ucusunda zorunlu — atlanirsa zaman serisi
  bozulur (Belge Bolum 9.5).
- `uv.lock` commit edilir (surum kilitleme); `data/` icerigi commit edilmez.
```
