"""Indeks hesaplamalari icin ortak yardimcilar."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

# Sifira bolmeyi onlemek icin epsilon
EPS = 1e-10


def _normalized_difference(
    a: NDArray[np.float32], b: NDArray[np.float32]
) -> NDArray[np.float32]:
    """(a - b) / (a + b) normalize fark. Girdileri mutate etmez.

    NDVI ailesi indekslerin tamami bu formdadir.
    """
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    if a.shape != b.shape:
        raise ValueError(f"Bant shape uyusmuyor: {a.shape} vs {b.shape}")
    return (a - b) / (a + b + EPS)
