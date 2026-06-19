"""Sentetik veri ile pipeline'in ucan-ucuna calistigini gosterir.

Gercek drone/uydu verisi gelmeden once pipeline'i dogrulamak icin: sentetik bir
termal + RGB raster uretir, CWSI ve RGB indekslerini hesaplar, cift onayli stres
maskesini cikarir ve NDRE esigi ile bir gubreleme onerisi uretir.

Calistir:  uv run python scripts/01_synthetic_demo.py
"""

from __future__ import annotations

import numpy as np

from tarla_ai.indices import cwsi, dual_confirmed_stress, vari
from tarla_ai.rules import evaluate_ndre, evaluate_soil_ph


def main() -> None:
    rng = np.random.default_rng(42)
    shape = (64, 64)

    # --- Sentetik termal: sol yari iyi sulanmis (~19C), sag yari stresli (~31C) ---
    canopy = np.full(shape, 19.0, np.float32)
    canopy[:, 32:] = 31.0
    canopy += rng.normal(0, 0.5, shape).astype(np.float32)

    cwsi_arr = cwsi(canopy, t_wet=18.5, t_dry=32.0)
    print(f"CWSI  -> ort={cwsi_arr.mean():.3f}  (sol~0, sag~1 beklenir)")

    # --- Sentetik RGB: stresli sag tarafta vigor dusuk ---
    r = np.full(shape, 0.30, np.float32)
    g = np.full(shape, 0.45, np.float32)
    b = np.full(shape, 0.20, np.float32)
    g[:, 32:] = 0.32  # sag yari daha az yesil -> dusuk VARI
    vari_arr = vari(r, g, b)
    print(f"VARI  -> sol ort={vari_arr[:, :32].mean():.3f}  sag ort={vari_arr[:, 32:].mean():.3f}")

    # --- Cift onayli stres ---
    mask = dual_confirmed_stress(cwsi_arr, vari_arr)
    print(f"Cift onayli stres pikselleri: {int(mask.sum())} / {mask.size}")

    # --- Kural tabanli oneriler ---
    print("\n--- Kural tabanli oneriler ---")
    for ndre_val in (0.15, 0.35):
        print("  ", evaluate_ndre(ndre_val).message)
    for ph in (5.4, 6.8, 8.2):
        print("  ", evaluate_soil_ph(ph).message)


if __name__ == "__main__":
    main()
