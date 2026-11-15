import {it,expect} from 'vitest';
import {spectrumPosition} from '../src/lib/astro/spectrum-position';
import {propagate} from '../src/lib/data/coordinates';
import type {GaiaStar} from '../src/lib/data/types';

const star: GaiaStar = {source_id:'measured-star',ra:269.446268,dec:4.768204,
  pmra:-801.6,pmdec:10362.4,ref_epoch:2026,parallax:546.9759};

it('a click at a moving source in an earlier plate requests its API reference position',()=>{
  const [ra,dec] = propagate(star.ra,star.dec,star.pmra!,star.pmdec!,star.ref_epoch,60914.213);
  const result = spectrumPosition(ra,dec,60914.213,[star]);
  const [r,d] = propagate(star.ra,star.dec,star.pmra!,star.pmdec!,star.ref_epoch,61041);
  expect(result.ra).toBeCloseTo(r,10);
  expect(result.dec).toBeCloseTo(d,10);
  expect(result.source).toBe('Gaia DR3 measured-star');
});

it('an unmatched sky position is preserved and missing motion is not invented',()=>{
  expect(spectrumPosition(0,0,60914,[star])).toEqual({ra:0,dec:0,source:''});
  expect(spectrumPosition(star.ra,star.dec,60914,[{...star,pmra:null}])).toEqual({ra:star.ra,dec:star.dec,source:''});
});
