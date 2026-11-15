import {propagate} from '../data/coordinates.js';
import type {GaiaStar, Manifest} from '../data/types.js';

/** The spectrum API accepts ICRS coordinates at its stated 2026-01-01 epoch. */
export function spectrumPosition(ra: number, dec: number, mjd: number, stars: GaiaStar[], target?: Manifest) {
  const candidates = stars.flatMap(star => star.pmra === null || star.pmdec === null ? [] : [{
    ra: star.ra, dec: star.dec, pmra: star.pmra, pmdec: star.pmdec, epoch: star.ref_epoch,
    source: 'Gaia DR3 ' + star.source_id,
  }]);
  if (target?.pm) candidates.push({ra: target.pm.ra0, dec: target.pm.dec0,
    pmra: target.pm.pmra_masyr, pmdec: target.pm.pmdec_masyr,
    epoch: target.pm.ref_epoch_jyear, source: target.name});
  const matches = candidates.map(c => {
    const [r,d] = propagate(c.ra,c.dec,c.pmra,c.pmdec,c.epoch,mjd);
    const distance = Math.hypot((((r-ra+540)%360)-180)*Math.cos(dec*Math.PI/180), d-dec)*3600;
    return {...c,distance};
  }).filter(c => c.distance <= 2).sort((a,b) => a.distance-b.distance);
  const match = matches[0];
  if (!match) return {ra,dec,source: ''};
  const [r,d] = propagate(match.ra,match.dec,match.pmra,match.pmdec,match.epoch,61041);
  return {ra:r,dec:d,source:match.source};
}
