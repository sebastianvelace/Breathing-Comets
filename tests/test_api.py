"""API boundaries: real canonical keys, error envelopes, CORS and resource limits."""

import pytest
from fastapi.testclient import TestClient

from services.api.app.main import RATE_LIMITS, app


@pytest.fixture
def client():
    RATE_LIMITS.clear()
    with TestClient(app) as instance:
        yield instance
    RATE_LIMITS.clear()


@pytest.mark.parametrize("path", ["/v1/stack?ra=nan&dec=0", "/v1/gaia?ra=0&dec=0&radius=2", "/v1/spectrum?ra=1&dec=-91", "/v1/exposures?ra=1&dec=1&det=7", "/v1/known?ra=1&dec=1&fov=.2&mjd=NaN", "/missing"])
def test_errors_are_versioned_json(client, path):
    response = client.get(path)
    assert response.status_code in (404, 422)
    assert set(response.json()["error"]) == {"code", "source", "message", "retry_after_s"}
    assert "X-SPX-Data-Version" in response.headers


def test_rate_limit_shared_across_stack_and_spectrum(client):
    for i in range(30):
        response = client.get("/v1/stack" if i % 2 else "/v1/spectrum")
        assert response.status_code == 422
    response = client.get("/v1/spectrum")
    assert response.status_code == 429
    assert int(response.headers["Retry-After"]) > 0
    assert response.json()["error"]["code"] == "RATE_LIMITED"
    assert client.get("/v1/health").status_code == 200


@pytest.mark.parametrize("origin", ["https://breathingcomets.org", "https://breathing-comets.pages.dev", "https://abcd1234.breathing-comets.pages.dev"])
def test_cors_permits_production_and_preview(client, origin):
    response = client.get("/v1/health", headers={"Origin": origin})
    assert response.headers["access-control-allow-origin"] == origin


def test_fits_redirect_uses_index_and_public_bucket(client):
    response = client.get("/v1/fits", params={"obs_id": "2026W19_2A_1286_1", "det": 4, "collection": "qr2"}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "https://nasa-irsa-spherex.s3.us-east-1.amazonaws.com/dr1/level2/2026W19_2A/l2b-v27-2026-245/4/level2_2026W19_2A_1286_1D4_spx_l2b-v27-2026-245.fits"


def test_declared_spectrum_has_no_aperture_parameter(client):
    schema = client.get("/openapi.json").json()
    parameters = schema["paths"]["/v1/spectrum"]["get"]["parameters"]
    assert {p["name"] for p in parameters} == {"ra", "dec", "t0", "t1", "track"}
