import type {FrameMeta} from "#lib/data/types.js";

/** Prefer the longest baseline with wavelengths within one band width. */
export function comparisonPair(frames: FrameMeta[]): [number, number] {
  let pair: [number, number] = [0, Math.max(0, frames.length - 1)];
  let baseline = -1, separation = Infinity;
  frames.forEach((first, a) => frames.forEach((last, b) => {
    if (a >= b || first.visit === last.visit) return;
    const color = Math.abs(first.lam_um - last.lam_um);
    if (color > Math.min(first.bw_um, last.bw_um)) return;
    const span = Math.abs(last.mjd - first.mjd);
    if (span > baseline || (span === baseline && color < separation)) {
      pair = [a, b]; baseline = span; separation = color;
    }
  }));
  return pair;
}
