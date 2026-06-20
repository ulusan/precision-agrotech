"""analyze_scene testleri — bellekte gerçek GeoTIFF üretip işler.

Burada 'dummy değer' yoktur; rasterio ile gerçek formatlı raster üretilir ve
fonksiyonun gerçek I/O + indeks zinciriyle çalıştığı doğrulanır.
"""

from __future__ import annotations

import numpy as np
import rasterio
from rasterio.io import MemoryFile

from tarla_ai.drone.analysis import analyze_scene


def _geotiff_bytes(array: np.ndarray) -> bytes:
    """(bands, h, w) array'i geçerli GeoTIFF bytes'a çevirir."""
    count, height, width = array.shape
    profile = {
        "driver": "GTiff",
        "height": height,
        "width": width,
        "count": count,
        "dtype": "float32",
        "crs": "EPSG:4326",
        "transform": rasterio.transform.from_bounds(0, 0, 1, 1, width, height),
    }
    with MemoryFile() as mem:
        with mem.open(**profile) as dst:
            dst.write(array.astype(np.float32))
        return mem.read()


class TestThermalScene:
    def test_thermal_detected_and_cwsi_computed(self) -> None:
        # Tek bant, °C aralığında (0–100) → THERMAL olarak tanınmalı
        temps = np.array([[[20.0, 25.0], [30.0, 35.0]]], dtype=np.float32)
        result = analyze_scene(_geotiff_bytes(temps))
        assert result.raster_type == "thermal"
        assert result.cwsi_mean is not None
        assert result.stress_ratio is not None
        assert 0.0 <= result.stress_ratio <= 1.0
        # Termal sahnede RGB indeksleri hesaplanmamalı
        assert result.vari_mean is None

    def test_thermal_does_not_fabricate_ndvi(self) -> None:
        # Çeşitli sıcaklıklı (anlamlı dağılımlı) termal sahne
        temps = np.array([[[18.0, 22.0], [26.0, 31.0]]], dtype=np.float32)
        result = analyze_scene(_geotiff_bytes(temps))
        # NDVI/NDRE alanı DTO'da yok — uydurma metrik üretilmediğini garanti et
        assert not hasattr(result, "ndvi_mean")
        assert not hasattr(result, "ndre_mean")

    def test_homogeneous_thermal_does_not_crash(self) -> None:
        # Tüm pikseller eşit (ör. uniform yüzey): ıslak/kuru referans yok.
        # CWSI hesaplanamaz → çökme yerine cwsi_mean=None dönmeli.
        temps = np.full((1, 4, 4), 28.0, dtype=np.float32)
        result = analyze_scene(_geotiff_bytes(temps))
        assert result.raster_type == "thermal"
        assert result.cwsi_mean is None
        assert result.stress_ratio is None


class TestRgbScene:
    def test_rgb_detected_and_visible_indices_computed(self) -> None:
        # 3 bant → RGB. Yeşil baskın yaprak benzeri bir sahne.
        r = np.full((4, 4), 0.2, dtype=np.float32)
        g = np.full((4, 4), 0.6, dtype=np.float32)
        b = np.full((4, 4), 0.1, dtype=np.float32)
        result = analyze_scene(_geotiff_bytes(np.stack([r, g, b])))
        assert result.raster_type == "rgb"
        assert result.vari_mean is not None
        assert result.tgi_mean is not None
        assert result.exg_mean is not None
        # RGB sahnede termal metrikleri None kalmalı
        assert result.cwsi_mean is None
        assert result.stress_ratio is None

    def test_rgb_vari_sign_reasonable_for_green_canopy(self) -> None:
        # Yeşil > kırmızı olduğunda VARI pozitif olmalı (yeşillik göstergesi)
        r = np.full((4, 4), 0.2, dtype=np.float32)
        g = np.full((4, 4), 0.6, dtype=np.float32)
        b = np.full((4, 4), 0.1, dtype=np.float32)
        result = analyze_scene(_geotiff_bytes(np.stack([r, g, b])))
        assert result.vari_mean is not None and result.vari_mean > 0
