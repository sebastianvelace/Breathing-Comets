"""Long epoch lists must be split so the Horizons URI is never truncated."""

import numpy as np
from spxcore import ephem


def test_long_requests_are_chunked_in_order(monkeypatch):
    calls = []

    def fake(designation, jd):
        calls.append(len(jd))
        return np.column_stack([jd - 2460000.0, -jd])  # encodes each epoch so order is checkable

    monkeypatch.setattr(ephem, "_horizons_chunk", fake)
    mjd = np.linspace(60886, 60903, 181)
    result = ephem.horizons_positions("2025 N1", mjd)
    assert max(calls) <= ephem.HORIZONS_CHUNK and sum(calls) == 181 and len(calls) == 5
    assert result.shape == (181, 2)
    assert np.all(np.diff(result[:, 0]) > 0)


def test_short_requests_use_a_single_query(monkeypatch):
    calls = []
    monkeypatch.setattr(ephem, "_horizons_chunk", lambda d, jd: calls.append(len(jd)) or np.zeros((len(jd), 2)))
    ephem.horizons_positions("2025 N1", [60886.0, 60887.0])
    assert calls == [2]
