import { expect, it } from "vitest";
import { propagate } from "../src/lib/data/coordinates";

// Gaia DR3 4472832130942575872 (Barnard's Star). Reference positions from Astropy 8:
// apply_space_motion (rv = 0) for the proper-motion-only case, and the DE440-based
// get_body_barycentric("earth") vector for the geocentric (observer-parallax) case.
const star = { ra: 269.44850252543836, dec: 4.739420051112412, pmra: -801.5509783684709, pmdec: 10362.394206546573, plx: 546.975939730948, epoch: 2016.0 };
// [mjd, ra_geocentric, dec_geocentric, ra_barycentric, dec_barycentric] in degrees
const cases = [
  [60914.213, 269.446207549, 4.767237543, 269.446345822, 4.767205304],
  [61000.0, 269.446216432, 4.767821152, 269.446293343, 4.767881369],
  [61100.0, 269.446374997, 4.768645656, 269.446232170, 4.768669444],
  [61200.0, 269.446202565, 4.769529168, 269.446170997, 4.769457518],
  [61285.258, 269.445974537, 4.770155107, 269.446118841, 4.770129414],
];
const arcsec = (ra1: number, dec1: number, ra2: number, dec2: number) =>
  Math.hypot((ra1 - ra2) * Math.cos((dec2 * Math.PI) / 180), dec1 - dec2) * 3600;

it("matches Astropy's proper-motion propagation within 5 mas", () => {
  for (const [mjd, , , ra, dec] of cases) {
    const [r, d] = propagate(star.ra, star.dec, star.pmra, star.pmdec, star.epoch, mjd);
    expect(arcsec(r, d, ra, dec)).toBeLessThan(0.005);
  }
});

it("applies observer parallax to within 10 mas of the DE440 geocentric direction", () => {
  for (const [mjd, ra, dec, rb, db] of cases) {
    const [r, d] = propagate(star.ra, star.dec, star.pmra, star.pmdec, star.epoch, mjd, star.plx);
    expect(arcsec(r, d, ra, dec)).toBeLessThan(0.01);
    // and the shift itself is the 0.28–0.53″ parallactic displacement, not noise
    expect(arcsec(rb, db, ra, dec)).toBeGreaterThan(0.25);
  }
});

it("leaves positions unchanged without a positive parallax", () => {
  const a = propagate(star.ra, star.dec, star.pmra, star.pmdec, star.epoch, 61000);
  expect(propagate(star.ra, star.dec, star.pmra, star.pmdec, star.epoch, 61000, null)).toEqual(a);
  expect(propagate(star.ra, star.dec, star.pmra, star.pmdec, star.epoch, 61000, -1)).toEqual(a);
});
