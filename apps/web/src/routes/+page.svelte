<script lang="ts">
  import { page } from "$app/state";
  import * as m from "#lib/paraglide/messages.js";
  import { getLocale, localizeHref } from "#lib/paraglide/runtime.js";
  import Hero from "#lib/components/landing/Hero.svelte";
  import SpectrumRibbon from "#lib/components/landing/SpectrumRibbon.svelte";
  import BlinkSection from "#lib/components/landing/BlinkSection.svelte";
  import DiffSection from "#lib/components/landing/DiffSection.svelte";
  import SpectrumSection from "#lib/components/landing/SpectrumSection.svelte";
  import CometsSection from "#lib/components/landing/CometsSection.svelte";
  import ValidationSection from "#lib/components/landing/ValidationSection.svelte";
  import TargetsSection from "#lib/components/landing/TargetsSection.svelte";
  import LandingFooter from "#lib/components/landing/LandingFooter.svelte";
  import {
    bundledComet,
    landingMedia,
    loadCometPacket,
    type CometState,
  } from "#lib/components/landing/landing.js";

  const ORIGIN = "https://breathingcomets.org";
  const locale = getLocale();

  let comet = $state<CometState>(bundledComet);

  // The 3I packet is optional and never blocks first paint: request it once the page has loaded.
  $effect(() => {
    if (bundledComet.status === "ready") return;
    let cancelled = false;
    const run = () => {
      comet = { status: "loading" };
      loadCometPacket().then((state) => {
        if (!cancelled) comet = state;
      });
    };
    if (document.readyState === "complete") run();
    else window.addEventListener("load", run, { once: true });
    return () => {
      cancelled = true;
    };
  });

  let active = $state("");
  $effect(() => {
    const els = ["blink", "diff", "spectrum", "comets", "validation", "targets"]
      .map((id) => document.getElementById(id))
      .filter((el): el is HTMLElement => el !== null);
    const observer = new IntersectionObserver(
      (entries) => {
        for (const e of entries) if (e.isIntersecting) active = e.target.id;
      },
      { rootMargin: "-35% 0px -55% 0px" },
    );
    els.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  });

  const sections = [
    { id: "blink", n: "§1", label: () => m.landing_nav_blink() },
    { id: "diff", n: "§2", label: () => m.landing_nav_diff() },
    { id: "spectrum", n: "§3", label: () => m.landing_nav_spectrum() },
    { id: "comets", n: "§4", label: () => m.landing_nav_comets() },
    { id: "validation", n: "§5", label: () => m.landing_nav_validation() },
    { id: "targets", n: "§6", label: () => m.landing_nav_targets() },
  ];
  const poster =
    bundledComet.status === "ready" && bundledComet.packet.plates.epochs[0]
      ? { src: bundledComet.packet.plates.epochs[0].image }
      : landingMedia.plates.barnard.epochs[0];
</script>

<svelte:head>
  <title>{m.landing_meta_title()}</title>
  <meta name="description" content={m.landing_meta_description()} />
  <link rel="canonical" href="{ORIGIN}{localizeHref('/')}" />
  <link rel="alternate" hreflang="en" href="{ORIGIN}{localizeHref('/', { locale: 'en' })}" />
  <link rel="alternate" hreflang="es" href="{ORIGIN}{localizeHref('/', { locale: 'es' })}" />
  <link rel="alternate" hreflang="x-default" href="{ORIGIN}/" />
  <link rel="preload" as="image" href={poster.src} type="image/webp" fetchpriority="high" />
  <meta property="og:title" content={m.landing_hero_title()} />
  <meta property="og:description" content={m.landing_meta_description()} />
  <meta property="og:image" content="{ORIGIN}{poster.src}" />
</svelte:head>

