<script lang="ts">
  import * as m from "#lib/paraglide/messages.js";
  import lite from "#lib/data/channels-lite.json";
  import { bands } from "#lib/astro/bands.js";

  const channels = lite.rows.map(([frame, wavelength_um, R]) => ({ frame, wavelength_um, R }));
  const LAM0 = channels[0].wavelength_um;
  const LAM1 = channels[channels.length - 1].wavelength_um;
  const R_MAX = Math.max(...channels.map((c) => c.R));
  const BLANK = new Set([50, 51]); // blank in the DR1 HiPS (dichroic)

  // Position of a wavelength along the equally spaced channel strip (interpolated by index).
  const position = (lam: number) => {
    const i = channels.findIndex((c) => c.wavelength_um >= lam);
    if (i <= 0) return 0;
    const a = channels[i - 1].wavelength_um, b = channels[i].wavelength_um;
    return ((i - 1 + (lam - a) / (b - a)) + 0.5) / channels.length;
  };
  const marks = bands
    .filter((b) => !b.label.startsWith("H I"))
    .map((b) => ({ label: b.label, x: position(b.center_um) * 100, color: b.color }));

  let go = $state(false);
  let readout = $state("");
  let host: HTMLElement | undefined = $state();

  $effect(() => {
    if (!host) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          go = true;
          observer.disconnect();
        }
      },
      { threshold: 0.35 },
    );
    observer.observe(host);
    return () => observer.disconnect();
  });

  const describe = (i: number) => {
    const c = channels[i];
    return m.landing_ribbon_readout({ n: c.frame + 1, lam: c.wavelength_um.toFixed(2), r: Math.round(c.R) });
  };
</script>

<section class="ribbon" id="colors" aria-labelledby="ribbon-title" bind:this={host} class:go>
  <div class="head">
    <h2 id="ribbon-title">{m.landing_ribbon_title({ n: channels.length })}</h2>
    <p>{m.landing_ribbon_caption({ lo: LAM0.toFixed(2), hi: LAM1.toFixed(2) })}</p>
  </div>
  <div
    class="strip"
    role="img"
    aria-label={m.landing_ribbon_alt({ n: channels.length, lo: LAM0.toFixed(2), hi: LAM1.toFixed(2) })}
    data-testid="ribbon"
    data-channels={channels.length}
    onpointerover={(e) => {
      const i = (e.target as HTMLElement).dataset.i;
      if (i !== undefined) readout = describe(Number(i));
    }}
  >
    {#each channels as c, i (c.frame)}
      <span
        class="bar"
        class:blank={BLANK.has(c.frame)}
        data-i={i}
        style:--i={i}
        style:--t={(c.wavelength_um - LAM0) / (LAM1 - LAM0)}
        style:--h={0.32 + 0.68 * (c.R / R_MAX)}
      ></span>
    {/each}
    {#each marks as mk (mk.label)}
      <span class="mark" style:left="{mk.x}%" style:--c="var({mk.color})"><i></i><b>{mk.label}</b></span>
    {/each}
  </div>
  <p class="readout mono" aria-live="off">{readout || m.landing_ribbon_hint()}</p>
  <p class="foot mono">{m.landing_ribbon_foot()}</p>
</section>

<style>
  .ribbon {
    max-width: 1280px;
    margin: 0 auto;
    padding: clamp(40px, 6vw, 88px) var(--gutter) clamp(56px, 7vw, 104px);
  }
  .head {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: 16px clamp(24px, 6vw, 96px);
    align-items: end;
    margin-bottom: 36px;
  }
  h2 {
    font-size: clamp(34px, 4.6vw, 64px);
    line-height: 1.02;
    margin: 0;
  }
  .head p {
    margin: 0;
    color: var(--ink-2);
    max-width: 48ch;
  }
  .strip {
    position: relative;
    display: flex;
    align-items: flex-end;
    gap: 3px;
    height: clamp(150px, 24vw, 260px);
    padding-bottom: 38px;
    border-bottom: 1px solid var(--rule);
  }
  .bar {
    flex: 1 1 0;
    min-width: 0;
    height: calc(var(--h) * 100%);
    background: color-mix(in oklab, var(--co2) calc(var(--t) * 100%), var(--h2o));
    transform: scaleY(0.04);
    transform-origin: bottom;
    opacity: 0.2;
    transition:
      transform 900ms var(--ease) calc(var(--i) * 11ms),
      opacity 700ms var(--ease) calc(var(--i) * 11ms);
  }
  .go .bar {
    transform: scaleY(1);
    opacity: 1;
    animation: shimmer 7s ease-in-out calc(1.4s + var(--i) * 55ms) infinite;
  }
  .bar:hover {
    animation: none;
    opacity: 1;
    filter: brightness(1.5);
  }
  .bar.blank {
    background: transparent;
    outline: 1px dashed var(--graphite);
    outline-offset: -1px;
  }
  @keyframes shimmer {
    0%, 82%, 100% { filter: brightness(1); }
    91% { filter: brightness(1.7); }
  }
  .mark {
    position: absolute;
    bottom: 0;
    transform: translateX(-50%);
    display: grid;
    justify-items: center;
    gap: 4px;
    pointer-events: none;
    font: 11px/1 var(--font-data);
    color: var(--c);
  }
  .mark i {
    width: 1px;
    height: 12px;
    background: var(--c);
  }
  .mark b {
    font-weight: 400;
    white-space: nowrap;
  }
  .readout {
    margin: 14px 0 0;
    min-height: 1.5em;
    color: var(--ink);
  }
  .foot {
    margin: 4px 0 0;
    color: var(--graphite);
  }
  @media (max-width: 760px) {
    .head {
      grid-template-columns: minmax(0, 1fr);
    }
    .strip {
      gap: 1px;
    }
    .mark b {
      font-size: 9px;
    }
  }
  @media (prefers-reduced-motion: reduce) {
    .bar,
    .go .bar {
      transition: none;
      animation: none;
      transform: scaleY(1);
      opacity: 1;
    }
  }
</style>
