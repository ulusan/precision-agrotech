"""Cok kaynakli birlesik stres maskeleri (Belge Bolum 10.8).

Termal (CWSI) ve RGB/multispektral vigor birlikte degerlendirilerek yanlis
pozitif azaltilir - "cift onayli stres bolgesi".
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def dual_confirmed_stress(
    cwsi_arr: NDArray[np.float32],
    vigor_arr: NDArray[np.float32],
    cwsi_threshold: float = 0.5,
    vigor_threshold: float = 0.1,
) -> NDArray[np.bool_]:
    """Yuksek su stresi (termal) VE dusuk bitki vigor (RGB/MS indeksi).

    Belge: stress_mask = (cwsi > 0.5) & (vari < 0.1)

    Iki bagimsiz fiziksel kaynak ayni bolgeyi isaret ettiginde stres onaylanir;
    bu, tek kaynaga gore yanlis pozitifi azaltir. Cikti ayni zamanda VRA
    recetesinin girdisidir (sulama onceligi + olasi gubre/ilac karari).

    Args:
        cwsi_arr: CWSI degerleri [0, 1].
        vigor_arr: Vejetasyon vigor indeksi (VARI, NDVI vb.).
        cwsi_threshold: Ustunde stres sayilan CWSI esigi.
        vigor_threshold: Altinda dusuk vigor sayilan esik.

    Returns:
        Bool maske - True = cift onayli stres bolgesi.
    """
    cwsi_arr = np.asarray(cwsi_arr, dtype=np.float32)
    vigor_arr = np.asarray(vigor_arr, dtype=np.float32)
    if cwsi_arr.shape != vigor_arr.shape:
        raise ValueError(
            f"Shape uyusmuyor: cwsi {cwsi_arr.shape} vs vigor {vigor_arr.shape}"
        )
    return (cwsi_arr > cwsi_threshold) & (vigor_arr < vigor_threshold)
