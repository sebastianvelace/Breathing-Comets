<script lang="ts">
  import { m } from "#lib/paraglide/messages.js";
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
</script>

<section class="hero" aria-labelledby="hero-title">
  <div class="copy">
    <p class="kicker">{m.landing_hero_kicker()}</p>
    <h1 id="hero-title">{m.landing_hero_title()}</h1>
    <p class="lede">{m.landing_hero_lede()}</p>
    <div class="actions">
      <a class="cta primary" href={exploreHref} data-testid="open-sky"
        >{m.landing_hero_cta_sky()}<span aria-hidden="true"> →</span></a
      >
      <a class="cta secondary" href={localizeHref("/comets")} data-testid="meet-comets">{m.landing_hero_cta_comets()}</a>
    </div>
  </div>

  <div class="plate-col" bind:this={figure}>
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
              alt={i === 0
                ? is3I
                  ? m.landing_hero_alt_3i()
                  : m.landing_hero_alt_barnard()
                : ""}
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
      </div>
      {#snippet caption()}
        <span class="who">
          {is3I ? m.landing_hero_plate_3i() : m.landing_hero_plate_barnard()}
        </span>
        <span class="meta" aria-live="off">
          SPHEREx{current.det ? ` D${current.det}` : is3I ? " D5" : ""} · {fmtLam(current.lam)} µm ·
          {current.date} · obs {current.obs}
        </span>
        {#if !is3I}
          <span class="standin">{m.landing_hero_standin()}</span>
        {/if}
      {/snippet}
    </Plate>
    <div class="loop-controls">
      <button
        type="button"
        class="ghost"
        aria-pressed={playing}
        disabled={!loaded || frames.length < 2}
        onclick={() => (playing = !playing)}
      >
        {playing ? m.landing_pause() : m.landing_play()}
      </button>
      <span class="counter mono">
        {m.landing_hero_visit({ n: index + 1, total: frames.length })}
      </span>
    </div>
  </div>
</section>

<style>
  .hero {
    display: grid;
    grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr);
    gap: clamp(32px, 6vw, 96px);
    align-items: center;
    padding: clamp(40px, 7vw, 96px) var(--gutter) clamp(56px, 8vw, 120px);
    max-width: 1280px;
    margin: 0 auto;
  }
  .kicker {
    font: 12px/1.4 var(--font-data);
    letter-spacing: 0.16em;
    color: var(--graphite);
    margin-bottom: 28px;
  }
  h1 {
    font-size: clamp(52px, 7.4vw, 96px);
    line-height: 0.98;
    letter-spacing: -0.015em;
    margin-bottom: 28px;
  }
  .lede {
    font-family: var(--font-display);
    font-size: clamp(20px, 1.8vw, 24px);
    line-height: 1.45;
    color: var(--ink-2);
    max-width: 34ch;
    margin-bottom: 40px;
  }
  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
  }
  .cta {
    display: inline-flex;
    align-items: center;
    min-height: 48px;
    padding: 12px 22px;
    font-weight: 500;
    text-decoration: none;
    border: 1px solid var(--co2);
  }
  .cta.primary {
    background: var(--co2);
    color: var(--paper);
  }
  .cta.secondary {
    color: var(--ink);
    border-color: var(--rule);
  }
  .cta.secondary:hover {
    border-color: var(--co2);
  }
  .cta.primary:hover {
    background: var(--ink);
    border-color: var(--ink);
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
  }
  .ghost[aria-pressed="true"] {
    background: transparent;
    color: var(--ink);
    border-color: var(--rule);
  }
  .counter {
    color: var(--graphite);
  }
  @media (max-width: 860px) {
    .hero {
      grid-template-columns: minmax(0, 1fr);
      align-items: start;
    }
    .lede {
      max-width: none;
    }
  }
</style>
