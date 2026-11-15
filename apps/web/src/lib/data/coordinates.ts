import type { Grid } from "./types.js";
const rad = Math.PI / 180;
export function worldToPixel(
  ra: number,
  dec: number,
  grid: Grid,
): [number, number] {
  const d = dec * rad,
    d0 = grid.crval[1] * rad,
    delta = (ra - grid.crval[0]) * rad;
  const den =
    Math.sin(d) * Math.sin(d0) + Math.cos(d) * Math.cos(d0) * Math.cos(delta);
  if (den <= 0) return [NaN, NaN];
  return [
    (Math.cos(d) * Math.sin(delta)) / den / rad / grid.cdelt_deg[0] +
      grid.crpix[0] -
      1,
    (Math.cos(d0) * Math.sin(d) -
      Math.sin(d0) * Math.cos(d) * Math.cos(delta)) /
      den /
      rad /
      grid.cdelt_deg[1] +
      grid.crpix[1] -
      1,
  ];
}
export function pixelToWorld(
  x: number,
  y: number,
  grid: Grid,
): [number, number] {
  const xi = (x + 1 - grid.crpix[0]) * grid.cdelt_deg[0] * rad,
    eta = (y + 1 - grid.crpix[1]) * grid.cdelt_deg[1] * rad,
    d0 = grid.crval[1] * rad;
  const q = Math.cos(d0) - eta * Math.sin(d0);
  return [
    (((grid.crval[0] + Math.atan2(xi, q) / rad) % 360) + 360) % 360,
    Math.atan2(Math.sin(d0) + eta * Math.cos(d0), Math.hypot(q, xi)) / rad,
  ];
}
/**
 * Earth's barycentric position in au (ICRS axes), low precision: the Sun's geocentric
 * position from the Astronomical Almanac formula (about 0.01° in longitude), negated.
 * The Sun–barycentre offset (≤ 0.01 au) is ignored; for a 547 mas parallax the resulting
 * error is below 0.006″. SPHEREx's low-Earth orbit adds under 5 × 10⁻⁵ au.
 */
export function earthBarycentricAu(mjd: number): [number, number, number] {
  const n = mjd - 51544.5;
  const g = (357.528 + 0.9856003 * n) * rad;
  const lambda = (280.46 + 0.9856474 * n + 1.915 * Math.sin(g) + 0.02 * Math.sin(2 * g)) * rad;
  const r = 1.00014 - 0.01671 * Math.cos(g) - 0.00014 * Math.cos(2 * g);
  const eps = (23.439 - 0.0000004 * n) * rad;
  return [
    -r * Math.cos(lambda),
    -r * Math.cos(eps) * Math.sin(lambda),
    -r * Math.sin(eps) * Math.sin(lambda),
  ];
}

/**
 * Catalogue position propagated by proper motion to `mjd` (UTC). When `parallaxMas` is given,
 * the direction is also shifted to the geocentre (observer parallax): u' ∝ u − ϖ E.
 */
export function propagate(
  ra: number,
  dec: number,
  pmra: number,
  pmdec: number,
  epoch: number,
  mjd: number,
  parallaxMas: number | null = null,
): [number, number] {
  const a = ra * rad,
    d = dec * rad,
    dt = (mjd - 51544.5) / 365.25 + 2000 - epoch,
    k = (rad / 3600000) * dt;
  let x =
    Math.cos(d) * Math.cos(a) +
    k * (-pmra * Math.sin(a) - pmdec * Math.sin(d) * Math.cos(a));
  let y =
    Math.cos(d) * Math.sin(a) +
    k * (pmra * Math.cos(a) - pmdec * Math.sin(d) * Math.sin(a));
  let z = Math.sin(d) + k * pmdec * Math.cos(d);
  if (parallaxMas !== null && Number.isFinite(parallaxMas) && parallaxMas > 0) {
    const p = (parallaxMas / 3600000) * rad,
      norm = Math.hypot(x, y, z),
      [ex, ey, ez] = earthBarycentricAu(mjd);
    x = x / norm - p * ex;
    y = y / norm - p * ey;
    z = z / norm - p * ez;
  }
  return [
    (((Math.atan2(y, x) / rad) % 360) + 360) % 360,
    Math.atan2(z, Math.hypot(x, y)) / rad,
  ];
}
export function fmtSci(value: number, digits = 3): string {
  return Number.isFinite(value)
    ? value.toPrecision(digits).replace("e+", "e")
    : "—";
}
