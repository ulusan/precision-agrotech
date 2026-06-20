"""Drone sahne analizi — GeoTIFF bytes → indeksler → DroneAnalysis DTO.

Gerçek donanım DJI Mavic 3 Enterprise yalnızca RGB + termal üretir; multispektral
(NIR) bant YOKTUR. Bu nedenle:
  - RGB GeoTIFF  → VARI / TGI / ExG (görünür-bant vejetasyon indeksleri)
  - Termal GeoTIFF → CWSI (su stresi)

NDVI/NDRE bu sahne analizinde HESAPLANMAZ; onlar NIR/red-edge gerektirir ve
Sentinel-2 verisinden ayrı bir akışta üretilir (Belge Bölüm 10.6).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from tarla_ai.core.raster import RasterType, detect_raster_type, read_band_bytes, read_rgb_bytes
from tarla_ai.drone.indices import cwsi, exg, tgi, vari
from tarla_ai.rules.thresholds import CWSI_STRESS_THRESHOLD


@dataclass(frozen=True)
class DroneAnalysis:
    """Drone sahne analizinin özet metrikleri.

    Alanlar yalnızca ilgili raster tipinde dolar; diğerleri None kalır
    (eksik veri = None, asla uydurma değer).
    """

    raster_type: str = "unknown"
    # RGB indeksleri (görünür bant — NDVI DEĞİL)
    vari_mean: float | None = None
    tgi_mean: float | None = None
    exg_mean: float | None = None
    # Termal
    cwsi_mean: float | None = None
    stress_ratio: float | None = None   # CWSI eşiği üstü piksel oranı 0–1


def analyze_scene(data: bytes) -> DroneAnalysis:
    """GeoTIFF bytes → DroneAnalysis.

    Termal tek-bant (°C) dosyası için CWSI ve stres oranı hesaplar.
    3-bant RGB dosyası için VARI/TGI/ExG ortalamalarını hesaplar.
    Tanınmayan dosya için sadece raster_type='unknown' döner.
    """
    rtype = detect_raster_type(data)

    if rtype == RasterType.THERMAL:
        band, _ = read_band_bytes(data)
        t_min, t_max = float(band.min()), float(band.max())
        # Homojen sahne (min≈max): anlamlı ıslak/kuru referans yok → CWSI hesaplanamaz.
        # Uydurma değer üretme; metrikleri None bırak (eksik veri = None ilkesi).
        if t_max - t_min < 1e-6:
            return DroneAnalysis(raster_type="thermal")
        cwsi_arr = cwsi(band, t_min, t_max)
        stress_ratio = float(np.mean(cwsi_arr > CWSI_STRESS_THRESHOLD))
        return DroneAnalysis(
            raster_type="thermal",
            cwsi_mean=float(np.mean(cwsi_arr)),
            stress_ratio=stress_ratio,
        )

    if rtype == RasterType.RGB:
        r, g, b, _ = read_rgb_bytes(data)
        return DroneAnalysis(
            raster_type="rgb",
            vari_mean=float(np.mean(vari(r, g, b))),
            tgi_mean=float(np.mean(tgi(r, g, b))),
            exg_mean=float(np.mean(exg(r, g, b))),
        )

    return DroneAnalysis(raster_type="unknown")
