<script lang="ts">
  import * as m from "#lib/paraglide/messages.js";
  import { statusLabel, type CometEntry, type CometStatus } from "#lib/data/comets.js";

  let {
    comets,
    selected = "",
    onselect,
  }: { comets: CometEntry[]; selected?: string; onselect: (slug: string) => void } = $props();

  const W = 760, H = 420, L = 64, R = 16, T = 18, B = 52;
  const X0 = 1, X1 = 20, Y0 = 1e23, Y1 = 1e28;
  const lx = (v: number) => L + ((Math.log10(v) - Math.log10(X0)) / (Math.log10(X1) - Math.log10(X0))) * (W - L - R);
  const ly = (v: number) => T + (1 - (Math.log10(v) - Math.log10(Y0)) / (Math.log10(Y1) - Math.log10(Y0))) * (H - T - B);
  const xTicks = [1, 2, 5, 10, 20];
  const yTicks = [23, 24, 25, 26, 27, 28];
  const sup = (n: number) => String(n).split("").map((c) => "⁰¹²³⁴⁵⁶⁷⁸⁹"["0123456789".indexOf(c)]).join("");
  const label = (c: CometEntry) =>
    `${c.name}: Q ${c.co2.q50.toExponential(2)} s⁻¹, r_h ${c.r_au!.toFixed(2)} au, ${statusLabel(c.co2.status as CometStatus)}`;
  const KEYS: Record<CometStatus, () => string> = {
    detected: m.comets_legend_detected,
    with_systematics: m.comets_legend_systematics,
    marginal: m.comets_legend_marginal,
    not_detected: m.comets_legend_not_detected,
  };
</script>

<figure>
  <svg viewBox="0 0 {W} {H}" role="group" aria-label={m.comets_chart_alt({ n: comets.length })} data-testid="comet-plot" data-points={comets.length}>
    {#each yTicks as t (t)}
      <line x1={L} x2={W - R} y1={ly(10 ** t)} y2={ly(10 ** t)} class="grid" />
      <text x={L - 8} y={ly(10 ** t) + 4} text-anchor="end" class="tick">10{sup(t)}</text>
    {/each}
    {#each xTicks as t (t)}
      <line x1={lx(t)} x2={lx(t)} y1={T} y2={H - B} class="grid" />
      <text x={lx(t)} y={H - B + 18} text-anchor="middle" class="tick">{t}</text>
    {/each}
    <text x={(L + W - R) / 2} y={H - 8} text-anchor="middle" class="axis-label">{m.comets_x()}</text>
    <text x={14} y={(T + H - B) / 2} text-anchor="middle" class="axis-label" transform="rotate(-90 14 {(T + H - B) / 2})">{m.comets_y()}</text>
    {#each comets as c (c.slug)}
      {@const x = lx(c.r_au!)}
      {@const y = ly(c.co2.q50)}
      {@const far = c.flags.includes("far_unreliable")}
      <g
        class="pt {c.co2.status}"
        class:chosen={selected === c.slug}
        class:far
        role="button"
        tabindex="0"
        aria-label={label(c)}
        aria-pressed={selected === c.slug}
        data-slug={c.slug}
        onclick={() => onselect(c.slug)}
        onkeydown={(e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), onselect(c.slug))}
      >
        <line x1={x} x2={x} y1={ly(c.co2.q16)} y2={ly(c.co2.q84)} class="bar" />
        <line x1={x - 4} x2={x + 4} y1={ly(c.co2.q16)} y2={ly(c.co2.q16)} class="bar" />
        <line x1={x - 4} x2={x + 4} y1={ly(c.co2.q84)} y2={ly(c.co2.q84)} class="bar" />
        {#if c.co2.status === "with_systematics"}
          <rect x={x - 5} y={y - 5} width="10" height="10" transform="rotate(45 {x} {y})" class="mark" />
        {:else}
          <circle cx={x} cy={y} r="5" class="mark" />
        {/if}
        <circle cx={x} cy={y} r="14" class="hit" />
      </g>
    {/each}
  </svg>
  <figcaption class="legend">
    {#each Object.entries(KEYS) as [key, text] (key)}
      <span><svg width="14" height="14" viewBox="-7 -7 14 14" aria-hidden="true" class="pt {key}">{#if key === "with_systematics"}<rect x="-4" y="-4" width="8" height="8" transform="rotate(45)" class="mark" />{:else}<circle r="4.5" class="mark" />{/if}</svg>{text()}</span>
    {/each}
    <span><svg width="14" height="14" viewBox="-7 -7 14 14" aria-hidden="true" class="pt far"><circle r="4.5" class="mark" /></svg>{m.comets_flag_far()}</span>
  </figcaption>
</figure>

<style>
  figure { margin: 0; }
  svg { display: block; width: 100%; height: auto; }
  .grid { stroke: var(--rule); stroke-width: 1; }
  .tick, .axis-label { font: 11px var(--font-data); fill: var(--graphite); }
  .bar { stroke: var(--graphite); stroke-width: 1.25; }
  .mark { stroke: var(--ink); stroke-width: 1.5; }
  .detected .mark { fill: var(--accent); }
  .with_systematics .mark { fill: var(--accent); stroke: var(--signal); stroke-width: 2; }
  .marginal .mark { fill: var(--paper); stroke: var(--accent); }
  .not_detected .mark { fill: var(--paper); stroke: var(--graphite); stroke-dasharray: 2 2; }
  .far .mark { fill: var(--paper); stroke: var(--signal); stroke-dasharray: 3 2; }
  .hit { fill: transparent; }
  .pt { cursor: pointer; }
  .pt:focus-visible { outline: none; }
  .pt:focus-visible .hit, .chosen .hit { stroke: var(--accent); stroke-width: 2; }
  .legend { display: flex; flex-wrap: wrap; gap: 6px 18px; margin-top: 8px; font: 12px var(--font-data); color: var(--graphite); }
  .legend span { display: inline-flex; align-items: center; gap: 6px; }
  .legend .pt { width: 14px; height: 14px; }
</style>
