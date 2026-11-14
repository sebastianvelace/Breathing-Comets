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
export function propagate(
  ra: number,
  dec: number,
  pmra: number,
  pmdec: number,
  epoch: number,
  mjd: number,
): [number, number] {
  const a = ra * rad,
    d = dec * rad,
    dt = (mjd - 51544.5) / 365.25 + 2000 - epoch,
    k = (rad / 3600000) * dt;
  const x =
    Math.cos(d) * Math.cos(a) +
    k * (-pmra * Math.sin(a) - pmdec * Math.sin(d) * Math.cos(a));
  const y =
    Math.cos(d) * Math.sin(a) +
    k * (pmra * Math.cos(a) - pmdec * Math.sin(d) * Math.sin(a));
  const z = Math.sin(d) + k * pmdec * Math.cos(d);
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
