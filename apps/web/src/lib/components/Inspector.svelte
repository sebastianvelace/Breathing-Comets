<script lang="ts">
  import * as m from "#lib/paraglide/messages.js";
  import type { Stack, SpectrumPoint, FrameMeta } from "#lib/data/types.js";
  import { worldToPixel, fmtSci } from "#lib/data/coordinates.js";
  import flagDefinitions from "../../../static/data/display_flags.json";
  import SpectrumPlot from "./SpectrumPlot.svelte";
  let {
    stack,
    index,
    selected,
    points,
    status,
    apiBase,
  }: {
    stack?: Stack;
    index: number;
    selected?: [number, number];
    points: SpectrumPoint[];
    status: string;
    apiBase: string;
  } = $props();
  const metadata = $derived(stack?.header.frames[index]);
  const sample = $derived.by(() => {
    if (!stack || !selected || !stack.frames[index]) return;
    const [x, y] = worldToPixel(...selected, stack.header.grid),
      xi = Math.round(x),
      yi = Math.round(y),
      { nx, ny, crpix } = stack.header.grid;
    if (xi < 0 || yi < 0 || xi >= nx || yi >= ny) return;
    const offset = yi * nx + xi,
      frame = stack.frames[index],
      flags = frame.flags[offset];
    const coefficients = metadata?.lam_poly,
      dx = xi - (crpix[0] - 1),
      dy = yi - (crpix[1] - 1);
    const wavelength = coefficients
      ? coefficients[0] +
        coefficients[1] * dx +
        coefficients[2] * dy +
        coefficients[3] * dx * dx +
        coefficients[4] * dx * dy +
        coefficients[5] * dy * dy
      : metadata?.lam_um;
    return {
      x: xi,
      y: yi,
      value: frame.flux[offset],
      variance: frame.var?.[offset],
      wavelength,
      flags,
      names: flagDefinitions.flags
        .filter((flag) => flags & (1 << flag.bit))
        .map((flag) => flag.name),
    };
  });
  function fitsLink(frame: FrameMeta) {
    return `${apiBase}/v1/fits?${new URLSearchParams({ obs_id: frame.obs_id, det: String(stack?.header.det), collection: frame.collection })}`;
  }
</script>

<aside class="inspector" aria-label={m.inspector()}>
  <p class="eyebrow mono">{m.inspector()}</p>
  <h2>{m.live_spectrum()}</h2>
  <p role="status" class="hint">{status || m.spectrum_pending()}</p>
  {#if points.length}<SpectrumPlot {points} label={m.live_spectrum()} />{/if}
  {#if selected}
    <p class="coordinates mono">ICRS {selected[0].toFixed(6)}, {selected[1].toFixed(6)}</p>
  {/if}
  {#if sample}
    <details>
      <summary>{m.pixel_details()}</summary>
      <dl class="mono">
        <div><dt>x, y</dt><dd>{sample.x}, {sample.y}</dd></div>
        <div><dt>λ</dt><dd>{sample.wavelength?.toFixed(4)} µm</dd></div>
        <div><dt>{m.intensity()}</dt><dd>{fmtSci(sample.value, 5)} MJy/sr</dd></div>
        <div><dt>σ</dt><dd>{sample.variance !== undefined ? fmtSci(Math.sqrt(sample.variance),4) : "—"} MJy/sr</dd></div>
        <div><dt>{m.flags()}</dt><dd>0x{sample.flags.toString(16)} {sample.names.join(" · ")}</dd></div>
      </dl>
    </details>
  {/if}
  {#if metadata}
    <details class="frame-properties">
      <summary>{m.frame_properties()}</summary>
      <dl class="mono">
        <div><dt>MJD</dt><dd>{metadata.mjd.toFixed(6)}</dd></div>
        <div><dt>UTC</dt><dd>{metadata.date}</dd></div>
        <div><dt>{m.visit()}</dt><dd>{metadata.visit+1}</dd></div>
        <div><dt>λ</dt><dd>{metadata.lam_um.toFixed(4)} µm</dd></div>
        <div><dt>Δλ</dt><dd>{metadata.bw_um.toFixed(4)} µm</dd></div>
        <div><dt>{m.collection()}</dt><dd>{metadata.collection}</dd></div>
        <div><dt>obs_id</dt><dd>{metadata.obs_id}</dd></div>
      </dl>
      <a href={fitsLink(metadata)} target="_blank" rel="noopener">{m.open_fits()} ↗</a>
    </details>
  {/if}
</aside>

<style>
  .inspector { background: var(--paper-2); color: var(--ink); padding: 24px; border: 1px solid var(--rule); border-radius: var(--r-lg); min-width: 0; align-self: start; }
  .eyebrow { color: var(--accent); margin-bottom: 10px; }
  h2 { font-size: 24px; line-height: 1.2; margin-bottom: 12px; }
  .hint { font-size: 14px; line-height: 1.6; color: var(--ink-2); }
  .coordinates { overflow-wrap: anywhere; color: var(--ink-2); margin-top: 16px; }
  details { margin-top: 18px; border-top: 1px solid var(--rule); }
  summary { font-size: 14px; font-weight: 500; }
  dl { font-size: 12px; }
  dl div { display: flex; gap: 12px; justify-content: space-between; border-bottom: 1px solid var(--rule); padding: 9px 0; }
  dt { color: var(--ink-2); flex-shrink: 0; }
  dd { margin: 0; text-align: right; overflow-wrap: anywhere; }
  a { font-size: 14px; }
  @media (max-width: 767px) { .inspector { margin-top: 24px; padding: 20px; } }
</style>
