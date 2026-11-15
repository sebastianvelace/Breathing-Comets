import type {FrameMeta, Grid} from "#lib/data/types.js";

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

/** Frame both predicted positions without claiming to measure their motion. */
export function comparisonViewport(grid: Grid, pixels: [number, number][], width: number, height: number) {
  if (!pixels.length || width <= 0 || height <= 0 || pixels.some(([x, y]) =>
    !Number.isFinite(x) || !Number.isFinite(y) || x < 0 || y < 0 || x >= grid.nx || y >= grid.ny)) return;
  const xs = pixels.map(p => p[0] + 0.5), ys = pixels.map(p => p[1] + 0.5);
  const left = Math.min(...xs), right = Math.max(...xs), bottom = Math.min(...ys), top = Math.max(...ys);
  const scale = Math.min(width / grid.nx, height / grid.ny);
  // Leave context around the PSF and enough space for both visits on mobile.
  const zoom = Math.max(1, Math.min(12, 0.75 * Math.min(
    width / Math.max(15, right - left + 12), height / Math.max(15, top - bottom + 12)) / scale));
  return {cx: (left + right) / 2, cy: (bottom + top) / 2, zoom};
}
