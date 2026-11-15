<script lang="ts">
  import * as m from "#lib/paraglide/messages.js";
  import Plate from "./Plate.svelte";
  import { fmtLam, gaiaPixel, isoDate, landingMedia } from "./landing.js";

  const barnard = landingMedia.plates.barnard;
  const grid = barnard.grid;
  const a = barnard.epochs[0];
  const b = barnard.epochs[barnard.epochs.length - 1];
  const star = barnard.gaia_counterpart;

  // Grid pixel (0-based, row 0 = south) → display coordinates of the north-up image.
  const toDisplay = ([x, y]: [number, number]): [number, number] => [
    x + 0.5,
    grid.ny - 1 - y + 0.5,
  ];
  const pa = star ? toDisplay(gaiaPixel(star, grid, a.mjd)) : null;
  const pb = star ? toDisplay(gaiaPixel(star, grid, b.mjd)) : null;
  const shiftPx = pa && pb ? Math.hypot(pb[0] - pa[0], pb[1] - pa[1]) : null;

  // Crop a window around the star so a 1–2 px displacement is visible.
  const HALF = 14;
  const cx = pa && pb ? (pa[0] + pb[0]) / 2 : grid.nx / 2;
  const cy = pa && pb ? (pa[1] + pb[1]) / 2 : grid.ny / 2;
  const x0 = Math.max(0, Math.min(grid.nx - 2 * HALF, Math.round(cx - HALF)));
  const y0 = Math.max(0, Math.min(grid.ny - 2 * HALF, Math.round(cy - HALF)));

  let showB = $state(false);
  let blinking = $state(false);
  let drawn = $state(false);
  let near = $state(false);
  let host: HTMLDivElement | undefined = $state();

  $effect(() => {
    if (!blinking) return;
    const timer = window.setInterval(() => (showB = !showB), 600);
    return () => window.clearInterval(timer);
  });

  $effect(() => {
    if (!host) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          drawn = true;
          observer.disconnect();
        }
      },
      { threshold: 0.4 },
    );
    observer.observe(host);
    // SVG <image> has no native lazy loading: mount the plates only near the viewport.
    const nearObserver = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          near = true;
          nearObserver.disconnect();
        }
      },
      { rootMargin: "600px 0px" },
    );
    nearObserver.observe(host);
    return () => (observer.disconnect(), nearObserver.disconnect());
  });

  // Open reticle: four ticks with a gap, so the star itself stays visible.
  const cross = (p: [number, number], inner = 1.4, outer = 3.4) =>
    `M${p[0] - outer} ${p[1]}H${p[0] - inner}M${p[0] + inner} ${p[1]}H${p[0] + outer}` +
    `M${p[0]} ${p[1] - outer}V${p[1] - inner}M${p[0]} ${p[1] + inner}V${p[1] + outer}`;
  const arrow = (from: [number, number], to: [number, number]) => {
    const dx = to[0] - from[0],
      dy = to[1] - from[1],
      len = Math.hypot(dx, dy) || 1,
      ux = dx / len,
      uy = dy / len,
      head = 0.9;
    // Open arrowhead: two strokes, no fill.
    const left = [to[0] - head * (ux + uy * 0.7), to[1] - head * (uy - ux * 0.7)];
    const right = [to[0] - head * (ux - uy * 0.7), to[1] - head * (uy + ux * 0.7)];
    return `M${from[0]} ${from[1]}L${to[0]} ${to[1]}M${left[0]} ${left[1]}L${to[0]} ${to[1]}L${right[0]} ${right[1]}`;
  };
  const current = $derived(showB ? b : a);
</script>

