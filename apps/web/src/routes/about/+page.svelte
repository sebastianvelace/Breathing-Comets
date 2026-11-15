<script lang="ts">
  import LegalLinks from "#lib/components/LegalLinks.svelte";
  import ProductNav from "#lib/components/ProductNav.svelte";
  import channelData from "../../../static/data/channels.json";
  import atlas from "../../../static/data/comets/index.json";
  import { getLocale, localizeHref } from "#lib/paraglide/runtime.js";
  import * as m from "#lib/paraglide/messages.js";

  const other = getLocale() === "en" ? "es" : "en";
  // Explicit functions, never a dynamic lookup in the message namespace (it defeats tree-shaking).
  const sources = [
    { id: "spherex", name: m.about_d_spherex, provider: "NASA/JPL-Caltech/IRSA", use: m.about_u_spherex },
    { id: "hips", name: m.about_d_hips, provider: "IRSA (NASA/IPAC)", use: m.about_u_hips },
    { id: "gaia", name: m.about_d_gaia, provider: "ESA/Gaia/DPAC", use: m.about_u_gaia },
    { id: "wise", name: m.about_d_wise, provider: "IRSA (NASA/IPAC). 2MASS: UMass and IPAC/Caltech. WISE, NEOWISE: NASA/JPL-Caltech", use: m.about_u_wise },
    { id: "jpl", name: m.about_d_jpl, provider: "NASA/JPL", use: m.about_u_jpl },
    { id: "simbad", name: m.about_d_simbad, provider: "CDS, Strasbourg (Harvard mirror)", use: m.about_u_simbad },
    { id: "aladin", name: m.about_d_aladin, provider: "CDS, Strasbourg", use: m.about_u_aladin },
    { id: "astropy", name: m.about_d_astropy, provider: "Astropy Project", use: m.about_u_astropy },
  ];
</script>

<svelte:head>
  <title>{m.about_title()} · Breathing Comets</title>
  <meta name="description" content={m.about_intro()} />
  <link rel="canonical" href={"https://breathingcomets.org" + localizeHref("/about")} />
  <link rel="alternate" hreflang="en" href="https://breathingcomets.org/about" />
  <link rel="alternate" hreflang="es" href="https://breathingcomets.org/es/about" />
</svelte:head>

<header class="product-header">
  <a class="brand" href={localizeHref("/")}>BREATHING COMETS</a>
    <div class="product-navigation"><ProductNav /></div>
  <nav>
    <a href={localizeHref("/method")}>{m.method_title()}</a>
    <a lang={other} href={localizeHref("/about", { locale: other })} data-sveltekit-reload>{other.toUpperCase()}</a>
  </nav>
</header>

<main>
  <h1>{m.about_title()}</h1>
  <p class="intro">{m.about_intro()}</p>

  <section id="what">
    <h2>{m.about_s1()}</h2>
    <p>{m.about_s1_p1({ n: channelData.channels.length })}</p>
    <p>{m.about_s1_p2()}</p>
  </section>

  <section id="challenge">
    <h2>{m.about_s2()}</h2>
    <p>{m.about_s2_p1()}</p>
    <p class="mono">{m.about_s2_p2()}</p>
  </section>

  <section id="start">
    <h2>{m.about_s3()}</h2>
    <ul class="links">
      <li><a href={`${localizeHref("/explore")}?target=barnard&ui=story`}>{m.about_l_sky()}</a></li>
      <li><a href={localizeHref("/comets")}>{m.about_l_comets({ n: atlas.counts.comets })}</a></li>
      <li><a href={localizeHref("/neo")}>{m.about_l_neo()}</a></li>
      <li><a href={localizeHref("/method")}>{m.about_l_method()}</a></li>
    </ul>
  </section>

  <section id="credits">
    <h2>{m.about_s4()}</h2>
    <p>{m.about_s4_intro()}</p>
    <div class="scroll">
      <table data-testid="about-sources">
        <thead><tr><th>{m.about_col_source()}</th><th>{m.about_col_provider()}</th><th>{m.about_col_use()}</th></tr></thead>
        <tbody>
          {#each sources as s (s.id)}
            <tr data-source={s.id}><th scope="row">{s.name()}</th><td>{s.provider}</td><td class="use">{s.use()}</td></tr>
          {/each}
        </tbody>
      </table>
    </div>
  </section>

  <section id="ai">
    <h2>{m.about_s5()}</h2>
    <p>{m.about_s5_p1()}</p>
    <p>{m.about_s5_p2()}</p>
  </section>

  <section id="software">
    <h2>{m.about_s6()}</h2>
    <p>{m.about_s6_p1()}</p>
    <p><a href="https://github.com/sebastianvelace/Breathing-Comets" rel="external">{m.about_s6_link()}</a></p>
  </section>
</main>
<footer>{m.method_credits()}<LegalLinks /></footer>

<style>
  header{display:flex;justify-content:space-between;gap:24px;padding:24px var(--gutter);border-bottom:1px solid var(--rule)}nav{display:flex;gap:24px;flex-wrap:wrap}
  main{max-width:760px;margin:auto;padding:56px var(--gutter)}h1{font-size:clamp(44px,6vw,72px)}.intro{font-size:20px;color:var(--ink-2)}section{margin:60px 0}h2{font-size:clamp(28px,3.4vw,40px);margin-bottom:16px}
  main p,li{font-size:17px;line-height:1.68;color:var(--ink-2)}a{color:var(--accent)}.links{padding-left:20px}.links li{margin-bottom:10px}.scroll{overflow:auto;margin-top:18px}
  table{width:100%;border-collapse:collapse;text-align:left;font-size:14px}th{font-weight:500;color:var(--ink)}thead th{font:12px var(--font-data);color:var(--graphite);font-weight:400}td,th{padding:12px 12px 12px 0;border-bottom:1px solid var(--rule);vertical-align:top}.use{color:var(--ink-2)}
  @media(max-width:700px){header{flex-wrap:wrap}h1{font-size:44px}td,th{min-width:150px}}
</style>
