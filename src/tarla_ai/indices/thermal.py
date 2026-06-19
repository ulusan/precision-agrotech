"""Termal sensor tabanli su stresi (Belge Bolum 10.3 / 10.8).

DJI Mavic 3 Enterprise'in 640x512 radyometrik LWIR sensoru ile dogrudan hesaplanir.
CWSI, su stresi izlemenin altin standardidir (Bolum 10.3).
"""

from __future__ import annotations

from typing import cast

import numpy as np
from numpy.typing import NDArray


def cwsi(
    canopy_temp: NDArray[np.float32],
    t_wet: float,
    t_dry: float,
) -> NDArray[np.float32]:
    """Crop Water Stress Index.

    CWSI = (T_canopy - T_wet) / (T_dry - T_wet), [0, 1] araligina kirpilir.
    0 = stres yok (iyi sulanmis), 1 = ciddi stres.

    Args:
        canopy_temp: Radyometrik termal goruntu, Celsius (orneklem: bitki ortusu).
        t_wet: Iyi sulanmis referans bolgenin yaprak sicakligi (alt sinir).
        t_dry: Stresli/kuru referans bolgenin yaprak sicakligi (ust sinir).

    Referans sicakliklar AYNI ucustaki iki ekstrem noktadan secilir; boylece
    gun/saat farki normalize edilir.

    Raises:
        ValueError: t_dry <= t_wet ise (gecersiz referans araligi).
    """
    if t_dry <= t_wet:
        raise ValueError(f"t_dry ({t_dry}) > t_wet ({t_wet}) olmali")
    canopy_temp = np.asarray(canopy_temp, dtype=np.float32)
    result = (canopy_temp - t_wet) / (t_dry - t_wet)
    return cast("NDArray[np.float32]", np.clip(result, 0.0, 1.0).astype(np.float32))
