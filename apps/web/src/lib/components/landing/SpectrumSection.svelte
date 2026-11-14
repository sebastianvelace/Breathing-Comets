<script lang="ts">
  import { m } from "#lib/paraglide/messages.js";
  import { localizeHref } from "#lib/paraglide/runtime.js";
  import { bands } from "#lib/astro/bands.js";
  import { fmtLam } from "./landing.js";

  type Point = { lam: number; f: number; e: number };
  type Load =
    | { status: "idle" | "loading" }
    | { status: "error" }
    | { status: "ready"; points: Point[]; name: string };

  const SLUG = "eps-indi-b";
  let spec = $state<Load>({ status: "idle" });
  let host: HTMLElement | undefined = $state();
  let selected = $state<number | null>(null);

  async function load() {
    spec = { status: "loading" };
    try {
      const response = await fetch(`/data/targets/${SLUG}.json`);
      if (!response.ok) throw new Error(String(response.status));
      const data = (await response.json()) as { name: string; spectrum: Point[] };
      const points = data.spectrum.filter(
        (p) => Number.isFinite(p.lam) && Number.isFinite(p.f) && Number.isFinite(p.e),
      );
      if (!points.length) throw new Error("empty");
      spec = { status: "ready", points, name: data.name };
    } catch {
      spec = { status: "error" };
    }
  }

  $effect(() => {
    if (!host) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          observer.disconnect();
          load();
        }
      },
      { rootMargin: "500px 0px" },
    );
    observer.observe(host);
    return () => observer.disconnect();
  });

  // Plot geometry (SVG user units).
  const W = 640,
    H = 340,
    L = 48,
    R = 12,
    T = 34,
    B = 40;
  const LAM0 = 0.7,
    LAM1 = 5.05;
  const x = (lam: number) => L + ((lam - LAM0) / (LAM1 - LAM0)) * (W - L - R);
  const yMax = $derived(
    spec.status === "ready"
      ? Math.max(...spec.points.map((p) => p.f + p.e)) * 1.08
      : 1,
  );
  const y = (f: number) => T + (1 - Math.max(f, 0) / yMax) * (H - T - B);
  const path = $derived(
    spec.status === "ready"
      ? spec.points
          .map((p, i) => `${i ? "L" : "M"}${x(p.lam).toFixed(1)} ${y(p.f).toFixed(1)}`)
          .join("")
      : "",
  );
  const yTicks = $derived.by(() => {
    const step = yMax > 40 ? 20 : yMax > 15 ? 10 : 5;
    const out: number[] = [];
    for (let v = 0; v <= yMax; v += step) out.push(v);
    return out;
  });

  type BandInfo = { text: () => string; slug?: string; anchor?: string };
  const info = (label: string): BandInfo => {
    if (label.startsWith("H I")) return { text: m.landing_s3_band_h };
    if (label.startsWith("H₂O")) return { text: m.landing_s3_band_h2o, slug: SLUG };
    if (label.startsWith("CH₄")) return { text: m.landing_s3_band_ch4, slug: SLUG };
    if (label.startsWith("CO₂")) return { text: m.landing_s3_band_co2, anchor: "#comets" };
    return { text: m.landing_s3_band_co, slug: SLUG };
  };
  const colorVar = (c: string) => `var(${c})`;
  const current = $derived(selected === null ? null : bands[selected]);
  const currentInfo = $derived(current ? info(current.label) : null);
</script>

