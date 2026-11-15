<script lang="ts">
  import ProductNav from "#lib/components/ProductNav.svelte";
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
  import ClosingCta from "#lib/components/landing/ClosingCta.svelte";
  import Starfield from "#lib/components/Starfield.svelte";
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

  // A persistent call to action appears once the hero (and its buttons) has scrolled away.
  let pastHero = $state(false);
  $effect(() => {
    const hero = document.querySelector("section.hero");
    if (!hero) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        pastHero = !entry.isIntersecting && entry.boundingClientRect.top < 0;
      },
      { threshold: 0 },
    );
    observer.observe(hero);
    return () => observer.disconnect();
  });
  const exploreHref = `${localizeHref("/explore")}?target=barnard&ui=story`;

  const sections = [
    { id: "blink", label: () => m.landing_nav_blink() },
    { id: "diff", label: () => m.landing_nav_diff() },
    { id: "spectrum", label: () => m.landing_nav_spectrum() },
    { id: "comets", label: () => m.landing_nav_comets() },
    { id: "validation", label: () => m.landing_nav_validation() },
    { id: "targets", label: () => m.landing_nav_targets() },
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
  <header class="masthead on-plate product-header">
    <a class="brand" href={localizeHref("/")}>BREATHING COMETS</a>
    <div class="product-navigation"><ProductNav /></div>

    <a class="nav-cta" class:show={pastHero} href={exploreHref} tabindex={pastHero ? 0 : -1} aria-hidden={pastHero ? undefined : "true"} data-testid="nav-cta"
      >{m.landing_nav_cta()}<span aria-hidden="true"> →</span></a
    >
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
    <nav class="section-nav" aria-label={m.landing_nav_label()}>
      <ul>
        {#each sections as s (s.id)}
          <li><a href="#{s.id}" class:active={active === s.id} aria-current={active === s.id ? "location" : undefined}>{s.label()}</a></li>
        {/each}
      </ul>
    </nav>
    <div class="on-plate band-ribbon"><SpectrumRibbon /></div>
    <BlinkSection />
    <div class="on-plate"><DiffSection /></div>
    <SpectrumSection />
    <div class="on-plate"><CometsSection {comet} /></div>
    <ValidationSection {comet} />
    <div class="tone"><TargetsSection /></div>
    <div class="on-plate closing"><Starfield count={70} seed={23} /><ClosingCta /></div>
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
    background: var(--accent);
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
  }
  header.masthead.on-plate {
    background: color-mix(in srgb, #050814 88%, transparent);
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
    background: var(--accent);
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
  .nav-cta {
    flex: none;
    display: inline-flex;
    align-items: center;
    min-height: 40px;
    padding: 6px 16px;
    font-size: 14px;
    font-weight: 500;
    text-decoration: none;
    background: var(--accent);
    color: var(--accent-ink);
    border: 1px solid var(--accent);
    border-radius: var(--r-pill);
    opacity: 0;
    translate: 0 -6px;
    visibility: hidden;
    transition:
      opacity 300ms var(--ease),
      translate 300ms var(--ease),
      visibility 0s linear 300ms,
      background 200ms var(--ease);
  }
  .nav-cta.show {
    opacity: 1;
    translate: 0 0;
    visibility: visible;
    transition-delay: 0s;
  }
  .nav-cta:hover {
    background: var(--accent-strong);
    border-color: var(--accent-strong);
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
    text-decoration-color: var(--accent);
    text-decoration-thickness: 2px;
  }
  @media (max-width: 1060px) {
    .section-nav {
      overflow-x: auto;
    }
    .masthead {
      justify-content: space-between;
      gap: 12px;
    }
    .nav-cta {
      margin-left: auto;
    }
  }
  .section-nav {
    max-width: 1280px;
    margin: 0 auto;
    padding: 12px var(--gutter);
    overflow-x: auto;
    border-block: 1px solid var(--rule);
  }
  .section-nav ul { flex-wrap: nowrap; width: max-content; }
  .section-nav a { white-space: nowrap; }
  @media (max-width: 520px) {
    .nav-cta {
      padding: 6px 10px;
      font-size: 13px;
    }
    .masthead .brand {
      letter-spacing: 0.12em;
      font-size: 12px;
    }
  }

  /* Dark "plate" bands: the same tokens, flipped, so every component inherits them. */
  .landing :global(.on-plate) {
    --paper: #050814;
    --paper-2: #0b1126;
    --ink: #e8ecf8;
    --ink-2: #b7c0da;
    --graphite: #8691b2;
    --rule: #1a2342;
    --accent: #7aa7ff;
    --accent-strong: #a6c4ff;
    --accent-ink: #061033;
    --co2: #f5d54a;
    --co: #7fd4e6;
    --h2o: #8fa5ff;
    --signal: #ff6b57;
    background: var(--paper);
    color: var(--ink);
  }
  .closing {
    position: relative;
    overflow: hidden;
  }
  .landing :global(.tone) {
    background: var(--paper-2);
  }

  /* Shared section grammar. */
  .landing :global(.section) {
    display: grid;
    grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
    gap: clamp(32px, 6vw, 96px);
    max-width: 1280px;
    margin: 0 auto;
    padding: clamp(72px, 10vw, 150px) var(--gutter);
    align-items: start;
  }
  .landing :global(.section.wide) {
    grid-template-columns: minmax(0, 1fr);
  }
  .landing :global(.section.wide > .text),
  .landing :global(.section .text) {
    max-width: 640px;
  }
  .landing :global(.section h2) {
    font-size: clamp(36px, 4.8vw, 68px);
    line-height: 1.02;
    letter-spacing: -0.035em;
    margin-bottom: 28px;
    text-wrap: balance;
  }
  .landing :global(.section .text > p:not(.margin-note)) {
    font-size: 18px;
    line-height: 1.68;
    color: var(--ink-2);
  }
  .landing :global(.margin-note) {
    margin-top: 24px;
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
