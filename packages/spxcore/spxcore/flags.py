"""Official photometry mask and the SPXF v1 display-bit mapping."""

import numpy as np

HARD_ES21 = sum(1 << b for b in (2, 6, 7, 9, 10, 11, 15, 17, 26, 27, 28, 29))
DISPLAY_BITS = (0, 1, 2, 4, 6, 7, 9, 10, 11, 15, 17, 19, 21)
NODATA = 1 << 13
EXTENDED_HARD = sum(1 << b for b in (26, 27, 28, 29))
# Difference products only: reference was the median of non-bracketing visits.
DIFF_MEDIAN = 1 << 15


def remap_flags(flags, nodata=None):
    out = np.zeros(np.shape(flags), np.uint16)
    for bit, source in enumerate(DISPLAY_BITS):
        out |= (((flags >> source) & 1) << bit).astype(np.uint16)
    out |= ((flags & EXTENDED_HARD) != 0).astype(np.uint16) << 14
    if nodata is not None:
        out[nodata] |= NODATA
    return out


HARD_DISPLAY = int(remap_flags(np.array([HARD_ES21], np.int64))[0])


def restore_display_flags(flags):
    """Restore individually represented L2 categories; bit 14 is a grouped category."""
    out = np.zeros(np.shape(flags), np.uint32)
    for bit, source in enumerate(DISPLAY_BITS):
        out |= (((flags >> bit) & 1).astype(np.uint32) << source)
    return out
