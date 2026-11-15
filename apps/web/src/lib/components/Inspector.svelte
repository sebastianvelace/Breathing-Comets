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
  <h2>{m.inspector()}</h2>
  {#if selected}<p class="mono">
      ICRS {selected[0].toFixed(6)}, {selected[1].toFixed(6)}
    </p>{/if}
  {#if sample}
    <dl class="mono">
      <div>
        <dt>x, y</dt>
        <dd>{sample.x}, {sample.y}</dd>
      </div>
      <div>
        <dt>λ</dt>
        <dd>{sample.wavelength?.toFixed(4)} µm</dd>
      </div>
      <div>
        <dt>{m.intensity()}</dt>
        <dd>{fmtSci(sample.value, 5)} MJy/sr</dd>
      </div>
      <div>
        <dt>σ</dt>
        <dd>
          {sample.variance !== undefined
            ? fmtSci(Math.sqrt(sample.variance), 4)
            : "—"} MJy/sr
        </dd>
      </div>
      <div>
        <dt>{m.flags()}</dt>
        <dd>0x{sample.flags.toString(16)} {sample.names.join(" · ")}</dd>
      </div>
    </dl>
  {:else}<p class="hint">{m.spectrum_pending()}</p>{/if}
  <h3>{m.live_spectrum()}</h3>
  <p role="status" class="hint">{status || m.spectrum_pending()}</p>
  {#if points.length}<SpectrumPlot {points} label={m.live_spectrum()} />{/if}
  {#if metadata}<section class="frame-properties">
      <h3>{m.frame_properties()}</h3>
      <dl class="mono">
        <div>
          <dt>MJD</dt>
          <dd>{metadata.mjd.toFixed(6)}</dd>
        </div>
        <div>
          <dt>UTC</dt>
          <dd>{metadata.date}</dd>
        </div>
        <div>
          <dt>{m.visit()}</dt>
          <dd>{metadata.visit + 1}</dd>
        </div>
        <div>
          <dt>λ</dt>
          <dd>{metadata.lam_um.toFixed(4)} µm</dd>
        </div>
        <div>
          <dt>Δλ</dt>
          <dd>{metadata.bw_um.toFixed(4)} µm</dd>
        </div>
        <div>
          <dt>{m.collection()}</dt>
          <dd>{metadata.collection}</dd>
        </div>
        <div>
          <dt>obs_id</dt>
          <dd>{metadata.obs_id}</dd>
        </div>
      </dl>
      <a class="mono" href={fitsLink(metadata)} target="_blank" rel="noopener"
        >{m.open_fits()} ↗</a
      >
    </section>{/if}
</aside>

<style>
  .inspector {
    --paper: #1a1916;
    --ink: #ece7dc;
    --ink-2: #c9c2b4;
    --graphite: #9a9488;
    --rule: #34312a;
    --co2: #f2d24b;
    --accent: #7aa7ff;
    --accent-ink: #061033;
    --co: #5fbfc7;
    --h2o: #8fa5ff;
    background: var(--paper);
    color: var(--ink);
    padding: 22px 20px;
    border: 1px solid var(--rule);
    min-width: 0;
    overflow: auto;
    max-height: calc(100vh - 180px);
    position: sticky;
    top: 20px;
  }
  h2 {
    font: 12px var(--font-data);
    letter-spacing: 0.08em;
    margin-bottom: 20px;
  }
  h3 {
    font: 20px var(--font-display);
    margin-top: 22px;
    margin-bottom: 10px;
  }
  dl {
    font-size: 10px;
    margin-bottom: 20px;
  }
  dl div {
    display: flex;
    gap: 12px;
    justify-content: space-between;
    border-bottom: 1px solid var(--rule);
    padding: 7px 0;
  }
  dt {
    color: var(--graphite);
    flex-shrink: 0;
  }
  dd {
    margin: 0;
    text-align: right;
    overflow-wrap: anywhere;
  }
  .hint {
    font-size: 12px;
    color: var(--graphite);
  }
  .frame-properties {
    border-top: 1px solid var(--rule);
    margin-top: 20px;
  }
  a {
    font-size: 11px;
  }
  .mono {
    overflow-wrap: anywhere;
  }
</style>
