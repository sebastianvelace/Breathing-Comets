<script lang="ts">
  import * as m from "#lib/paraglide/messages.js";
  import { localizeHref } from "#lib/paraglide/runtime.js";
  import Plate from "./Plate.svelte";
  import {
    fmtLam,
    isoDate,
    landingMedia,
    type CometState,
  } from "./landing.js";

  let { comet }: { comet: CometState } = $props();

  const barnard = landingMedia.plates.barnard;
  const LOOP_MS = 6000;

  type HeroFrame = {
    src: string;
    width?: number;
    height?: number;
    date: string;
    lam: number;
    obs: string;
    det?: number;
  };

  const barnardFrames: HeroFrame[] = barnard.epochs.map((e) => ({
    src: e.src,
    width: e.width,
    height: e.height,
    date: isoDate(e.date),
    lam: e.lam_um,
    obs: e.obs_id,
    det: e.det,
  }));

  // MJD → ISO date (UTC) for packet epochs, which carry MJD only.
  const mjdDate = (mjd: number) =>
    new Date((mjd - 40587) * 86400000).toISOString().slice(0, 10);

  const is3I = $derived(
    comet.status === "ready" && comet.packet.plates.epochs.length > 0,
  );
  const packetPlates = $derived(
    comet.status === "ready" && comet.packet.plates.epochs.length > 0 ? comet.packet.plates : null,
  );
  const frames = $derived<HeroFrame[]>(
    comet.status === "ready" && comet.packet.plates.epochs.length > 0
      ? comet.packet.plates.epochs.map((e) => ({
          src: e.image,
          width: e.width,
          height: e.height,
          date: mjdDate(e.mjd),
          lam: e.lambda_um,
          obs: e.obs_id,
        }))
      : barnardFrames,
  );
  const credit = $derived(
    comet.status === "ready" && is3I
      ? comet.packet.credits.join(" · ")
      : landingMedia.credits[0],
  );

  let index = $state(0);
  let playing = $state(false);
  let loaded = $state(false);
  let reducedMotion = $state(false);
  let visible = $state(true);
  let figure: HTMLDivElement | undefined = $state();

  const current = $derived(frames[Math.min(index, frames.length - 1)]);

  // Preload the remaining epochs only after the first plate (the LCP) has loaded.
  $effect(() => {
    const list = frames;
    loaded = false;
    index = 0;
    let cancelled = false;
    const start = () =>
      Promise.all(
        list.slice(1).map((f) => {
          const img = new Image();
          img.src = f.src;
          return img.decode().catch(() => undefined);
        }),
      ).then(() => {
        if (cancelled) return;
        loaded = true;
        playing = !reducedMotion;
      });
    const idle = (cb: () => void) =>
      typeof window.requestIdleCallback === "function"
        ? window.requestIdleCallback(cb, { timeout: 1500 })
        : setTimeout(cb, 200);
    if (document.readyState === "complete") idle(start);
    else window.addEventListener("load", () => idle(start), { once: true });
    return () => {
      cancelled = true;
    };
  });

  $effect(() => {
    const query = window.matchMedia("(prefers-reduced-motion: reduce)");
    reducedMotion = query.matches;
    const change = () => {
      reducedMotion = query.matches;
      if (reducedMotion) playing = false;
    };
    query.addEventListener("change", change);
    return () => query.removeEventListener("change", change);
  });

  $effect(() => {
    if (!figure) return;
    const observer = new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting;
    });
    observer.observe(figure);
    return () => observer.disconnect();
  });

  $effect(() => {
    if (!playing || !loaded || !visible || frames.length < 2) return;
    const timer = window.setInterval(
      () => (index = (index + 1) % frames.length),
      LOOP_MS / frames.length,
    );
    return () => window.clearInterval(timer);
  });

  const exploreHref = `${localizeHref("/explore")}?target=barnard&ui=story`;
  const words = $derived(m.landing_hero_title().split(" "));

  // Gentle pointer parallax on the plate; skipped for touch and reduced motion.
  let tilt = $state({ x: 0, y: 0 });
  const onmove = (e: PointerEvent) => {
    if (reducedMotion || e.pointerType === "touch") return;
    tilt = { x: e.clientX / window.innerWidth - 0.5, y: e.clientY / window.innerHeight - 0.5 };
  };
</script>

