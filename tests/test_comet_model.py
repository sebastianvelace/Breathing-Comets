from pathlib import Path

import numpy as np
import pytest
from spxcore.comets import co2_profile, fit_co2_rate, haser_fraction


def test_haser_projected_fraction_and_band_normalization():
    fractions = [haser_fraction(x) for x in (.001, .01, .1, 1, 10, 60)]
    assert 0 < fractions[0] < fractions[-1] == 1
    assert np.all(np.diff(fractions) > 0)
    lam = np.linspace(4.0, 4.5, 10001)
    profile = co2_profile(lam, np.full_like(lam, .01), 100)
    assert np.trapezoid(profile, lam) == pytest.approx(1, abs=1e-5)


@pytest.mark.slow
def test_golden_3I_co2():
    """Actual August photometry must recover the published consistency range."""
    path = Path(__file__).parent.parent/'data/derived/comets/3I_aug2025_D5_skysub.csv'
    data = np.genfromtxt(path, delimiter=',', names=True, dtype=None, encoding='utf8')
    data = data[data['f3_jy'] != 0]
    fit = fit_co2_rate(data['lam_um'], data['bw_um'], data['f3_jy'], data['e3_jy'], data['r'], data['delta'])
    assert .94e27 <= fit.q <= 1.6e27
    assert fit.temperature_k == 100
    assert fit.extra_width_um == .005
    assert fit.chi2_red < 50
    assert fit.statistical_error > 0
