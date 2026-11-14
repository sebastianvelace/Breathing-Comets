"""FITS physical HDU layout and row reads, including RICE_1 flags."""

import asyncio
import io

import httpx
import numpy as np
from astropy.io.fits import Header

from . import s3

BLOCK = 2880
_layouts = {}


class RangeReader(io.BufferedIOBase):
    """Seekable HTTPX transport for independent Astropy reads and codec fallback."""

    def __init__(self, url):
        if not url.startswith(s3.S3):
            raise ValueError("Only the public SPHEREx bucket is supported")
        self.url, self.position = url, 0
        self.client = httpx.Client(timeout=8)
        response = self.client.get(url, headers={"Range": "bytes=0-65535"})
        response.raise_for_status()
        if response.status_code != 206:
            self.client.close()
            raise ValueError("Range requests are required")
        self.size = int(response.headers["Content-Range"].rsplit("/", 1)[1])
        self.cached_start, self.cached = 0, response.content

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=0):
        pos = offset + (self.position if whence == 1 else self.size if whence == 2 else 0)
        if pos < 0:
            raise ValueError("Negative seek")
        self.position = pos
        return pos

    def read(self, size=-1):
        if size is None or size < 0:
            size = self.size-self.position
        size = min(size, max(0, self.size-self.position))
        if size == 0:
            return b""
        if self.cached_start <= self.position and self.position+size <= self.cached_start+len(self.cached):
            offset = self.position-self.cached_start
            result = self.cached[offset:offset+size]
        else:
            end = min(self.size-1, self.position+max(size, 65536)-1)
            response = self.client.get(self.url, headers={"Range": f"bytes={self.position}-{end}"})
            response.raise_for_status()
            if response.status_code != 206:
                raise ValueError("Range requests are required")
            self.cached_start, self.cached = self.position, response.content
            result = self.cached[:size]
        self.position += len(result)
        return result

    def close(self):
        if not self.closed:
            self.client.close()
        super().close()


def open_l2(url):
    from astropy.io import fits

    return fits.open(RangeReader(url), memmap=False)


async def read_hdu_layout(key, max_hdus=12):
    cache_key = (key, max_hdus)
    if cache_key in _layouts:
        return _layouts[cache_key]
    out, loc = [], 0
    for _ in range(max_hdus):
        blocks = 12
        while True:
            chunk = await s3.get_range(key, loc, BLOCK * blocks)
            end = next((i for i in range(0, len(chunk), 80) if chunk[i:i + 8] == b"END     "), None)
            if end is not None:
                break
            if blocks >= 192:
                raise ValueError("FITS header exceeds supported bounds")
            blocks *= 2
        hlen = (end // BLOCK + 1) * BLOCK
        header = Header.fromstring(chunk[:hlen].decode("ascii"), sep="")
        axes = [header[f"NAXIS{i}"] for i in range(1, header.get("NAXIS", 0) + 1)]
        size = abs(header.get("BITPIX", 8)) // 8 * (int(np.prod(axes)) if axes else 0)
        size = (size + header.get("PCOUNT", 0)) * header.get("GCOUNT", 1)
        span = (size + BLOCK - 1) // BLOCK * BLOCK
        out.append({"name": header.get("EXTNAME", "PRIMARY"), "header": header,
                    "hdr_loc": loc, "dat_loc": loc + hlen, "dat_span": span})
        loc += hlen + span
        if out[-1]["name"] == "WCS-WAVE":
            break
    if len(_layouts) >= 256:
        _layouts.pop(next(iter(_layouts)))
    _layouts[cache_key] = out
    return out


async def read_flag_rows_dr1(key, hdu, y0, y1):
    from astropy.io.fits.hdu.compressed._codecs import Rice1

    h = hdu["header"]
    if h.get("ZCMPTYPE") != "RICE_1" or h.get("ZTILE2", 1) != 1:
        raise ValueError("Unsupported compressed FLAGS tiling")
    rowlen, nrows = h["NAXIS1"], h["NAXIS2"]
    if rowlen != 8 or not h.get("TFORM1", "").startswith("1PB"):
        raise ValueError("Unsupported compressed FLAGS descriptor")
    raw = await s3.get_range(key, hdu["dat_loc"] + y0 * rowlen, (y1 - y0) * rowlen)
    desc = np.frombuffer(raw, ">i4").reshape(-1, 2)
    count, offsets = desc[:, 0], desc[:, 1]
    if np.any(count < 0) or np.any(offsets < 0):
        raise ValueError("Invalid RICE heap descriptor")
    low, high = int(offsets.min()), int((offsets + count).max())
    heap_start = hdu["dat_loc"] + h.get("THEAP", rowlen * nrows)
    heap = np.frombuffer(await s3.get_range(key, heap_start + low, high - low), np.uint8)
    parameters = {h.get(f"ZNAME{i}"): h.get(f"ZVAL{i}") for i in range(1, 10)}
    rice = Rice1(blocksize=parameters.get("BLOCKSIZE", 32), bytepix=parameters.get("BYTEPIX", 4),
                 tilesize=h.get("ZTILE1", h["ZNAXIS1"]))
    return np.vstack([np.frombuffer(rice.decode(heap[int(off) - low:int(off) - low + int(n)]), np.int32)
                      for off, n in zip(offsets, count)])


async def read_rows(key, layout, y0, y1, names=("IMAGE", "FLAGS")):
    hdus = {h["name"]: h for h in layout}
    result = {}
    raw_names, starts, ends, compressed = [], [], [], []
    for name in names:
        hdu, h = hdus[name], hdus[name]["header"]
        width = h.get("ZNAXIS1", h.get("NAXIS1"))
        height = h.get("ZNAXIS2", h.get("NAXIS2"))
        if not 0 <= y0 < y1 <= height:
            raise ValueError("Row range outside detector")
        if h.get("ZIMAGE", False):
            compressed.append((name, hdu))
        else:
            row_bytes = width * abs(h["BITPIX"]) // 8
            start = hdu["dat_loc"] + y0 * row_bytes
            raw_names.append(name)
            starts.append(start)
            ends.append(start + (y1 - y0) * row_bytes)
    jobs = [read_flag_rows_dr1(key, hdu, y0, y1) for _, hdu in compressed]
    if starts:
        jobs.append(s3.get_ranges(key, starts, ends))
    values = await asyncio.gather(*jobs)
    result.update({name: value for (name, _), value in zip(compressed, values)})
    if starts:
        buffers = values[-1]
        for name, buf in zip(raw_names, buffers):
            h = hdus[name]["header"]
            dtype = f">{'f' if h['BITPIX'] < 0 else 'i'}{abs(h['BITPIX']) // 8}"
            array = np.frombuffer(buf, dtype).reshape(y1 - y0, h["NAXIS1"])
            if h.get("BSCALE", 1) != 1 or h.get("BZERO", 0):
                array = array.astype(float) * h.get("BSCALE", 1) + h.get("BZERO", 0)
            result[name] = array
    return result
