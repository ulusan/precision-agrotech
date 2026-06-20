"""RGB-tabanli vejetasyon indeksleri (Belge Bolum 10.4 / 10.8).

Mevcut DJI Mavic 3 Enterprise yuksek cozunurluklu RGB uretir. Bu indeksler
NDVI kadar guclu olmasa da bitki ortusu ve klorofil hakkinda anlamli bilgi verir.

Girdiler R, G, B reflektans (0-1) float32 - genelde 0-255'ten /255 ile normalize.
"""

from __future__ import annotations

from typing import cast

import numpy as np
from numpy.typing import NDArray

from tarla_ai.core.math import EPS


def vari(
    r: NDArray[np.float32], g: NDArray[np.float32], b: NDArray[np.float32]
) -> NDArray[np.float32]:
    """VARI = (G - R) / (G + R - B). Atmosferik etkilere dayanikli, NDVI'ya en yakin.

    Visible Atmospherically Resistant Index.
    """
    r = np.asarray(r, dtype=np.float32)
    g = np.asarray(g, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    return cast("NDArray[np.float32]", (g - r) / (g + r - b + EPS))


def tgi(
    r: NDArray[np.float32], g: NDArray[np.float32], b: NDArray[np.float32]
) -> NDArray[np.float32]:
    """TGI = G - 0.39*R - 0.61*B. Triangular Greenness Index, klorofile duyarli."""
    r = np.asarray(r, dtype=np.float32)
    g = np.asarray(g, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    return cast("NDArray[np.float32]", g - 0.39 * r - 0.61 * b)


def exg(
    r: NDArray[np.float32], g: NDArray[np.float32], b: NDArray[np.float32]
) -> NDArray[np.float32]:
    """ExG = 2*G - R - B. Excess Green - basit ama etkili biyokutle gostergesi."""
    r = np.asarray(r, dtype=np.float32)
    g = np.asarray(g, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    return cast("NDArray[np.float32]", 2.0 * g - r - b)