<div class="band on-plate" onpointermove={onmove} role="presentation">
  <div class="ambient" aria-hidden="true">
    <svg viewBox="-400 -400 800 800" class="chart">
      <g fill="none" stroke="currentColor" stroke-width="1">
        <circle r="150" /><circle r="250" /><circle r="360" stroke-dasharray="2 8" />
        <path d="M-380 0H380M0 -380V380" opacity=".5" />
        {#each Array.from({ length: 36 }, (_, k) => k) as k (k)}
          <path d="M0 -360V-348" transform="rotate({k * 10})" />
        {/each}
      </g>
    </svg>
  </div>

  <section class="hero" aria-labelledby="hero-title">
    <div class="copy">
      <p class="kicker">{m.landing_hero_kicker()}</p>
      <h1 id="hero-title">
        {#each words as word, i (i)}<span class="w" style:--d="{120 + i * 140}ms">{word}</span>{" "}{/each}
      </h1>
      <p class="lede">{m.landing_hero_lede()}</p>
      <div class="actions">
        <a class="cta primary" href={exploreHref} data-testid="open-sky"
          >{m.landing_hero_cta_sky()}<span aria-hidden="true" class="arrow"> →</span></a
        >
        <a class="cta secondary" href={localizeHref("/comets")} data-testid="meet-comets">{m.landing_hero_cta_comets()}</a>
      </div>
      <a class="cue mono" href="#colors" aria-label={m.landing_hero_scroll()}><span aria-hidden="true"></span>{m.landing_hero_scroll()}</a>
    </div>

    <div class="plate-col" bind:this={figure} style:--px={tilt.x} style:--py={tilt.y}>
      <Plate
        arcsecPerPx={packetPlates ? packetPlates.pixel_arcsec : barnard.grid.pixel_arcsec}
        viewPx={packetPlates ? (packetPlates.nx ?? 1) : barnard.grid.nx}
        compass={packetPlates ? packetPlates.north_up === true : true}
        {credit}
      >
        <div class="frames" data-testid="hero-plate" data-frame={index} data-frames={frames.length}>
          {#if loaded}
            {#each frames as frame, i (frame.src)}
              <img
                src={frame.src}
                width={frame.width}
                height={frame.height}
                alt={i === 0 ? (is3I ? m.landing_hero_alt_3i() : m.landing_hero_alt_barnard()) : ""}
                aria-hidden={i === 0 ? undefined : "true"}
                class:shown={i === index}
                decoding="async"
              />
            {/each}
          {:else}
            <img
              class="shown"
              src={frames[0].src}
              width={frames[0].width}
              height={frames[0].height}
              alt={is3I ? m.landing_hero_alt_3i() : m.landing_hero_alt_barnard()}
              fetchpriority="high"
              decoding="async"
            />
          {/if}
          {#if playing}<span class="scan" aria-hidden="true"></span>{/if}
        </div>
        {#snippet caption()}
          <span class="who">{is3I ? m.landing_hero_plate_3i() : m.landing_hero_plate_barnard()}</span>
          <span class="meta" aria-live="off">
            SPHEREx{current.det ? ` D${current.det}` : is3I ? " D5" : ""} · {fmtLam(current.lam)} µm ·
            {current.date} · obs {current.obs}
          </span>
          {#if !is3I}<span class="standin">{m.landing_hero_standin()}</span>{/if}
        {/snippet}
      </Plate>
      <div class="loop-controls">
        <button type="button" class="ghost" aria-pressed={playing} disabled={!loaded || frames.length < 2} onclick={() => (playing = !playing)}>
          {playing ? m.landing_pause() : m.landing_play()}
        </button>
        <span class="progress" aria-hidden="true"><i style:width="{((index + 1) / frames.length) * 100}%"></i></span>
        <span class="counter mono">{m.landing_hero_visit({ n: index + 1, total: frames.length })}</span>
      </div>
    </div>
  </section>
</div>

<style>
  .band {
    position: relative;
    overflow: hidden;
    background: var(--paper);
    color: var(--ink);
  }
  .ambient {
    position: absolute;
    inset: 0;
    pointer-events: none;
    background:
      radial-gradient(60% 70% at 78% 45%, color-mix(in srgb, var(--co2) 14%, transparent), transparent 70%),
      repeating-linear-gradient(0deg, transparent 0 79px, color-mix(in srgb, var(--ink) 5%, transparent) 79px 80px),
      repeating-linear-gradient(90deg, transparent 0 79px, color-mix(in srgb, var(--ink) 5%, transparent) 79px 80px);
  }
  .chart {
    position: absolute;
    right: -12%;
    top: 50%;
    width: min(95vh, 900px);
    translate: 0 -50%;
    color: color-mix(in srgb, var(--ink) 16%, transparent);
    animation: turn 180s linear infinite;
  }
  @keyframes turn {
    to {
      rotate: 360deg;
    }
  }
  .hero {
    position: relative;
    display: grid;
    grid-template-columns: minmax(0, 1.08fr) minmax(0, 0.92fr);
    gap: clamp(32px, 6vw, 96px);
    align-items: center;
    padding: clamp(48px, 8vw, 112px) var(--gutter) clamp(64px, 9vw, 128px);
    max-width: 1280px;
    margin: 0 auto;
    min-height: min(86vh, 860px);
  }
  .kicker {
    font: 12px/1.4 var(--font-data);
    letter-spacing: 0.16em;
    color: var(--graphite);
    margin-bottom: 28px;
    animation: rise 900ms var(--ease) both;
  }
  h1 {
    font-size: clamp(56px, 8.6vw, 124px);
    line-height: 0.94;
    letter-spacing: -0.02em;
    margin-bottom: 32px;
    text-wrap: balance;
  }
  .w {
    display: inline-block;
    animation: word 1000ms var(--ease) var(--d) both;
  }
  @keyframes word {
    from {
      opacity: 0;
      transform: translateY(0.45em) rotate(1.5deg);
      filter: blur(6px);
    }
  }
  @keyframes rise {
    from {
      opacity: 0;
      transform: translateY(14px);
    }
  }
  .lede {
    font-family: var(--font-display);
    font-size: clamp(20px, 1.9vw, 26px);
    line-height: 1.45;
    color: var(--ink-2);
    max-width: 34ch;
    margin-bottom: 40px;
    animation: rise 1000ms var(--ease) 700ms both;
  }
  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    animation: rise 1000ms var(--ease) 900ms both;
  }
  .cta {
    display: inline-flex;
    align-items: center;
    min-height: 52px;
    padding: 12px 26px;
    font-weight: 500;
    text-decoration: none;
    border: 1px solid var(--co2);
    transition: background var(--t-fast, 200ms) var(--ease), color 200ms var(--ease), border-color 200ms var(--ease), transform 200ms var(--ease);
  }
  .cta.primary {
    background: var(--co2);
    color: #17160f;
  }
  .cta.primary:hover {
    background: var(--ink);
    border-color: var(--ink);
    color: var(--paper);
    transform: translateY(-2px);
  }
  .cta .arrow {
    display: inline-block;
    margin-left: 8px;
    transition: transform 250ms var(--ease);
  }
  .cta:hover .arrow {
    transform: translateX(5px);
  }
  .cta.secondary {
    color: var(--ink);
    border-color: color-mix(in srgb, var(--ink) 30%, transparent);
  }
  .cta.secondary:hover {
    border-color: var(--co2);
    color: var(--co2);
  }
  .cue {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    margin-top: clamp(32px, 6vh, 64px);
    color: var(--graphite);
    text-decoration: none;
    animation: rise 1000ms var(--ease) 1200ms both;
  }
  .cue span {
    width: 1px;
    height: 36px;
    background: var(--graphite);
    transform-origin: top;
    animation: drip 2.4s var(--ease) infinite;
  }
  @keyframes drip {
    0% { transform: scaleY(0); }
    50% { transform: scaleY(1); }
    100% { transform: scaleY(1); opacity: 0; }
  }
  .plate-col {
    animation: plate-in 1200ms var(--ease) 300ms both;
    transform: perspective(1400px) rotateY(calc(var(--px, 0) * 5deg)) rotateX(calc(var(--py, 0) * -5deg));
    transition: transform 400ms var(--ease);
  }
  @keyframes plate-in {
    from {
      opacity: 0;
      translate: 0 40px;
    }
  }
  .frames {
    position: relative;
    aspect-ratio: 1;
  }
  .frames img {
    position: absolute;
    inset: 0;
    opacity: 0;
  }
  .frames img.shown {
    opacity: 1;
  }
  .scan {
    position: absolute;
    top: 0;
    bottom: 0;
    width: 2px;
    background: var(--co2);
    box-shadow: 0 0 14px 2px color-mix(in srgb, var(--co2) 70%, transparent);
    animation: scan 6s linear infinite;
    pointer-events: none;
  }
  @keyframes scan {
    from { left: 0; opacity: 0; }
    8%, 92% { opacity: 0.9; }
    to { left: 100%; opacity: 0; }
  }
  .who {
    display: block;
    color: var(--ink);
  }
  .meta {
    display: block;
  }
  .standin {
    display: block;
    margin-top: 6px;
    color: var(--signal);
  }
  .loop-controls {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-top: 12px;
  }
  .ghost {
    min-height: 40px;
    font-size: 14px;
    border-color: color-mix(in srgb, var(--ink) 25%, transparent);
  }
  .ghost[aria-pressed="true"] {
    background: transparent;
    color: var(--ink);
    border-color: color-mix(in srgb, var(--ink) 25%, transparent);
  }
  .progress {
    flex: 1;
    height: 1px;
    background: var(--rule);
    position: relative;
  }
  .progress i {
    position: absolute;
    left: 0;
    top: -1px;
    height: 3px;
    background: var(--co2);
    transition: width 500ms var(--ease);
  }
  .counter {
    color: var(--graphite);
  }
  @media (max-width: 860px) {
    .hero {
      grid-template-columns: minmax(0, 1fr);
      align-items: start;
      min-height: 0;
    }
    .lede {
      max-width: none;
    }
    .chart {
      right: -40%;
      width: 130vw;
    }
    .cue {
      display: none;
    }
    .plate-col {
      transform: none;
    }
  }
  @media (prefers-reduced-motion: reduce) {
    .w, .kicker, .lede, .actions, .cue, .plate-col, .chart, .scan, .cue span {
      animation: none;
    }
    .plate-col {
      transform: none;
    }
  }
</style>
