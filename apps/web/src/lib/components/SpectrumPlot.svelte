<script lang="ts">
  import { onMount } from 'svelte';
  import type UPlot from 'uplot';
  import 'uplot/dist/uPlot.min.css';
  import type { SpectrumPoint } from '#lib/data/types.js';
  import { fmtSci } from '#lib/data/coordinates.js';
  import * as m from '#lib/paraglide/messages.js';
  let { points, label }: { points: SpectrumPoint[]; label: string } = $props();
  let host: HTMLDivElement;
  let plot: UPlot | undefined;
  let width = $state(0), Constructor = $state.raw<typeof UPlot>();
  const sorted = $derived(points.filter(p => Number.isFinite(p.lam) && Number.isFinite(p.f)).toSorted((a,b) => a.lam-b.lam));
  onMount(() => { let disposed = false; import('uplot').then(module => { if (!disposed) Constructor = module.default; }); const observer = new ResizeObserver(([entry]) => width = Math.floor(entry.contentRect.width)); observer.observe(host); return () => { disposed = true; observer.disconnect(); plot?.destroy(); }; });
  $effect(() => {
    if (!Constructor || width < 120 || !sorted.length) return;
    const source = sorted;
    plot?.destroy();
    plot = new Constructor({ width, height: 220, legend: { show:false }, cursor: { show: false },
      scales: { x: { time:false } },
      series: [{}, { stroke:'#A85A14', width:0, points:{ show:true, size:4, fill:'#A85A14' } }],
      axes: [{ label:m.wavelength(), labelSize:24, size:35, stroke:'#6F6A5E', grid:{show:false}, values:(_u, ticks) => ticks.map(v => v.toFixed(1)) }, { label:m.flux(), labelSize:24, size:48, stroke:'#6F6A5E', grid:{stroke:'#D3CCBD',width:.5}, values:(_u, ticks) => ticks.map(v => fmtSci(v,2)) }],
      hooks:{ drawClear:[u => { const bands:[number,number,string][] = [[2.6,2.85,'#3550C4'],[4.2,4.35,'#A85A14'],[4.55,4.8,'#1C6E73']]; u.ctx.save(); u.ctx.globalAlpha=.10; for(const [a,b,color] of bands){ u.ctx.fillStyle=color; const x=u.valToPos(a,'x',true), end=u.valToPos(b,'x',true);u.ctx.fillRect(Math.max(u.bbox.left,x),u.bbox.top,Math.max(0,Math.min(end,u.bbox.left+u.bbox.width)-Math.max(x,u.bbox.left)),u.bbox.height); }u.ctx.restore(); }], draw:[u => { const ctx=u.ctx;ctx.save();ctx.beginPath();ctx.rect(u.bbox.left,u.bbox.top,u.bbox.width,u.bbox.height);ctx.clip();ctx.strokeStyle='#A85A14';ctx.fillStyle=getComputedStyle(host).getPropertyValue('--paper');ctx.lineWidth=1; for(const p of source){ const x=u.valToPos(p.lam,'x',true),y=u.valToPos(p.f,'y',true);ctx.beginPath();ctx.moveTo(x,u.valToPos(p.f-p.e,'y',true));ctx.lineTo(x,u.valToPos(p.f+p.e,'y',true));ctx.stroke();if(p.sat){ctx.beginPath();ctx.arc(x,y,4,0,Math.PI*2);ctx.fill();ctx.stroke();} }ctx.restore(); }] }
    }, [source.map(p => p.lam),source.map(p => p.f)],host);
    return () => { plot?.destroy(); plot=undefined; };
  });
</script>
<div bind:this={host} role="img" aria-label={label} data-testid="spectrum-plot" data-points={points.length}></div>
<details><summary>{m.wavelength()} / {m.flux()}</summary><div class="data-table"><table><thead><tr><th>µm</th><th>mJy</th><th>σ</th></tr></thead><tbody>{#each sorted as p}<tr><td>{p.lam.toFixed(4)}</td><td>{fmtSci(p.f,4)}</td><td>{fmtSci(p.e,3)}{p.sat ? ' ○' : ''}</td></tr>{/each}</tbody></table></div></details>
<style>div[role=img]{min-width:0;width:100%;min-height:220px}details{font:11px var(--font-data);color:var(--graphite);margin-bottom:20px}.data-table{max-height:180px;overflow:auto}table{width:100%;text-align:right}th,td{padding:4px;border-bottom:1px solid var(--rule)}</style>
