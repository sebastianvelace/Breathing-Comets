<script lang="ts">
  import { page } from "$app/state";
  import { m } from "#lib/paraglide/messages.js";
  import { getLocale, localizeHref } from "#lib/paraglide/runtime.js";
  import Hero from "#lib/components/landing/Hero.svelte";
  import BlinkSection from "#lib/components/landing/BlinkSection.svelte";
  import DiffSection from "#lib/components/landing/DiffSection.svelte";
  import SpectrumSection from "#lib/components/landing/SpectrumSection.svelte";
  import CometsSection from "#lib/components/landing/CometsSection.svelte";
  import ValidationSection from "#lib/components/landing/ValidationSection.svelte";
  import TargetsSection from "#lib/components/landing/TargetsSection.svelte";
  import LandingFooter from "#lib/components/landing/LandingFooter.svelte";
  import {
    landingMedia,
    loadCometPacket,
    type CometState,
  } from "#lib/components/landing/landing.js";

  const ORIGIN = "https://breathingcomets.org";
  const locale = getLocale();

  let comet = $state<CometState>({ status: "idle" });

  // The 3I packet is optional and never blocks first paint: request it once the page has loaded.
  $effect(() => {
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

  const sections = [
    { id: "blink", n: "§1", label: () => m.landing_nav_blink() },
    { id: "diff", n: "§2", label: () => m.landing_nav_diff() },
    { id: "spectrum", n: "§3", label: () => m.landing_nav_spectrum() },
    { id: "comets", n: "§4", label: () => m.landing_nav_comets() },
    { id: "validation", n: "§5", label: () => m.landing_nav_validation() },
    { id: "targets", n: "§6", label: () => m.landing_nav_targets() },
  ];
  const poster = landingMedia.plates.barnard.epochs[0];
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
  <header class="masthead">
    <a class="brand" href={localizeHref("/")}>BREATHING COMETS</a>
    <nav aria-label={m.landing_nav_label()}>
      <ul>
        {#each sections as s (s.id)}
          <li><a href="#{s.id}"><span class="n">{s.n}</span> {s.label()}</a></li>
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
    <BlinkSection />
    <DiffSection />
    <SpectrumSection />
    <CometsSection {comet} />
    <ValidationSection {comet} />
    <TargetsSection />
  </main>

  <LandingFooter />
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
    z-index: 10;
  }
  .skip:focus {
    top: 8px;
  }
  .masthead {
    display: flex;
    align-items: center;
    gap: 24px;
    max-width: 1280px;
    margin: 0 auto;
    padding: 18px var(--gutter);
    border-bottom: 1px solid var(--rule);
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
    font-size: 14px;
    color: var(--ink-2);
    text-decoration: none;
    min-height: 40px;
    display: inline-flex;
    align-items: center;
  }
  nav a:hover {
    color: var(--ink);
    text-decoration: underline;
  }
  .n {
    font-family: var(--font-data);
    font-size: 12px;
    color: var(--graphite);
    margin-right: 2px;
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

  /* Shared section grammar (scoped to the landing root). */
  .landing :global(.section) {
    display: grid;
    grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
    gap: clamp(32px, 6vw, 96px);
    max-width: 1280px;
    margin: 0 auto;
    padding: clamp(56px, 8vw, 112px) var(--gutter);
    border-top: 1px solid var(--rule);
    align-items: start;
  }
  .landing :global(.section.wide) {
    grid-template-columns: minmax(0, 1fr);
  }
  .landing :global(.section.wide > .text) {
    max-width: 640px;
  }
  .landing :global(.section .text) {
    max-width: 640px;
  }
  .landing :global(.section .num) {
    font: 13px/1 var(--font-data);
    color: var(--co2);
    margin-bottom: 18px;
  }
  .landing :global(.section h2) {
    font-size: clamp(34px, 4.2vw, 56px);
    line-height: 1.04;
    letter-spacing: -0.01em;
    margin-bottom: 24px;
  }
  .landing :global(.section .text > p:not(.num):not(.margin-note)) {
    font-size: 17px;
    line-height: 1.65;
    color: var(--ink-2);
  }
  .landing :global(.margin-note) {
    margin-top: 24px;
    padding-top: 12px;
    border-top: 1px solid var(--rule);
    font: 12px/1.6 var(--font-data);
    color: var(--graphite);
    max-width: 52ch;
  }
  .landing :global(.figure) {
    min-width: 0;
  }
  @media (max-width: 860px) {
    .landing :global(.section) {
      grid-template-columns: minmax(0, 1fr);
    }
  }
</style>
