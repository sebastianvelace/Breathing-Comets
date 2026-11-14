"""Periodic comets need a unique Horizons record; the resolver must find one without guessing."""

import asyncio

import pytest
from spxcore import ephem, known


def test_candidates_for_periodic_and_non_periodic_comets():
    assert known.track_candidates({"des": "29P", "prefix": "P", "spkid": "1000079"}) == ["29P", "DES=29P; CAP", "1000079"]
    # a non-periodic comet keeps its plain designation first and adds no CAP form
    assert known.track_candidates({"des": "2025 N1", "prefix": "C", "spkid": "1004083"}) == ["2025 N1", "1004083"]
    assert known.track_candidates({"des": "2025 N1"}) == ["2025 N1"]


def test_first_resolving_identifier_wins(monkeypatch):
    seen = []

    def fake(designation, mjd):
        seen.append(designation)
        if designation != "DES=29P; CAP":
            raise ValueError("Horizons returned no ephemeris for this target and observer")
        return [[173.15, -2.74]]

    monkeypatch.setattr(ephem, "horizons_positions", fake)
    track, position = asyncio.run(known.first_working_track(["29P", "DES=29P; CAP", "1000079"], 61025.2))
    assert track == "DES=29P; CAP" and seen == ["29P", "DES=29P; CAP"] and position[0][0] == 173.15


def test_unavailable_service_is_not_swallowed(monkeypatch):
    def fake(designation, mjd):
        raise ephem.EphemerisUnavailable("Horizons is unavailable; retry later")

    monkeypatch.setattr(ephem, "horizons_positions", fake)
    with pytest.raises(ephem.EphemerisUnavailable):
        asyncio.run(known.first_working_track(["29P", "DES=29P; CAP"], 61025.2))


def test_all_unresolved_raises_a_clear_error(monkeypatch):
    def fake(designation, mjd):
        raise ValueError("no ephemeris")

    monkeypatch.setattr(ephem, "horizons_positions", fake)
    with pytest.raises(ValueError, match=r"no unique Horizons ephemeris \(tried 29P\)"):
        asyncio.run(known.first_working_track(["29P"], 61025.2))


def test_ambiguous_sbdb_answer_uses_only_an_exact_designation():
    matches = [{"pdes": "240P", "name": "240P/NEAT"}, {"pdes": "240P-B", "name": "240P/NEAT-B"}]
    assert known.pick_sbdb_match(matches, "240P") == "240P"
    assert known.pick_sbdb_match(matches, " 240p ") == "240P"
    with pytest.raises(ValueError, match="ambiguous: 240P/NEAT, 240P/NEAT-B"):
        known.pick_sbdb_match(matches, "240")
    with pytest.raises(ValueError, match="ambiguous"):
        known.pick_sbdb_match([{"pdes": "73P-B"}, {"pdes": "73P-C"}], "73P")
