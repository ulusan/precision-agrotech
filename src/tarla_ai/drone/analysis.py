"""Drone sahne analizi — GeoTIFF bytes → indeksler → DroneAnalysis DTO."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from tarla_ai.core.raster import RasterType, detect_raster_type, read_band_bytes, read_rgb_bytes
from tarla_ai.drone.indices import cwsi, dual_confirmed_stress, ndre, ndvi, vari
from tarla_ai.rules.thresholds import CWSI_STRESS_THRESHOLD, NITROGEN_NDRE_THRESHOLD


@dataclass(frozen=True)
class DroneAnalysis:
    """Drone sahne analizinin özet metrikleri."""

    ndvi_mean: float | None = None
    ndre_mean: float | None = None
    cwsi_mean: float | None = None
    stress_ratio: float | None = None   # stresli piksel oranı 0–1
    raster_type: str = "unknown"


def analyze_scene(data: bytes) -> DroneAnalysis:
    """GeoTIFF bytes → DroneAnalysis.

    Termal tek-bant dosyası için CWSI hesaplar.
    3-bant RGB dosyası için NDVI/NDRE/stres maskesi hesaplar.
    """
    rtype = detect_raster_type(data)

    if rtype == RasterType.THERMAL:
        band, _ = read_band_bytes(data)
        t_min, t_max = float(band.min()), float(band.max())
        cwsi_arr = cwsi(band, t_min, t_max)
        return DroneAnalysis(
            cwsi_mean=float(np.mean(cwsi_arr)),
            raster_type="thermal",
        )

    if rtype == RasterType.RGB:
        r, g, b, _ = read_rgb_bytes(data)
        ndvi_arr = ndvi(r, b)   # RGB'de yakın kızılötesi yok; NDVI yerine kırmızı-mavi fark
        vari_arr = vari(r, g, b)
        return DroneAnalysis(
            ndvi_mean=float(np.mean(ndvi_arr)),
            raster_type="rgb",
        )

    return DroneAnalysis(raster_type="unknown")
