"""GeoTIFF raster okuma/yazma - rasterio sarmalayicisi.

Tum indeks ciktilari georef'li, sikistirilmis, float32 GeoTIFF olarak yazilir;
boylece zaman serisi analizi ve QGIS gibi araclarda dogrudan kullanilir.
"""

from __future__ import annotations

import io
from enum import Enum, auto
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from numpy.typing import NDArray


class RasterType(Enum):
    THERMAL = auto()   # tek bant, sıcaklık (°C veya K)
    RGB     = auto()   # 3 bant görünür spektrum
    UNKNOWN = auto()


def detect_raster_type(path_or_bytes: Path | str | bytes) -> RasterType:
    """Bant sayısı ve piksel aralığına bakarak dosya tipini tahmin eder."""
    src = _open_raster(path_or_bytes)
    try:
        count  = src.count
        sample = src.read(1).astype(np.float32)
        vmin, vmax = float(sample.min()), float(sample.max())
    finally:
        src.close()

    if count == 1:
        # Termal: genellikle 0–100 °C veya 270–330 K aralığında
        if (0 <= vmin and vmax <= 100) or (200 <= vmin and vmax <= 400):
            return RasterType.THERMAL
        return RasterType.UNKNOWN
    if count >= 3:
        return RasterType.RGB
    return RasterType.UNKNOWN


def _open_raster(source: Path | str | bytes) -> rasterio.DatasetReader:
    if isinstance(source, bytes):
        return rasterio.open(io.BytesIO(source))
    return rasterio.open(source)


def read_band(path: Path | str, band: int = 1) -> tuple[NDArray[np.float32], dict[str, Any]]:
    """Tek bant oku, float32 array ve rasterio profile dondur."""
    with rasterio.open(path) as src:
        arr = src.read(band).astype(np.float32)
        profile = dict(src.profile)
    return arr, profile


def read_band_bytes(data: bytes, band: int = 1) -> tuple[NDArray[np.float32], dict[str, Any]]:
    """Bytes verisinden tek bant oku (Streamlit uploader için)."""
    with rasterio.open(io.BytesIO(data)) as src:
        arr = src.read(band).astype(np.float32)
        profile = dict(src.profile)
    return arr, profile


def read_rgb(
    path: Path | str, normalize: bool = True
) -> tuple[NDArray[np.float32], NDArray[np.float32], NDArray[np.float32], dict[str, Any]]:
    """3 bantlı RGB ortomosaik oku."""
    with rasterio.open(path) as src:
        bands = src.read().astype(np.float32)
        profile = dict(src.profile)
    if bands.shape[0] < 3:
        raise ValueError(f"En az 3 bant bekleniyor, {bands.shape[0]} bulundu")
    if normalize:
        bands = bands / 255.0
    return bands[0], bands[1], bands[2], profile


def read_rgb_bytes(
    data: bytes, normalize: bool = True
) -> tuple[NDArray[np.float32], NDArray[np.float32], NDArray[np.float32], dict[str, Any]]:
    """Bytes verisinden 3 bantlı RGB oku."""
    with rasterio.open(io.BytesIO(data)) as src:
        bands = src.read().astype(np.float32)
        profile = dict(src.profile)
    if bands.shape[0] < 3:
        raise ValueError(f"En az 3 bant bekleniyor, {bands.shape[0]} bulundu")
    if normalize:
        bands = bands / 255.0
    return bands[0], bands[1], bands[2], profile


def normalize_to_display(
    arr: NDArray[np.float32],
    out_size: int = 64,
) -> NDArray[np.float32]:
    """Büyük raster'ı dashboard görüntüleme için küçült ve 0-1'e normalize et.

    Args:
        arr: Ham bant array'i.
        out_size: Çıktı kenar boyutu (piksel). Orijinal oran korunur.

    Returns:
        0–1 arasında normalize edilmiş, küçültülmüş float32 array.
    """
    from skimage.transform import resize  # type: ignore[import-untyped]

    h, w = arr.shape
    if h > out_size or w > out_size:
        scale = out_size / max(h, w)
        new_h, new_w = max(1, int(h * scale)), max(1, int(w * scale))
        arr = resize(arr, (new_h, new_w), anti_aliasing=True).astype(np.float32)

    lo, hi = arr.min(), arr.max()
    if hi - lo < 1e-9:
        return np.zeros_like(arr)
    return (arr - lo) / (hi - lo)


def write_single_band(
    array: NDArray[np.float32],
    path: Path | str,
    profile: dict[str, Any],
) -> None:
    """Tek bantlı float32 array'i sıkıştırılmış GeoTIFF olarak yaz."""
    out_profile = dict(profile)
    out_profile.update(dtype="float32", count=1, compress="deflate")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(path, "w", **out_profile) as dst:
        dst.write(np.asarray(array, dtype=np.float32), 1)
