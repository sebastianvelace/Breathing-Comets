"""Replay published frames; change only the input quality mask in memory."""

import gzip, json, struct, numpy as np
from pathlib import Path
from spxcore import sky, flags


def stack(path):
    raw = gzip.decompress(path.read_bytes())
    _, _, bits, length, _ = struct.unpack_from("<4sHHII", raw)
    h = json.loads(raw[16 : 16 + length])
    pixels = h["grid"]["nx"] * h["grid"]["ny"]
    offset = 16 + length
    frames = []

    def plane():
        nonlocal offset
        a = np.frombuffer(raw[offset : offset + pixels * 4], np.uint8)
        offset += (pixels * 4 + 7) // 8 * 8
        if bits & 1:
            a = a.reshape(4, pixels).T.copy().ravel()
        return a.view("<f4").reshape(h["grid"]["ny"], h["grid"]["nx"])

    for _ in h["frames"]:
        f = {"flux": plane()}
        if h.get("has_var"):
            f["var"] = plane()
        f["flags"] = np.frombuffer(raw[offset : offset + pixels * 2], "<u2").reshape(
            h["grid"]["ny"], h["grid"]["nx"]
        )
        offset += (pixels * 2 + 7) // 8 * 8
        frames.append(f)
    return h, frames


hard = int(flags.remap_flags(np.array([flags.HARD_ES21], np.int64))[0])
results = []
for path in sorted(Path("apps/web/static/data/targets").glob("*/manifest.json")):
    m = json.loads(path.read_text())
    det = str(m["default_det"])
    h, frames = stack(path.parent / m["stacks"][det])
    dh, retained = stack(path.parent / m["diff"][det])
    masked = [
        {**f, "flux": np.where((f["flags"] & hard) != 0, np.nan, f["flux"])}
        for f in frames
    ]
    original_info, original = sky.difference_stack(h["frames"], frames, h["grid"])
    new_info, new = sky.difference_stack(h["frames"], masked, h["grid"])
    nvalid = nchanged = nlost = n5 = 0
    maxdelta = replay_delta = 0.0
    for old, fixed, published, current, meta in zip(
        original, new, retained, frames, original_info
    ):
        valid = np.isfinite(old["flux"]) & ((current["flags"] & hard) == 0)
        nvalid += int(valid.sum())
        nlost += int((valid & ~np.isfinite(fixed["flux"])).sum())
        both = valid & np.isfinite(fixed["flux"])
        delta = np.abs(old["flux"][both] - fixed["flux"][both])
        nchanged += int((delta > 1e-5).sum())
        n5 += int((delta > 5 * (meta.get("diff_sigma") or float("inf"))).sum())
        maxdelta = max(maxdelta, float(delta.max(initial=0)))
        rp = np.isfinite(old["flux"]) & np.isfinite(published["flux"])
        replay_delta = max(
            replay_delta,
            float(np.abs(old["flux"][rp] - published["flux"][rp]).max(initial=0)),
        )
    results.append(
        {
            "target": m["slug"],
            "detector": det,
            "finite_hard_flagged_input_pixels": sum(
                int((np.isfinite(f["flux"]) & ((f["flags"] & hard) != 0)).sum())
                for f in frames
            ),
            "unflagged_finite_difference_pixels": nvalid,
            "changed_gt_1e_5_MJy_sr_by_input_mask_only": nchanged,
            "lost_minimum_references_after_masking": nlost,
            "change_gt_5_original_display_MAD_scales": n5,
            "maximum_change_MJy_sr": maxdelta,
            "original_replay_vs_published_maximum_delta_MJy_sr": replay_delta,
        }
    )
print(json.dumps(results, indent=2))
