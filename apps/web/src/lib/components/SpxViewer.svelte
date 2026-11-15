<script lang="ts">
  import { onMount } from "svelte";
  import { PlateRenderer } from "#lib/gl/renderer.js";
  import {
    worldToPixel,
    pixelToWorld,
    propagate,
  } from "#lib/data/coordinates.js";
  import type { Stack, Manifest, GaiaStar } from "#lib/data/types.js";
  import { comparisonViewport } from "#lib/astro/comparison.js";
  import * as m from "#lib/paraglide/messages.js";
  import flagDefinitions from "../../../static/data/display_flags.json";
  let {
    stack,
    index,
    a,
    b,
    mode,
    blend,
    manifest,
    star,
    showGaia = true,
    showGrid = false,
    showFlags = false,
    knownObjects = [],
    onpick,
  }: {
    stack: Stack;
    index: number;
    a: number;
    b: number;
    mode: string;
    blend: number;
    manifest: Manifest;
    star?: GaiaStar;
    showGaia?: boolean;
    showGrid?: boolean;
    showFlags?: boolean;
    knownObjects?: {
      name: string;
      ra: number;
      dec: number;
      vmag: number | null;
    }[];
    onpick?: (ra: number, dec: number) => void;
  } = $props();
  let canvas: HTMLCanvasElement, box: HTMLDivElement;
  let width = $state(0),
    height = $state(0),
    zoom = $state(1),
    cx = $state(0),
    cy = $state(0),
    error = $state("");
  let renderer = $state.raw<PlateRenderer>();
  let pendingFocus = $state<[number, number]>();
  let uploaded = 0;
  const scale = $derived(
    Math.min(width / stack.header.grid.nx, height / stack.header.grid.ny) *
      zoom,
  );
  const displayed = $derived(
    Math.min(
      mode === "blink" && blend >= 0.5 ? b : mode === "blink" ? a : index,
      Math.max(0, stack.frames.length - 1),
    ),
  );
  const mjd = $derived(
    stack.header.frames[displayed]?.mjd ?? stack.header.frames[0].mjd,
  );
  function marker(time: number): [number, number] {
    if (!star || star.pmra === null || star.pmdec === null) return [NaN, NaN];
    const [ra, dec] = propagate(
      star.ra,
      star.dec,
      star.pmra,
      star.pmdec,
      star.ref_epoch,
      time,
      star.parallax,
    );
    const [x, y] = worldToPixel(ra, dec, stack.header.grid);
    return [
      (x + 0.5 - cx) * scale + width / 2,
      height / 2 - (y + 0.5 - cy) * scale,
    ];
  }
  export function focusComparison(first: number, last: number) {
    pendingFocus = [first, last];
  }
  $effect(() => {
    if (!pendingFocus || !width || !height) return;
    const [first, last] = pendingFocus;
    pendingFocus = undefined;
    const pm = manifest.pm;
    const source = star && star.pmra !== null && star.pmdec !== null
      ? {ra: star.ra, dec: star.dec, pmra: star.pmra, pmdec: star.pmdec, epoch: star.ref_epoch}
      : pm ? {ra: pm.ra0, dec: pm.dec0, pmra: pm.pmra_masyr, pmdec: pm.pmdec_masyr, epoch: pm.ref_epoch_jyear} : undefined;
    if (!source) return;
    const pixels: [number, number][] = [first, last].map(i => {
      const frame = stack.header.frames[i];
      return frame ? worldToPixel(...propagate(source.ra, source.dec, source.pmra,
        source.pmdec, source.epoch, frame.mjd), stack.header.grid) : [NaN, NaN];
    });
    const viewport = comparisonViewport(stack.header.grid, pixels, width, height);
    if (viewport) ({cx, cy, zoom} = viewport);
  });
  const knownMarkers = $derived(
    knownObjects.map((object) => {
      const [x, y] = worldToPixel(object.ra, object.dec, stack.header.grid);
      return {
        ...object,
        x: (x + 0.5 - cx) * scale + width / 2,
        y: height / 2 - (y + 0.5 - cy) * scale,
      };
    }),
  );
  const point = $derived(marker(mjd)),
    future = $derived(marker(mjd + 365.25));
  onMount(() => {
    cx = stack.header.grid.nx / 2;
    cy = stack.header.grid.ny / 2;
    try {
      renderer = new PlateRenderer(canvas, stack.header, mode === "diff");
    } catch (e) {
      error = String(e);
    }
    const observer = new ResizeObserver(([entry]) => {
      width = entry.contentRect.width;
      height = entry.contentRect.height;
    });
    observer.observe(box);
    return () => {
      observer.disconnect();
      renderer?.dispose();
    };
  });
  $effect(() => {
    if (!renderer || !stack.frames.length || !width) return;
    while (uploaded < stack.frames.length)
      renderer.upload(stack.frames[uploaded], uploaded++);
    const last = stack.frames.length - 1;
    renderer.draw(
      Math.min(mode === "blink" ? a : index, last),
      Math.min(b, last),
      mode === "diff" ? 2 : mode === "blink" ? 1 : 0,
      blend,
      [cx, cy, scale],
      width,
      height,
      showFlags ? flagDefinitions.hard_mask : 0,
    );
  });
  let drag:
    | { x: number; y: number; cx: number; cy: number; moved: boolean }
    | undefined;
  function down(e: PointerEvent) {
    drag = { x: e.clientX, y: e.clientY, cx, cy, moved: false };
    (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
  }
  function move(e: PointerEvent) {
    if (!drag) return;
    const dx = e.clientX - drag.x,
      dy = e.clientY - drag.y;
    if (Math.hypot(dx, dy) > 4) drag.moved = true;
    cx = drag.cx - dx / scale;
    cy = drag.cy + dy / scale;
  }
  function up(e: PointerEvent) {
    if (drag && !drag.moved) {
      const rect = box.getBoundingClientRect();
      const x = (e.clientX - rect.left - width / 2) / scale + cx - 0.5,
        y = (height / 2 - (e.clientY - rect.top)) / scale + cy - 0.5;
      if (
        x >= 0 &&
        y >= 0 &&
        x < stack.header.grid.nx &&
        y < stack.header.grid.ny
      )
        onpick?.(...pixelToWorld(x, y, stack.header.grid));
    }
    drag = undefined;
  }
  function wheel(e: WheelEvent) {
    e.preventDefault();
    const rect = box.getBoundingClientRect(),
      dx = e.clientX - rect.left - width / 2,
      dy = height / 2 - e.clientY + rect.top,
      old = scale;
    zoom = Math.max(0.5, Math.min(20, zoom * Math.exp(-e.deltaY * 0.0015)));
    const next =
      Math.min(width / stack.header.grid.nx, height / stack.header.grid.ny) *
      zoom;
    cx += dx / old - dx / next;
    cy += dy / old - dy / next;
  }
</script>

<div class="plate" data-stack-kind={stack.header.kind} data-zoom={zoom} bind:this={box}>
  <canvas
    bind:this={canvas}
    aria-label={m.sky_plate()}
    onpointerdown={down}
    onpointermove={move}
    onpointerup={up}
    onpointercancel={() => (drag = undefined)}
    onwheel={wheel}
  ></canvas>
  <svg class="overlay" {width} {height} aria-label={m.gaia_overlay()}>
    <defs
      ><marker
        id="arrow"
        markerWidth="6"
        markerHeight="6"
        refX="5"
        refY="3"
        orient="auto"
        ><path d="M0 0L5 3L0 6" fill="none" stroke="currentColor" /></marker
      ></defs
    >
    {#if showGrid}<g class="registration" opacity=".35"
        >{#each [0.25, 0.5, 0.75] as fraction}<line
            x1={(stack.header.grid.nx * fraction - cx) * scale + width / 2}
            y1="0"
            x2={(stack.header.grid.nx * fraction - cx) * scale + width / 2}
            y2={height}
          /><line
            x1="0"
            y1={height / 2 - (stack.header.grid.ny * fraction - cy) * scale}
            x2={width}
            y2={height / 2 - (stack.header.grid.ny * fraction - cy) * scale}
          />{/each}</g
      >{/if}
    {#each knownMarkers as object}<g
        class="known-marker"
        transform={`translate(${object.x},${object.y})`}
        ><circle
          r="9"
          fill="none"
          stroke="currentColor"
          stroke-width="1.25"
        /><text x="13" y="4">{object.name}</text></g
      >{/each}
    {#if showGaia && Number.isFinite(point[0])}
      <g
        class="gaia-cross"
        data-testid="gaia-cross"
        data-x={point[0]}
        data-y={point[1]}
        transform={`translate(${point[0]},${point[1]})`}
      >
        <path d="M-13 0H-4M4 0H13M0-13V-4M0 4V13" />
        <text x="17" y="-12">Gaia DR3</text>
      </g>
      <line
        x1={point[0]}
        y1={point[1]}
        x2={future[0]}
        y2={future[1]}
        marker-end="url(#arrow)"
        class="motion"
      />
    {/if}
    <g class="scale"
      ><path
        d={`M28 ${height - 36}v6h${(60 / (Math.abs(stack.header.grid.cdelt_deg[0]) * 3600)) * scale}v-6`}
      /><text x="28" y={height - 44}>1′</text></g
    >
    <text class="north" x={width - 30} y="46">N ↑</text>
  </svg>
  {#if error}<p class="plate-error" role="alert">
      {m.webgl_unavailable()}
      {error}
    </p>{/if}
  <div class="zoom">
    <button
      onclick={() => (zoom = Math.min(20, zoom * 1.5))}
      aria-label={m.zoom_in()}>+</button
    ><button
      onclick={() => (zoom = Math.max(0.5, zoom / 1.5))}
      aria-label={m.zoom_out()}>−</button
    ><button
      onclick={() => {
        zoom = 1;
        cx = stack.header.grid.nx / 2;
        cy = stack.header.grid.ny / 2;
      }}
      aria-label={m.reset_view()}>↺</button
    >
  </div>
  <span class="plate-label">SPHEREx · D{stack.header.det} · {zoom.toFixed(1)}×</span>
</div>

<style>
  .plate {
    position: relative;
    width: 100%;
    aspect-ratio: 1.47;
    background: var(--plate);
    border-radius: var(--r-lg);
    box-shadow:
      0 0 0 1px color-mix(in srgb, var(--accent-on-plate) 16%, transparent),
      0 40px 90px -50px color-mix(in srgb, var(--accent-on-plate) 55%, transparent);
    overflow: hidden;
    touch-action: none;
    color: var(--plate-ink);
  }
  /* Keep plate + timeline in one screen on laptops: the controls are part of the instrument. */
  @media (min-width: 768px) {
    .plate {
      max-height: max(340px, calc(100svh - 370px));
    }
  }
  canvas {
    width: 100%;
    height: 100%;
    display: block;
    cursor: crosshair;
  }
  .overlay {
    position: absolute;
    inset: 0;
    pointer-events: none;
    overflow: hidden;
  }
  .overlay path,
  .overlay line {
    stroke: currentColor;
    stroke-width: 1.25;
    fill: none;
  }
  .gaia-cross,
  .motion {
    color: var(--accent-on-plate);
  }
  text {
    font: 11px var(--font-data);
    fill: currentColor;
  }
  .known-marker {
    color: var(--plate-ink);
  }
  .registration,
  .scale,
  .north {
    color: var(--plate-dim);
  }
  .zoom {
    position: absolute;
    bottom: 22px;
    right: 20px;
    display: flex;
    gap: 2px;
    padding: 4px;
    border-radius: var(--r-pill);
    background: color-mix(in srgb, var(--lab-panel) 82%, transparent);
    backdrop-filter: blur(8px);
  }
  .zoom button {
    background: transparent;
    color: var(--plate-ink);
    border: 0;
    padding: 0;
    min-width: 36px;
    min-height: 36px;
    font-size: 18px;
  }
  .plate-label {
    position: absolute;
    left: 28px;
    top: 24px;
    font: 11px var(--font-data);
    letter-spacing: 0.08em;
  }
  .plate-error {
    position: absolute;
    inset: 30%;
    text-align: center;
  }
  .gaia-cross {
    transition: none;
  }
  @media (max-width: 767px) {
    .plate {
      aspect-ratio: 1;
    }
    .zoom {
      bottom: 14px;
      right: 14px;
    }
  }
</style>
