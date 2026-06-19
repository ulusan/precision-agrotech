"""GeoTIFF raster okuma/yazma - rasterio sarmalayicisi.

Tum indeks ciktilari georef'li, sikistirilmis, float32 GeoTIFF olarak yazilir;
boylece zaman serisi analizi ve QGIS gibi araclarda dogrudan kullanilir.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from numpy.typing import NDArray


def read_band(path: Path | str, band: int = 1) -> tuple[NDArray[np.float32], dict[str, Any]]:
    """Tek bant oku, float32 array ve rasterio profile dondur.

    Args:
        path: GeoTIFF yolu.
        band: 1-tabanli bant indeksi.

    Returns:
        (array, profile) - profile yazma sirasinda yeniden kullanilir.
    """
    with rasterio.open(path) as src:
        arr = src.read(band).astype(np.float32)
        profile = dict(src.profile)
    return arr, profile


def read_rgb(
    path: Path | str, normalize: bool = True
) -> tuple[NDArray[np.float32], NDArray[np.float32], NDArray[np.float32], dict[str, Any]]:
    """3 bantli RGB ortomosaik oku.

    Args:
        path: 3 bantli GeoTIFF.
        normalize: True ise 0-255 -> 0-1 araligina boler.

    Returns:
        (R, G, B, profile)
    """
    with rasterio.open(path) as src:
        bands = src.read().astype(np.float32)
        profile = dict(src.profile)
    if bands.shape[0] < 3:
        raise ValueError(f"En az 3 bant bekleniyor, {bands.shape[0]} bulundu")
    if normalize:
        bands = bands / 255.0
    return bands[0], bands[1], bands[2], profile


def write_single_band(
    array: NDArray[np.float32],
    path: Path | str,
    profile: dict[str, Any],
) -> None:
    """Tek bantli float32 array'i sikistirilmis GeoTIFF olarak yaz.

    Profile, kaynak rasterdan alinip tek-bant float32'ye guncellenir; boylece
    CRS ve transform (georef) korunur.
    """
    out_profile = dict(profile)
    out_profile.update(dtype="float32", count=1, compress="deflate")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(path, "w", **out_profile) as dst:
        dst.write(np.asarray(array, dtype=np.float32), 1)
