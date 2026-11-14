<script lang="ts">
  import type { NeoObject, ValidationDiameter } from '#lib/data/neo.js';
  import * as m from '#lib/paraglide/messages.js';
  let { objects, validation, kind, selected, onselect }: {
    objects: NeoObject[]; validation: ValidationDiameter[]; kind: 'catalog' | 'validation';
    selected: string; onselect: (slug: string) => void;
  } = $props();
  const dims = { w: 620, h: 350, left: 64, right: 24, top: 22, bottom: 56 };
  const bounds = $derived(kind === 'catalog'
    ? { xmin: Math.floor(Math.min(...objects.map(o => o.H))) - 1, xmax: Math.ceil(Math.max(...objects.map(o => o.H))) + 1,
        ymin: Math.floor(Math.log10(Math.min(...objects.map(o => o.D16)))), ymax: Math.ceil(Math.log10(Math.max(...objects.map(o => o.D84)))) }
    : { xmin: Math.floor(Math.log10(Math.min(...validation.map(o => o.neowise_km)))), xmax: Math.ceil(Math.log10(Math.max(...validation.map(o => o.neowise_km)))),
        ymin: Math.floor(Math.log10(Math.min(...validation.map(o => o.spherex_km)))), ymax: Math.ceil(Math.log10(Math.max(...validation.map(o => o.spherex_km)))) });
  const x = (v: number) => dims.left + (v - bounds.xmin) / (bounds.xmax - bounds.xmin) * (dims.w - dims.left - dims.right);
  const y = (v: number) => dims.h - dims.bottom - (Math.log10(v) - bounds.ymin) / (bounds.ymax - bounds.ymin) * (dims.h - dims.top - dims.bottom);
  const yTicks = $derived(Array.from({length: bounds.ymax - bounds.ymin + 1}, (_,i) => 10 ** (bounds.ymin + i)));
  const xTicks = $derived(Array.from({length: bounds.xmax - bounds.xmin + 1}, (_,i) => bounds.xmin + i));
  // These are labelled comparison assumptions, not measured albedos or refitted sizes.
  const albedos = [0.04, 0.14, 0.4];
  const diameterAtH = (H: number, p: number) => 1329 / Math.sqrt(p) * 10 ** (-H / 5);
</script>

<svg viewBox="0 0 620 350" role="img" aria-label={kind === 'catalog' ? m.neo_dh() : m.neo_validation_plot()}>
  <defs><clipPath id={'neo-' + kind}><rect x={dims.left} y={dims.top} width={dims.w-dims.left-dims.right} height={dims.h-dims.top-dims.bottom}/></clipPath></defs>
  {#each yTicks as v}<line class="grid" x1={dims.left} x2={dims.w-dims.right} y1={y(v)} y2={y(v)}/><text x={dims.left-10} y={y(v)+4} text-anchor="end">{v.toFixed(v < 1 ? -Math.log10(v) : 0)}</text>{/each}
  {#each xTicks as v}<text x={x(v)} y={dims.h-dims.bottom+22} text-anchor="middle">{kind === 'catalog' ? v : (10**v).toFixed(v < 0 ? -v : 0)}</text>{/each}
  <g clip-path={'url(#neo-' + kind + ')'}>
  {#if kind === 'catalog'}
    {#each albedos as p, i}<line class="assumption" x1={x(bounds.xmin)} y1={y(diameterAtH(bounds.xmin,p))} x2={x(bounds.xmax)} y2={y(diameterAtH(bounds.xmax,p))} stroke-dasharray={i === 1 ? '4 3' : '2 5'}/>{/each}
    {#each objects as o}
      <line class="interval" x1={x(o.H)} x2={x(o.H)} y1={y(o.D16)} y2={y(o.D84)}/>
      <a href={'#neo-' + o.slug} onclick={() => onselect(o.slug)} aria-label={`${o.pdes}: ${o.D_km} km, ${o.D16}–${o.D84} km, ${o.tier}`}>
        <circle class:selected={selected === o.slug} class:provisional={o.tier === 'provisional'} cx={x(o.H)} cy={y(o.D_km)} r={selected === o.slug ? 6 : 4}><title>{o.pdes} · {o.D_km} [{o.D16}–{o.D84}] km · {o.tier}</title></circle>
      </a>
    {/each}
  {:else}
    <line class="unity" x1={x(bounds.xmin)} y1={y(10**bounds.xmin)} x2={x(bounds.xmax)} y2={y(10**bounds.xmax)}/>
    {#each validation as o}<circle class="validation" cx={x(Math.log10(o.neowise_km))} cy={y(o.spherex_km)} r="3.5"><title>{o.key}: NEOWISE {o.neowise_km} km; SPHEREx {o.spherex_km.toPrecision(4)} km</title></circle>{/each}
  {/if}
  </g>
  <line class="axis" x1={dims.left} x2={dims.w-dims.right} y1={dims.h-dims.bottom} y2={dims.h-dims.bottom}/>
  <text class="label" x="330" y="340" text-anchor="middle">{kind === 'catalog' ? 'H (mag)' : 'D_NEOWISE (km)'}</text>
  <text class="label" transform="translate(16 160) rotate(-90)" text-anchor="middle">{kind === 'catalog' ? 'D (km)' : 'D_SPHEREx (km)'}</text>
</svg>
{#if kind === 'catalog'}<p class="legend">{m.neo_albedo()} {albedos.map(p => 'pV = ' + p.toFixed(2)).join(' · ')}</p>{/if}

<style>
  svg{display:block;width:100%;overflow:visible} text{fill:var(--graphite);font:11px var(--font-data)} .label{fill:var(--ink)} .grid,.axis{stroke:var(--rule);stroke-width:1} .assumption{stroke:var(--graphite);stroke-width:1;opacity:.6} .interval{stroke:var(--accent);stroke-width:1;opacity:.5} circle{fill:var(--accent);stroke:var(--paper);stroke-width:1}.provisional{fill:var(--paper);stroke:var(--accent)}.selected{fill:var(--signal);stroke:var(--ink);stroke-width:1.5}.validation{fill:var(--co)}.unity{stroke:var(--ink);stroke-width:1;stroke-dasharray:5 4} a:focus-visible circle{stroke:var(--ink);stroke-width:3}.legend{font:11px var(--font-data);color:var(--graphite)}
</style>
