import {describe,it,expect} from 'vitest';
import {comparisonPair, comparisonViewport} from '../src/lib/astro/comparison.js';
import type {FrameMeta, Grid} from '../src/lib/data/types.js';
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

describe('guided comparison framing',()=>{
  const grid: Grid = {nx:150,ny:150,crval:[0,0],crpix:[75,75],cdelt_deg:[-.0017,.0017],north_up:true};
  it('magnifies the source and keeps both visits visible on a narrow screen',()=>{
    const points: [number,number][] = [[72,73],[74,75]];
    const frame = comparisonViewport(grid,points,343,343)!;
    expect(frame.zoom).toBeGreaterThan(1);
    for (const [x,y] of points) {
      const scale = 343 / grid.nx * frame.zoom;
      expect(Math.abs((x+.5-frame.cx)*scale)).toBeLessThan(343/2-30);
      expect(Math.abs((y+.5-frame.cy)*scale)).toBeLessThan(343/2-30);
    }
  });
  it('does not hide widely separated visits outside the zoomed viewport',()=>{
    expect(comparisonViewport(grid,[[10,10],[140,140]],343,343)!.zoom).toBe(1);
  });
  it('leaves the view alone when positions are unavailable or outside the plate',()=>{
    expect(comparisonViewport(grid,[[NaN,75]],343,343)).toBeUndefined();
    expect(comparisonViewport(grid,[[150,75]],343,343)).toBeUndefined();
    expect(comparisonViewport(grid,[[75,75]],0,0)).toBeUndefined();
  });
});
