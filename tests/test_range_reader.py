import httpx
import pytest
from spxcore import fitsio, s3


def test_large_independent_reads_use_validated_bounded_ranges(monkeypatch):
    payload = bytes(range(256))*6000
    lengths = []

    def answer(request):
        first, last = map(int, request.headers['range'].removeprefix('bytes=').split('-'))
        last = min(last, len(payload)-1)
        lengths.append(last-first+1)
        return httpx.Response(206, headers={'Content-Range': f'bytes {first}-{last}/{len(payload)}'}, content=payload[first:last+1])

    original = httpx.Client
    monkeypatch.setattr(fitsio.httpx, 'Client', lambda **kw: original(transport=httpx.MockTransport(answer), **kw))
    with fitsio.RangeReader(s3.S3+'reference.fits') as reader:
        assert reader.read() == payload
        reader.seek(100)
        assert reader.read(30) == payload[100:130]
    assert max(lengths) <= 64*1024


def test_reference_cache_revalidates_the_object_etag(monkeypatch, tmp_path):
    version, requests = [1], []

    def answer(request):
        first, last = map(int, request.headers['range'].removeprefix('bytes=').split('-'))
        last = min(last, 200000-1)
        requests.append((version[0], first))
        return httpx.Response(206, headers={'Content-Range': f'bytes {first}-{last}/200000', 'ETag': str(version[0])},
                              content=bytes([version[0]])*(last-first+1))

    original = httpx.Client
    monkeypatch.setattr(fitsio.httpx, 'Client', lambda **kw: original(transport=httpx.MockTransport(answer), **kw))
    monkeypatch.setattr(fitsio, 'CACHE_DIR', tmp_path)
    with fitsio.RangeReader(s3.S3+'reference.fits') as reader:
        assert reader.read() == bytes([1])*200000
    previous = len(requests)
    with fitsio.RangeReader(s3.S3+'reference.fits') as reader:
        assert reader.read() == bytes([1])*200000
    assert len(requests) == previous+1  # fresh header, retained table pieces
    version[0] = 2
    with fitsio.RangeReader(s3.S3+'reference.fits') as reader:
        assert reader.read() == bytes([2])*200000
    assert len(requests) > previous+2


def test_ignored_range_is_rejected_before_downloading_the_full_object(monkeypatch):
    class Unreadable(httpx.SyncByteStream):
        def __iter__(self):
            raise AssertionError('Full object must not be consumed')

    original = httpx.Client
    transport = httpx.MockTransport(lambda request: httpx.Response(200, stream=Unreadable()))
    monkeypatch.setattr(fitsio.httpx, 'Client', lambda **kw: original(transport=transport, **kw))
    with pytest.raises(ValueError, match='Range requests are required'):
        fitsio.RangeReader(s3.S3+'reference.fits')
