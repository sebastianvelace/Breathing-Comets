"""Catalog outages must preserve DR3 identity and must not poison the cache."""

import asyncio
import csv
import io

import httpx
import pytest

from services.api.app import science
from spxcore import known

HEADER = "source_id,ra,dec,pmra,pmdec,parallax,phot_g_mean_mag\n"
CATALOG = HEADER + "4472832130942575872,10.684708,41.26875,,2.5,,17.2\n"


def mock_client(monkeypatch, answer):
    original = httpx.AsyncClient
    monkeypatch.setattr(known.httpx, "AsyncClient", lambda **kw:
                        original(transport=httpx.MockTransport(answer), **kw))


@pytest.mark.parametrize("failure", ["timeout", "http", "tap", "invalid_source", "missing_value"])
def test_same_dr3_query_recovers_from_primary_failure(monkeypatch, failure):
    requests = []

    def answer(request):
        requests.append(request)
        if len(requests) == 1:
            if failure == "timeout":
                raise httpx.ReadTimeout("upstream stalled", request=request)
            if failure == "http":
                return httpx.Response(503)
            text = {"tap": '<VOTABLE><INFO name="QUERY_STATUS" value="ERROR"/></VOTABLE>',
                    "invalid_source": HEADER + "123,nan,0,,,1,17\n",
                    "missing_value": HEADER + "123,10\n"}[failure]
            return httpx.Response(200, text=text)
        return httpx.Response(200, text=CATALOG)

    mock_client(monkeypatch, answer)
    result = asyncio.run(known.gaia(10.684708, 41.26875))
    assert len(requests) == 2
    assert requests[0].url.params["QUERY"] == requests[1].url.params["QUERY"]
    assert "gaiadr3.gaia_source " in requests[1].url.params["QUERY"]
    assert result[0]["source_id"] == "4472832130942575872"
    assert result[0]["pmra"] is None and result[0]["parallax"] is None
    assert result[0]["pmdec"] == 2.5 and result[0]["ref_epoch"] == 2016.0
    assert result[0]["catalog_url"] == "https://gaia.ari.uni-heidelberg.de/tap/sync"


def test_successful_primary_does_not_query_mirror(monkeypatch):
    requests = []

    def answer(request):
        requests.append(request)
        return httpx.Response(200, text=HEADER)

    mock_client(monkeypatch, answer)
    assert asyncio.run(known.gaia(10, 41)) == []
    assert len(requests) == 1


def test_failed_catalog_is_not_cached_as_an_empty_sky(monkeypatch, tmp_path):
    path = tmp_path / "catalog.json"
    monkeypatch.setattr(science, "cache_path", lambda *args: path)
    mock_client(monkeypatch, lambda request: httpx.Response(200, text="<html>Unavailable</html>"))
    with pytest.raises(httpx.RequestError):
        asyncio.run(science.catalog(10.684708, 41.26875, .25))
    assert not path.exists()


def test_potentially_truncated_cone_is_rejected(monkeypatch):
    row = next(csv.DictReader(io.StringIO(CATALOG)))
    monkeypatch.setattr(known.csv, "DictReader", lambda _: type("Rows", (), {
        "fieldnames": list(row), "__iter__": lambda self: iter([row] * 100000)})())
    with pytest.raises(ValueError, match="complete-catalog limit"):
        known._gaia_catalog(CATALOG, "https://example.test/tap")