<section class="section" id="blink" aria-labelledby="s1-title">
  <div class="text">
    <h2 id="s1-title">{m.landing_s1_title()}</h2>
    <p>{m.landing_s1_p1()}</p>
    <p>{m.landing_s1_p2()}</p>
    <p>{m.landing_s1_p3()}</p>
    <p class="margin-note">
      {m.landing_s1_note({
        visits: barnard.n_visits,
        frames: barnard.n_frames,
        det: barnard.det,
      })}
    </p>
  </div>

  <div class="figure" bind:this={host}>
    <Plate
      arcsecPerPx={grid.pixel_arcsec}
      viewPx={2 * HALF}
      scaleLabel="30″"
      scaleArcsec={30}
      credit={landingMedia.credits.join(" · ")}
    >
      <svg
        viewBox="{x0} {y0} {2 * HALF} {2 * HALF}"
        role="img"
        aria-label={showB ? m.landing_s1_alt_b({ date: isoDate(b.date) }) : m.landing_s1_alt_a({ date: isoDate(a.date) })}
        data-testid="blink-plate"
        data-epoch={showB ? "b" : "a"}
      >
        <rect x="0" y="0" width={grid.nx} height={grid.ny} class="blank" />
        {#if near}
          <image href={a.src} width={grid.nx} height={grid.ny} class:hidden={showB} />
          <image href={b.src} width={grid.nx} height={grid.ny} class:hidden={!showB} />
        {/if}
        {#if pa && pb}
          <g class="ink" class:drawn fill="none">
            <path d={cross(pa)} class="halo" />
            <path d={cross(pb)} class="halo" />
            <path d={cross(pa)} class="cross a" />
            <path d={cross(pb)} class="cross b" />
            <path d={arrow(pa, pb)} class="halo arrow-halo" />
            <path d={arrow(pa, pb)} class="arrow" pathLength="1" />
          </g>
        {/if}
      </svg>
      {#snippet caption()}
        <span class="ep">
          <b>{showB ? "B" : "A"}</b> SPHEREx D{current.det} · {fmtLam(current.lam_um)} µm ·
          {isoDate(current.date)} · obs {current.obs_id}
        </span>
        {#if star}
          <span>{m.landing_s1_gaia({ id: star.source_id })}</span>
        {:else}
          <span class="warn">{m.landing_s1_gaia_missing()}</span>
        {/if}
      {/snippet}
    </Plate>
    <div class="controls" role="group" aria-label={m.landing_s1_controls()}>
      <button
        type="button"
        aria-pressed={!showB && !blinking}
        onclick={() => ((blinking = false), (showB = false))}
        >{m.landing_s1_epoch_a({ date: isoDate(a.date) })}</button
      >
      <button
        type="button"
        aria-pressed={showB && !blinking}
        onclick={() => ((blinking = false), (showB = true))}
        >{m.landing_s1_epoch_b({ date: isoDate(b.date) })}</button
      >
      <button type="button" aria-pressed={blinking} onclick={() => (blinking = !blinking)}>
        {blinking ? m.landing_pause() : m.landing_s1_blink()}
      </button>
    </div>
    {#if shiftPx !== null}
      <p class="readout mono">
        {m.landing_s1_shift({
          px: shiftPx.toFixed(1),
          arcsec: (shiftPx * grid.pixel_arcsec).toFixed(1),
        })}
      </p>
    {/if}
  </div>
</section>

<style>
  svg {
    aspect-ratio: 1;
  }
  image {
    image-rendering: pixelated;
  }
  .blank {
    fill: var(--plate);
  }
  image.hidden {
    visibility: hidden;
  }
  .ink path {
    stroke-width: 1.25px;
    vector-effect: non-scaling-stroke;
    stroke-linecap: square;
  }
  .ink .halo {
    stroke: var(--plate);
    stroke-width: 4px;
    opacity: 0.85;
  }
  .ink .arrow-halo {
    opacity: 0;
  }
  .drawn .arrow-halo {
    animation: appear 1ms 520ms forwards;
  }
  @keyframes appear {
    to {
      opacity: 0.85;
    }
  }
  .cross.a {
    stroke: var(--plate-dim);
  }
  .cross.b {
    stroke: var(--plate-ink);
  }
  .arrow {
    stroke: var(--accent-on-plate);
    stroke-dasharray: 1;
    stroke-dashoffset: 1;
  }
  .drawn .arrow {
    animation: draw 520ms var(--ease) forwards;
  }
  @keyframes draw {
    to {
      stroke-dashoffset: 0;
    }
  }
  @media (prefers-reduced-motion: reduce) {
    .arrow {
      stroke-dashoffset: 0;
    }
    .ink .arrow-halo {
      opacity: 0.85;
    }
  }
  .ep b {
    color: var(--ink);
    font-weight: 400;
    margin-right: 6px;
  }
  .ep {
    display: block;
  }
  .warn {
    color: var(--signal);
  }
  .controls {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 14px;
  }
  .controls button {
    font-size: 14px;
  }
  .readout {
    margin-top: 12px;
    color: var(--graphite);
  }
</style>