<div class="landing">
  <a class="skip" href="#main">{m.landing_skip()}</a>
  <div class="progress" aria-hidden="true"></div>
  <header class="masthead on-plate">
    <a class="brand" href={localizeHref("/")}>BREATHING COMETS</a>
    <nav aria-label={m.landing_nav_label()}>
      <ul>
        {#each sections as s (s.id)}
          <li><a href="#{s.id}" class:active={active === s.id} aria-current={active === s.id ? "location" : undefined}><span class="n">{s.n}</span> {s.label()}</a></li>
        {/each}
      </ul>
    </nav>
    <div class="lang" role="group" aria-label={m.landing_lang_label()}>
      <a
        href={localizeHref(page.url.pathname, { locale: "en" })}
        hreflang="en"
        lang="en"
        aria-current={locale === "en" ? "true" : undefined}
        data-sveltekit-reload>EN</a
      >
      <a
        href={localizeHref(page.url.pathname, { locale: "es" })}
        hreflang="es"
        lang="es"
        aria-current={locale === "es" ? "true" : undefined}
        data-sveltekit-reload>ES</a
      >
    </div>
  </header>

  <main id="main">
    <Hero {comet} />
    <div class="on-plate band-ribbon"><SpectrumRibbon /></div>
    <BlinkSection />
    <div class="on-plate"><DiffSection /></div>
    <SpectrumSection />
    <div class="on-plate"><CometsSection {comet} /></div>
    <ValidationSection {comet} />
    <div class="tone"><TargetsSection /></div>
  </main>

  <div class="on-plate"><LandingFooter /></div>
</div>

<style>
  .landing {
    min-height: 100vh;
    overflow-x: clip;
  }
  .skip {
    position: absolute;
    left: 8px;
    top: -60px;
    padding: 8px 12px;
    background: var(--ink);
    color: var(--paper);
    z-index: 30;
  }
  .skip:focus {
    top: 8px;
  }
  .progress {
    position: fixed;
    inset: 0 0 auto 0;
    height: 2px;
    background: var(--co2);
    transform-origin: 0 50%;
    transform: scaleX(0);
    z-index: 25;
    pointer-events: none;
  }
  @supports (animation-timeline: scroll()) {
    .progress {
      animation: grow linear both;
      animation-timeline: scroll(root);
    }
    @keyframes grow {
      to {
        transform: scaleX(1);
      }
    }
  }
  .masthead {
    position: sticky;
    top: 0;
    z-index: 20;
    display: flex;
    align-items: center;
    gap: 24px;
    padding: 14px max(var(--gutter), calc((100vw - 1280px) / 2 + var(--gutter)));
    border-bottom: 1px solid #26241f;
  }
  header.masthead.on-plate {
    background: color-mix(in srgb, #0b0b0a 78%, transparent);
    backdrop-filter: blur(14px) saturate(1.2);
  }
  .masthead .brand {
    letter-spacing: 0.2em;
    font-size: 13px;
    white-space: nowrap;
    min-height: 40px;
    display: inline-flex;
    align-items: center;
  }
  nav {
    flex: 1;
    min-width: 0;
  }
  nav ul {
    display: flex;
    gap: 4px 18px;
    flex-wrap: wrap;
    list-style: none;
    margin: 0;
    padding: 0;
    justify-content: flex-end;
  }
  nav a {
    position: relative;
    font-size: 14px;
    color: var(--ink-2);
    text-decoration: none;
    min-height: 40px;
    display: inline-flex;
    align-items: center;
    transition: color 200ms var(--ease);
  }
  nav a::after {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    bottom: 6px;
    height: 1px;
    background: var(--co2);
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 300ms var(--ease);
  }
  nav a:hover,
  nav a.active {
    color: var(--ink);
  }
  nav a:hover::after,
  nav a.active::after {
    transform: scaleX(1);
  }
  .n {
    font-family: var(--font-data);
    font-size: 12px;
    color: var(--graphite);
    margin-right: 4px;
  }
  .lang {
    display: flex;
    gap: 2px;
    font: 13px var(--font-data);
  }
  .lang a {
    padding: 8px 8px;
    min-height: 40px;
    display: inline-flex;
    align-items: center;
    text-decoration: none;
    color: var(--graphite);
  }
  .lang a[aria-current="true"] {
    color: var(--ink);
    text-decoration: underline;
    text-decoration-color: var(--co2);
    text-decoration-thickness: 2px;
  }
  @media (max-width: 1060px) {
    nav {
      display: none;
    }
    .masthead {
      justify-content: space-between;
    }
  }

  /* Dark "plate" bands: the same tokens, flipped, so every component inherits them. */
  .landing :global(.on-plate) {
    --paper: #0b0b0a;
    --paper-2: #14130f;
    --ink: #ece7dc;
    --ink-2: #c9c2b4;
    --graphite: #9a9488;
    --rule: #34312a;
    --co2: #f2a03d;
    --co: #7fd4e6;
    --h2o: #8fa5ff;
    --signal: #ff6b57;
    background: var(--paper);
    color: var(--ink);
  }
  .landing :global(.tone) {
    background: var(--paper-2);
  }
  .band-ribbon {
    border-top: 1px solid var(--rule);
  }

  /* Shared section grammar. */
  .landing :global(.section) {
    display: grid;
    grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
    gap: clamp(32px, 6vw, 96px);
    max-width: 1280px;
    margin: 0 auto;
    padding: clamp(72px, 10vw, 150px) var(--gutter);
    border-top: 1px solid var(--rule);
    align-items: start;
  }
  .landing :global(.on-plate .section) {
    border-top-color: var(--rule);
  }
  .landing :global(.section.wide) {
    grid-template-columns: minmax(0, 1fr);
  }
  .landing :global(.section.wide > .text),
  .landing :global(.section .text) {
    max-width: 640px;
  }
  .landing :global(.section .num) {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    font: 13px/1 var(--font-data);
    color: var(--co2);
    margin-bottom: 22px;
  }
  .landing :global(.section .num::after) {
    content: "";
    width: 56px;
    height: 1px;
    background: var(--co2);
    transform-origin: left;
  }
  .landing :global(.section h2) {
    font-size: clamp(38px, 5.2vw, 76px);
    line-height: 1;
    letter-spacing: -0.015em;
    margin-bottom: 28px;
    text-wrap: balance;
  }
  .landing :global(.section .text > p:not(.num):not(.margin-note)) {
    font-size: 18px;
    line-height: 1.68;
    color: var(--ink-2);
  }
  .landing :global(.margin-note) {
    margin-top: 28px;
    padding-top: 14px;
    border-top: 1px solid var(--rule);
    font: 12px/1.6 var(--font-data);
    color: var(--graphite);
    max-width: 52ch;
  }
  .landing :global(.figure) {
    min-width: 0;
  }
  /* The figure follows the reader while the essay text scrolls past it. */
  @media (min-width: 861px) {
    .landing :global(.section:not(.wide) > .figure) {
      position: sticky;
      top: 96px;
    }
  }
  @media (max-width: 860px) {
    .landing :global(.section) {
      grid-template-columns: minmax(0, 1fr);
    }
  }

  /* Scroll-driven reveal: pure CSS, no flash, and absent where unsupported. */
  @supports (animation-timeline: view()) {
    .landing :global(.section .text > *),
    .landing :global(.section .figure),
    .landing :global(.section.wide > :not(.text)) {
      animation: reveal linear both;
      animation-timeline: view();
      animation-range: entry 0% entry 45%;
    }
    @keyframes reveal {
      from {
        opacity: 0;
        translate: 0 36px;
      }
    }
  }
  @media (prefers-reduced-motion: reduce) {
    .progress {
      animation: none;
      transform: scaleX(0);
    }
    .landing :global(.section .text > *),
    .landing :global(.section .figure),
    .landing :global(.section.wide > :not(.text)) {
      animation: none;
    }
  }
</style>
