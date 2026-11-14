"""Pinned-client regression against a retained, actual Horizons JD response."""

import numpy as np
import pytest
from spxcore import ephem
from spxcore.config import ROOT


def test_raw_jd_csv_matches_actual_response():
    text = (ROOT / "data/validation/horizons-3i-jd.txt").read_text()
    positions = ephem.parse_horizons_positions(text, [2461359.200525472])
    np.testing.assert_allclose(positions, [[106.029347905, 19.303506284]], atol=1e-9)
    with pytest.raises(ValueError, match="epoch mismatch"):
        ephem.parse_horizons_positions(text, [2461359.3])


@pytest.mark.network
def test_live_spacecraft_jd_ephemeris():
    position = ephem.horizons_positions("3I", [2461359.200525472-2400000.5])
    np.testing.assert_allclose(position, [[106.029347905, 19.303506284]], atol=1e-7)
