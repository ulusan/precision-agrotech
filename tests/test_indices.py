"""Indeks fonksiyonlari testleri - saf, deterministik, bilinen degerlerle."""

from __future__ import annotations

import numpy as np
import pytest

from tarla_ai.indices import cwsi, dual_confirmed_stress, exg, gndvi, lci, ndre, ndvi, tgi, vari


class TestSpectral:
    def test_ndvi_known_value(self) -> None:
        # NIR=0.8, Red=0.2 -> (0.6)/(1.0) = 0.6
        result = ndvi(np.array([0.8], np.float32), np.array([0.2], np.float32))
        assert result[0] == pytest.approx(0.6, abs=1e-5)

    def test_ndvi_does_not_mutate_input(self) -> None:
        nir = np.array([0.8, 0.5], np.float32)
        red = np.array([0.2, 0.5], np.float32)
        nir_copy, red_copy = nir.copy(), red.copy()
        ndvi(nir, red)
        np.testing.assert_array_equal(nir, nir_copy)
        np.testing.assert_array_equal(red, red_copy)

    def test_ndvi_zero_division_safe(self) -> None:
        # NIR=0, Red=0 -> EPS sayesinde NaN degil 0
        result = ndvi(np.array([0.0], np.float32), np.array([0.0], np.float32))
        assert not np.isnan(result[0])

    def test_ndre(self) -> None:
        result = ndre(np.array([0.7], np.float32), np.array([0.3], np.float32))
        assert result[0] == pytest.approx(0.4, abs=1e-5)

    def test_gndvi(self) -> None:
        result = gndvi(np.array([0.6], np.float32), np.array([0.4], np.float32))
        assert result[0] == pytest.approx(0.2, abs=1e-5)

    def test_lci(self) -> None:
        # (NIR - RE)/(NIR + Red) = (0.8-0.5)/(0.8+0.2) = 0.3
        result = lci(
            np.array([0.8], np.float32),
            np.array([0.5], np.float32),
            np.array([0.2], np.float32),
        )
        assert result[0] == pytest.approx(0.3, abs=1e-5)

    def test_shape_mismatch_raises(self) -> None:
        with pytest.raises(ValueError, match="shape"):
            ndvi(np.array([0.8, 0.5], np.float32), np.array([0.2], np.float32))


class TestRGB:
    def test_vari(self) -> None:
        # (G-R)/(G+R-B) = (0.5-0.3)/(0.5+0.3-0.2) = 0.2/0.6
        result = vari(
            np.array([0.3], np.float32),
            np.array([0.5], np.float32),
            np.array([0.2], np.float32),
        )
        assert result[0] == pytest.approx(0.2 / 0.6, abs=1e-4)

    def test_tgi(self) -> None:
        # G - 0.39*R - 0.61*B
        result = tgi(
            np.array([0.2], np.float32),
            np.array([0.5], np.float32),
            np.array([0.1], np.float32),
        )
        expected = 0.5 - 0.39 * 0.2 - 0.61 * 0.1
        assert result[0] == pytest.approx(expected, abs=1e-5)

    def test_exg(self) -> None:
        # 2*G - R - B
        result = exg(
            np.array([0.2], np.float32),
            np.array([0.5], np.float32),
            np.array([0.1], np.float32),
        )
        assert result[0] == pytest.approx(2 * 0.5 - 0.2 - 0.1, abs=1e-5)


class TestThermal:
    def test_cwsi_no_stress(self) -> None:
        # canopy == t_wet -> 0
        result = cwsi(np.array([18.5], np.float32), t_wet=18.5, t_dry=32.0)
        assert result[0] == pytest.approx(0.0, abs=1e-5)

    def test_cwsi_full_stress(self) -> None:
        # canopy == t_dry -> 1
        result = cwsi(np.array([32.0], np.float32), t_wet=18.5, t_dry=32.0)
        assert result[0] == pytest.approx(1.0, abs=1e-5)

    def test_cwsi_clips_above_one(self) -> None:
        result = cwsi(np.array([40.0], np.float32), t_wet=18.5, t_dry=32.0)
        assert result[0] == 1.0

    def test_cwsi_clips_below_zero(self) -> None:
        result = cwsi(np.array([10.0], np.float32), t_wet=18.5, t_dry=32.0)
        assert result[0] == 0.0

    def test_cwsi_invalid_range_raises(self) -> None:
        with pytest.raises(ValueError, match="t_dry"):
            cwsi(np.array([20.0], np.float32), t_wet=32.0, t_dry=18.5)


class TestStress:
    def test_dual_confirmed_both_conditions(self) -> None:
        # cwsi > 0.5 AND vari < 0.1 -> True
        cwsi_arr = np.array([0.6, 0.6, 0.3], np.float32)
        vigor = np.array([0.05, 0.5, 0.05], np.float32)
        mask = dual_confirmed_stress(cwsi_arr, vigor)
        np.testing.assert_array_equal(mask, [True, False, False])

    def test_dual_confirmed_shape_mismatch(self) -> None:
        with pytest.raises(ValueError, match="Shape"):
            dual_confirmed_stress(
                np.array([0.6], np.float32), np.array([0.05, 0.1], np.float32)
            )
