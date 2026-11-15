import asyncio
import io

import numpy as np
from astropy.io import fits
from spxcore import fitsio


def test_partial_physical_layout_extends_without_refetching_headers(monkeypatch):
    file = io.BytesIO()
    fits.HDUList([fits.PrimaryHDU(), fits.ImageHDU(np.ones((3, 4)), name='IMAGE'),
                  fits.ImageHDU(np.zeros((3, 4)), name='WCS-WAVE')]).writeto(file)
    raw = file.getvalue()
    requests = []

    async def read(key, start, length):
        requests.append(start)
        return raw[start:start+length]

    monkeypatch.setattr(fitsio.s3, 'get_range', read)
    monkeypatch.setattr(fitsio, '_layouts', {})

    async def verify():
        prefix = await fitsio.read_hdu_layout('retained-layout', max_hdus=2)
        assert [h['name'] for h in prefix] == ['PRIMARY', 'IMAGE']
        first_requests = list(requests)
        full = await fitsio.read_hdu_layout('retained-layout')
        assert [h['name'] for h in full] == ['PRIMARY', 'IMAGE', 'WCS-WAVE']
        assert requests[:2] == first_requests
        assert len(requests) == 3
        assert (await fitsio.read_hdu_layout('retained-layout', 1))[0]['name'] == 'PRIMARY'
        assert len(requests) == 3

    asyncio.run(verify())
