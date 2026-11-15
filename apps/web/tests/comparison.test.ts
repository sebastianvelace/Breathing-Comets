import {describe,it,expect} from 'vitest';
import {comparisonPair} from '../src/lib/astro/comparison.js';
import type {FrameMeta} from '../src/lib/data/types.js';
const frame=(mjd:number,lam_um:number,visit:number):FrameMeta=>({mjd,lam_um,visit,bw_um:.08,obs_id:String(mjd),date:'2026-01-01',collection:'dr1'});
describe('prepared visit comparison',()=>{
  it('prefers a long baseline at nearby wavelengths over unmatched endpoints',()=>{
    expect(comparisonPair([frame(1,2.5,0),frame(2,3.7,0),frame(20,2.52,1),frame(30,3.0,2)])).toEqual([0,2]);
  });
  it('compares different visits and uses the closest color to break a baseline tie',()=>{
    expect(comparisonPair([frame(1,2.5,0),frame(20,2.55,1),frame(20,2.51,1),frame(30,2.5,0)])).toEqual([0,2]);
  });
  it('retains the endpoints when no wavelength-matched pair exists',()=>{
    expect(comparisonPair([frame(1,2.5,0),frame(20,4.5,1)])).toEqual([0,1]);
  });
});
