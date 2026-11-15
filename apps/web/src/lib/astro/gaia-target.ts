import {propagate} from '../data/coordinates.js';
import type {GaiaStar} from '../data/types.js';

/** Match a free field at the API's 2026-01-01 reference epoch. */
export function referenceCounterpart(stars: GaiaStar[], ra: number, dec: number) {
  let closest: GaiaStar | undefined, distance = 2;
  for (const star of stars) {
    if (star.pmra === null || star.pmdec === null) continue;
    const [r, d] = propagate(star.ra, star.dec, star.pmra, star.pmdec, star.ref_epoch, 61041);
    const separation = Math.hypot((((r-ra+540)%360)-180)*Math.cos(dec*Math.PI/180), d-dec)*3600;
    if (separation < distance) {closest = star; distance = separation;}
  }
  return closest;
}
