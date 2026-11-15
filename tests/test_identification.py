import asyncio

import httpx
import pytest

from services.api.app import catalog_jobs


def test_documented_geocentric_observer_and_explicit_empty_field(monkeypatch):
    requests = []

    def answer(request):
        requests.append(request)
        return httpx.Response(200, json={"signature": {"version": "1.1"}, "warning": "no matching records"})

    original = httpx.AsyncClient
    monkeypatch.setattr(catalog_jobs.httpx, 'AsyncClient', lambda **kw: original(transport=httpx.MockTransport(answer), **kw))
    assert asyncio.run(catalog_jobs.identify(269.446268, -7.242182, .25, 61041)) == []
    assert len(requests) == 2
    for request in requests:
        assert request.url.params['xobs'] == '0,0,0,0,0,0'
        assert 'mpc-code' not in request.url.params
        assert request.url.params['fov-dec-center'].startswith('M07-14-')


def test_missing_result_count_is_not_silently_treated_as_empty(monkeypatch):
    original = httpx.AsyncClient
    transport = httpx.MockTransport(lambda r: httpx.Response(200, json={"signature": {"version": "1.1"}}))
    monkeypatch.setattr(catalog_jobs.httpx, 'AsyncClient', lambda **kw: original(transport=transport, **kw))
    with pytest.raises(ValueError, match='omitted the result count'):
        asyncio.run(catalog_jobs.identify(0, 0, .25, 61041))