<section class="section" id="spectrum" aria-labelledby="s3-title" bind:this={host}>
  <div class="text">
    <p class="num">§3</p>
    <h2 id="s3-title">{m.landing_s3_title()}</h2>
    <p>{m.landing_s3_p1()}</p>
    <p>{m.landing_s3_p2()}</p>
    <p class="margin-note">{m.landing_s3_note()}</p>
  </div>

  <div class="figure">
    <figure class="chart">
      <svg
        viewBox="0 0 {W} {H}"
        role="img"
        aria-label={m.landing_s3_alt()}
        data-testid="landing-spectrum"
        data-points={spec.status === "ready" ? spec.points.length : 0}
      >
        {#each bands as band, i (band.label)}
          <rect
            x={x(band.lo_um)}
            y={T}
            width={Math.max(x(band.hi_um) - x(band.lo_um), 2)}
            height={H - T - B}
            fill={colorVar(band.color)}
            class="band"
            class:active={selected === i}
            aria-hidden="true"
          />
        {/each}
        <line x1={L} x2={W - R} y1={H - B} y2={H - B} class="axis" />
        <line x1={L} x2={L} y1={T} y2={H - B} class="axis" />
        {#each [1, 2, 3, 4, 5] as t (t)}
          <line x1={x(t)} x2={x(t)} y1={H - B} y2={H - B + 5} class="axis" />
          <text x={x(t)} y={H - B + 18} text-anchor="middle" class="tick">{t}</text>
        {/each}
        <text x={W - R} y={H - 6} text-anchor="end" class="tick">λ (µm)</text>
        {#each yTicks as v (v)}
          <line x1={L - 5} x2={L} y1={y(v)} y2={y(v)} class="axis" />
          <text x={L - 8} y={y(v) + 4} text-anchor="end" class="tick">{v}</text>
        {/each}
        <text x={L} y={T - 14} class="tick">mJy</text>
        {#if spec.status === "ready"}
          {#each spec.points as p (p.lam)}
            <line
              x1={x(p.lam)}
              x2={x(p.lam)}
              y1={y(p.f + p.e)}
              y2={y(p.f - p.e)}
              class="err"
            />
          {/each}
          <path d={path} class="line" />
        {/if}
      </svg>
      <figcaption>
        {#if spec.status === "ready"}
          {m.landing_s3_caption({ name: spec.name, n: spec.points.length })}
        {:else if spec.status === "error"}
          <span class="warn">{m.landing_s3_error()}</span>
        {:else}
          {m.landing_loading()}
        {/if}
        <span class="credit">SPHEREx: NASA/JPL-Caltech/IRSA</span>
      </figcaption>
    </figure>

    <div class="bands" role="group" aria-label={m.landing_s3_bands_label()}>
      {#each bands as band, i (band.label)}
        <button
          type="button"
          aria-pressed={selected === i}
          style:--swatch={colorVar(band.color)}
          onclick={() => (selected = selected === i ? null : i)}
        >
          <i aria-hidden="true"></i>{band.label}
          <span class="mono">{fmtLam(band.center_um)}</span>
        </button>
      {/each}
    </div>
    <div class="band-info" aria-live="polite">
      {#if current && currentInfo}
        <p>
          <span class="mono">{current.label} · {fmtLam(current.lo_um)}–{fmtLam(current.hi_um)} µm</span><br />
          {currentInfo.text()}
          {#if currentInfo.slug}
            <a href="{localizeHref('/explore')}?target={currentInfo.slug}&ui=story"
              >{m.landing_s3_open_target()}</a
            >
          {:else if currentInfo.anchor}
            <a href={currentInfo.anchor}>{m.landing_s3_open_comets()}</a>
          {/if}
        </p>
      {:else}
        <p class="muted">{m.landing_s3_pick()}</p>
      {/if}
    </div>
  </div>
</section>

<style>
  .chart {
    margin: 0;
    border-top: 1px solid var(--rule);
    border-bottom: 1px solid var(--rule);
    padding: 12px 0;
  }
  svg {
    display: block;
    width: 100%;
    height: auto;
    overflow: visible;
  }
  .band {
    opacity: 0.16;
  }
  .band.active {
    opacity: 0.38;
  }
  .axis {
    stroke: var(--rule);
    stroke-width: 1;
  }
  .tick {
    font: 11px var(--font-data);
    fill: var(--graphite);
  }
  .err {
    stroke: var(--graphite);
    stroke-width: 1;
  }
  .line {
    fill: none;
    stroke: var(--ink);
    stroke-width: 1.25;
    stroke-linejoin: round;
  }
  figcaption {
    margin-top: 8px;
    font: 12px/1.6 var(--font-data);
    color: var(--graphite);
  }
  .credit {
    display: block;
  }
  .warn {
    color: var(--signal);
  }
  .bands {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 16px;
  }
  .bands button {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
  }
  .bands button[aria-pressed="true"] {
    background: transparent;
    color: var(--ink);
    border-color: var(--co2);
    box-shadow: inset 0 -2px 0 var(--co2);
  }
  .bands i {
    width: 10px;
    height: 10px;
    background: var(--swatch);
    display: inline-block;
  }
  .bands .mono {
    color: var(--graphite);
  }
  .band-info {
    min-height: 88px;
    margin-top: 14px;
    max-width: 56ch;
  }
  .band-info a {
    color: var(--co2);
    margin-left: 4px;
  }
</style>
