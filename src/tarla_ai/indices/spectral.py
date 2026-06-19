"""Multispektral vejetatif indeksler (Sentinel-2 veya multispektral drone bantlari).

Belge Bolum 9.2'deki indeks tablosuna karsilik gelir. Mevcut DJI Mavic 3 Enterprise
multispektral uretmez; bu indeksler Sentinel-2 verisinden hesaplanir (Bolum 10.6).

Bant adlandirma: red, nir, red_edge (RE), green - hepsi reflektans (0-1) float32.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from tarla_ai.indices._common import _normalized_difference


def ndvi(nir: NDArray[np.float32], red: NDArray[np.float32]) -> NDArray[np.float32]:
    """NDVI = (NIR - Red) / (NIR + Red). Ortu yogunlugu, verim haritasi tabani.

    Kritik donem: tum donemler.
    """
    return _normalized_difference(nir, red)


def ndre(
    nir: NDArray[np.float32], red_edge: NDArray[np.float32]
) -> NDArray[np.float32]:
    """NDRE = (NIR - RE) / (NIR + RE). Azot stres haritasi, VRA girdisi.

    Kritik donem: BBCH 30-39 (sapa kalkma). Azot durumunu NDVI'dan 1-2 hafta
    once ortaya koyar.
    """
    return _normalized_difference(nir, red_edge)


def gndvi(
    nir: NDArray[np.float32], green: NDArray[np.float32]
) -> NDArray[np.float32]:
    """GNDVI = (NIR - Green) / (NIR + Green). Klorofil icerigi haritasi.

    Kritik donem: kardeslenme ve sonrasi.
    """
    return _normalized_difference(nir, green)


def lci(
    nir: NDArray[np.float32],
    red_edge: NDArray[np.float32],
    red: NDArray[np.float32],
) -> NDArray[np.float32]:
    """LCI = (NIR - RE) / (NIR + Red). Yaprak klorofil, hastalik uyarisi.

    Kritik donem: BBCH 37-39 (bayrak yaprak).
    """
    nir = np.asarray(nir, dtype=np.float32)
    red_edge = np.asarray(red_edge, dtype=np.float32)
    red = np.asarray(red, dtype=np.float32)
    from tarla_ai.indices._common import EPS

    return (nir - red_edge) / (nir + red + EPS)
