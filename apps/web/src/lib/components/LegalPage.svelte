<script lang="ts">
  import ProductNav from "#lib/components/ProductNav.svelte";
  import LegalLinks from "#lib/components/LegalLinks.svelte";
  import { getLocale, localizeHref } from "#lib/paraglide/runtime.js";
  import * as m from "#lib/paraglide/messages.js";
  import { legal, updated, issues } from "#lib/data/legal.js";

  let { kind }: { kind: "terms" | "privacy" } = $props();
  const locale = getLocale() === "es" ? "es" : "en";
  const other = locale === "en" ? "es" : "en";
  const doc = $derived(legal[kind][locale]);
  const path = $derived("/" + kind);
</script>

<svelte:head>
  <title>{doc.title} · Breathing Comets</title>
  <meta name="description" content={doc.intro} />
  <link rel="canonical" href={"https://breathingcomets.org" + localizeHref(path)} />
  <link rel="alternate" hreflang="en" href={"https://breathingcomets.org" + path} />
  <link rel="alternate" hreflang="es" href={"https://breathingcomets.org/es" + path} />
</svelte:head>

<header class="product-header">
  <a class="brand" href={localizeHref("/")}>BREATHING COMETS</a>
  <div class="product-navigation"><ProductNav /></div>
  <nav>
    <a href={localizeHref("/about")}>{m.about_title()}</a>
    <a lang={other} href={localizeHref(path, { locale: other })} data-sveltekit-reload>{other.toUpperCase()}</a>
  </nav>
</header>

<main data-testid="legal-page">
  <h1>{doc.title}</h1>
  <p class="intro">{doc.intro}</p>
  {#each doc.sections as section (section.h)}
    <section>
      <h2>{section.h}</h2>
      {#each section.p as paragraph}<p>{paragraph}</p>{/each}
    </section>
  {/each}
  <p class="meta mono">{m.legal_updated({ date: updated })} · <a href={issues} rel="external">{m.legal_contact()}</a></p>
</main>

<footer><LegalLinks /></footer>

<style>
  main { max-width: 760px; margin: auto; padding: 56px var(--gutter); }
  h1 { font-size: clamp(40px, 6vw, 64px); }
  .intro { font-size: 19px; color: var(--ink-2); }
  section { margin: 40px 0; }
  h2 { font-size: clamp(22px, 2.6vw, 28px); margin-bottom: 12px; }
  main p { font-size: 16px; line-height: 1.7; color: var(--ink-2); }
  .meta { margin-top: 48px; font-size: 13px; color: var(--graphite); }
  a { color: var(--accent); }
  footer { max-width: 760px; margin: 0 auto; padding: 0 var(--gutter) 40px; }
  @media (max-width: 700px) { h1 { font-size: 40px; } main { padding-top: 36px; } }
</style>
