<script lang="ts">
  import LegalLinks from "#lib/components/LegalLinks.svelte";
  import ProductNav from "#lib/components/ProductNav.svelte";
  import build from "../../../static/data/build.json";
  import calibration from "../../../static/data/calibration.json";
  import channelData from "../../../static/data/channels.json";
  import atlas from "../../../static/data/comets/index.json";
  import neo from "../../../static/data/neo/index.json";
  import diameters from "../../../static/data/neo/validation_diameters.json";
  import { landingMedia } from "#lib/components/landing/landing.js";
  import { fmtSciUnicode } from "#lib/data/format.js";
  import { comaModel, diffLambda, instrument, maskedFlags, photometry } from "#lib/data/method.js";
  import { getLocale, localizeHref } from "#lib/paraglide/runtime.js";
  import * as m from "#lib/paraglide/messages.js";

  const other = getLocale() === "en" ? "es" : "en";
  // Integers only, grouped with a narrow no-break space: no locale API, no ambiguous commas.
  const fmt = (n: number) => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, "\u202f");
  const channels = channelData.channels;
  const detectors = [1, 2, 3, 4, 5, 6].map((d) => {
    const c = channels.filter((x) => x.detector === d);
    return {
      d,
      lo: Math.min(...c.map((x) => x.wl_min_um)),
      hi: Math.max(...c.map((x) => x.wl_max_um)),
      n: c.length,
      r: [Math.min(...c.map((x) => x.R)), Math.max(...c.map((x) => x.R))],
      shift: (calibration.wavelength_shift_v27_minus_v20_nm as Record<string, number>)[`D${d}`],
    };
  });
  const bandShift = calibration.wavelength_shift_v27_minus_v20_nm.D5.toFixed(1);
  const barnard = landingMedia.plates.barnard;
  const diff = barnard.difference;
  const counts = atlas.counts as Record<string, number>;
  const percent = (x: number) => (x * 100).toFixed(0);
  const w = (k: [number, number]) => k.map((v) => v.toFixed(2));
  const sections = [
    { n: 1, title: m.method_s1 }, { n: 2, title: m.method_s2 }, { n: 3, title: m.method_s3 },
    { n: 4, title: m.method_s4 }, { n: 5, title: m.method_s5 }, { n: 6, title: m.method_s6 },
    { n: 7, title: m.method_s7 }, { n: 8, title: m.method_s8 }, { n: 9, title: m.method_s9 },
    { n: 10, title: m.method_s10 },
  ];
</script>

<svelte:head>
  <title>{m.method_title()} · Breathing Comets</title>
  <meta name="description" content={m.method_intro()} />
  <link rel="canonical" href={"https://breathingcomets.org" + localizeHref("/method")} />
  <link rel="alternate" hreflang="en" href="https://breathingcomets.org/method" />
  <link rel="alternate" hreflang="es" href="https://breathingcomets.org/es/method" />
</svelte:head>

<header class="product-header">
  <a class="brand" href={localizeHref("/")}>BREATHING COMETS</a>
    <div class="product-navigation"><ProductNav /></div>
  <nav>
    <a href={localizeHref("/about")}>{m.about_title()}</a>
    <a lang={other} href={localizeHref("/method", { locale: other })} data-sveltekit-reload>{other.toUpperCase()}</a>
  </nav>
</header>

<div class="layout">
  <aside aria-label={m.method_toc()}>
    <p class="mono toc-title">{m.method_toc()}</p>
    <ol>
      {#each sections as s (s.n)}<li><a href="#s{s.n}">{s.title()}</a></li>{/each}
    </ol>
  </aside>

  <main>
    <h1>{m.method_title()}</h1>
    <p class="intro">{m.method_intro()}</p>

    <section id="s1">
      <h2>{m.method_s1()}</h2>
      <p>{m.method_s1_p1({ l2: build.data_version.l2, rows: fmt(build.exposure_index.rows_d4_d6), keys: fmt(build.exposure_index.s3_keys) })}</p>
      <p>{m.method_s1_p2()}</p>
    </section>

    <section id="s2">
      <h2>{m.method_s2()}</h2>
      <p>{m.method_s2_p1({ pixel: instrument.pixel_arcsec.toFixed(2), n: channels.length, lo: channels[0].wavelength_um.toFixed(2), hi: channels[channels.length - 1].wavelength_um.toFixed(2), exposure: instrument.exposure_s })}</p>
      <div class="scroll">
        <table data-testid="method-detectors">
          <thead><tr><th>{m.method_s2_col_det()}</th><th class="r">{m.method_s2_col_range()}</th><th class="r">{m.method_s2_col_channels()}</th><th class="r">{m.method_s2_col_r()}</th></tr></thead>
          <tbody>
            {#each detectors as x (x.d)}
              <tr><th scope="row">D{x.d}</th><td class="r">{x.lo.toFixed(2)}–{x.hi.toFixed(2)}</td><td class="r">{x.n}</td><td class="r">{x.r[0].toFixed(0)}–{x.r[1].toFixed(0)}</td></tr>
            {/each}
          </tbody>
        </table>
      </div>
    </section>

    <section id="s3">
      <h2>{m.method_s3()}</h2>
      <p>{m.method_s3_p1({ swcs: build.data_version.spectral_wcs, edge: photometry.edge_margin_px })}</p>
      <p>{m.method_s3_p2({ shift: bandShift })}</p>
      <div class="scroll">
        <table data-testid="method-shift">
          <thead><tr><th>{m.method_s3_col()}</th><th class="r">{m.method_s3_shift()}</th></tr></thead>
          <tbody>{#each detectors as x (x.d)}<tr><th scope="row">D{x.d}</th><td class="r">{x.shift === 0 ? "0.0" : "+" + x.shift.toFixed(1)}</td></tr>{/each}</tbody>
        </table>
      </div>
    </section>

    <section id="s4">
      <h2>{m.method_s4()}</h2>
      <p>{m.method_s4_p1({ k: diffLambda.references, bw: diffLambda.window_bandwidths, min: diffLambda.min_references })}</p>
      <p>{m.method_s4_p2({ mad: diffLambda.mad_scale })}</p>
      <figure class="pair">
        <div class="pic"><img src={diff.raw.src} width={diff.raw.width} height={diff.raw.height} alt={m.method_s4_alt_raw()} loading="lazy" /></div>
        <div class="pic"><img src={diff.diff_lambda.src} width={diff.diff_lambda.width} height={diff.diff_lambda.height} alt={m.method_s4_alt_diff()} loading="lazy" /></div>
        <figcaption class="mono">{m.method_s4_cap({ det: diff.diff_lambda.det })} {landingMedia.credits[0]}</figcaption>
      </figure>
      <p>{m.method_s4_p3()}</p>
    </section>

    <section id="s5">
      <h2>{m.method_s5()}</h2>
      <p>{m.method_s5_p1({ r: photometry.radius_px, flags: maskedFlags.join(", ") })}</p>
      <p>{m.method_s5_p2({ floor: photometry.floor_pct })}</p>
      <p>{m.method_s5_p3({ n: calibration.n_stars, fields: calibration.fields.join(", ").toUpperCase() })}</p>
      <div class="scroll">
        <table data-testid="method-photometry">
          <thead><tr><th>{m.method_s5_col_band()}</th><th class="r">{m.method_s5_col_n()}</th><th class="r">{m.method_s5_col_ratio()}</th></tr></thead>
          <tbody>{#each calibration.validation as v (v.band)}<tr><th scope="row" class="mono">{v.band}</th><td class="r">{v.n}</td><td class="r">{v.ratio.toFixed(3)} ± {v.sigma.toFixed(3)}</td></tr>{/each}</tbody>
        </table>
      </div>
      <p>{m.method_s5_p4({ mean: calibration.ratio_mean.toFixed(3), min: calibration.ratio_min.toFixed(3), max: calibration.ratio_max.toFixed(3) })}</p>
    </section>

    <section id="s6">
      <h2>{m.method_s6()}</h2>
      <p>{m.method_s6_p1({ co_lo: comaModel.windows_um.co_d6[0].toFixed(2), co_hi: comaModel.windows_um.co_d6[1].toFixed(2), h2o_lo: comaModel.windows_um.h2o_d4[0].toFixed(2), h2o_hi: comaModel.windows_um.h2o_d4[1].toFixed(2), co2_lo: comaModel.windows_um.co2_d5[0].toFixed(2), co2_hi: comaModel.windows_um.co2_d5[1].toFixed(2) })}</p>
      <p>{m.method_s6_p2({ ap: comaModel.aperture_px, ring_lo: comaModel.background_ring_px[0], ring_hi: comaModel.background_ring_px[1], low: comaModel.speed_low_km_s_at_1au.toFixed(2), speed: comaModel.speed_km_s_at_1au.toFixed(2) })}</p>
      <div class="scroll">
        <table data-testid="method-constants">
          <thead><tr><th>{m.method_s6_col_const()}</th><th class="r">{m.method_s6_col_value()}</th></tr></thead>
          <tbody>
            <tr><th scope="row">{m.method_s6_g()} CO₂</th><td class="r mono">{fmtSciUnicode(comaModel.g_co2_1au)} s⁻¹</td></tr>
            <tr><th scope="row">{m.method_s6_g()} CO</th><td class="r mono">{fmtSciUnicode(comaModel.g_co_1au)} s⁻¹</td></tr>
            <tr><th scope="row">{m.method_s6_g()} H₂O</th><td class="r mono">{fmtSciUnicode(comaModel.g_h2o_1au)} s⁻¹</td></tr>
            <tr><th scope="row">{m.method_s6_tau()} CO₂</th><td class="r mono">{fmtSciUnicode(comaModel.tau_co2_quiet_s)} s ({fmtSciUnicode(comaModel.tau_co2_active_s)} s)</td></tr>
            <tr><th scope="row">{m.method_s6_tau()} CO</th><td class="r mono">{fmtSciUnicode(comaModel.tau_co_s)} s</td></tr>
            <tr><th scope="row">{m.method_s6_tau()} H₂O</th><td class="r mono">{fmtSciUnicode(comaModel.tau_h2o_s)} s</td></tr>
          </tbody>
        </table>
      </div>
      <p>{m.method_s6_p3({ draws: fmt(comaModel.monte_carlo_draws), cal: comaModel.calibration_pct, g: comaModel.g_pct, tau: comaModel.tau_lognormal, v: comaModel.speed_lognormal })}</p>
      <p data-testid="method-status">{m.method_s6_p4({ detected: counts.detected, systematics: counts.with_systematics, marginal: counts.marginal, none: counts.not_detected, n: counts.comets })}</p>
      <p><a href={localizeHref("/comets")}>{m.method_s6_link()}</a></p>
    </section>

    <section id="s7">
      <h2>{m.method_s7()}</h2>
      <p>{m.method_s7_p1()}</p>
      <p data-testid="method-neo">{m.method_s7_p2({ eta: neo.method.eta, sigma: neo.method.eta_sigma, cv_n: neo.method.cv_n, p16: neo.method.cv_p16.toFixed(2), p84: neo.method.cv_p84.toFixed(2), lo: percent(1 - neo.method.cv_p16), hi: percent(neo.method.cv_p84 - 1), median: neo.method.cv_median.toFixed(2), floor: percent(neo.method.floor_fraction) })}</p>
      <p>{m.method_s7_p3({ avail: diameters.points.length, total: neo.method.cv_n })}</p>
      <p><a href={localizeHref("/neo")}>{m.method_s7_link()}</a></p>
    </section>

    <section id="s8">
      <h2>{m.method_s8()}</h2>
      <p>{m.method_s8_p1()}</p>
      <p class="caveat">{m.method_s8_p2()}</p>
    </section>

    <section id="s9">
      <h2>{m.method_s9()}</h2>
      <ul>
        <li>{m.method_s9_l1()}</li><li>{m.method_s9_l2()}</li><li>{m.method_s9_l3()}</li><li>{m.method_s9_l4()}</li><li>{m.method_s9_l5()}</li>
      </ul>
    </section>

    <section id="s10">
      <h2>{m.method_s10()}</h2>
      <p>{m.method_s10_p1({ commit: build.git.commit.slice(0, 7) })}</p>
      <div class="scroll">
        <table data-testid="method-build">
          <thead><tr><th>{m.method_s10_col()}</th><th class="r">{m.method_s10_val()}</th></tr></thead>
          <tbody>
            <tr><th scope="row">{m.method_s10_data()}</th><td class="r mono">{build.data_version.releases.join(" + ").toUpperCase()} · {build.data_version.l2}</td></tr>
            <tr><th scope="row">{m.method_s10_swcs()}</th><td class="r mono">{build.data_version.spectral_wcs}</td></tr>
            <tr><th scope="row">{m.method_s10_index()}</th><td class="r mono">{fmt(build.exposure_index.rows_d4_d6)}</td></tr>
            <tr><th scope="row">{m.method_s10_stacks()}</th><td class="r mono">{build.products.stacks}</td></tr>
            <tr><th scope="row">{m.method_s10_generated()}</th><td class="r mono">{build.generated}</td></tr>
          </tbody>
        </table>
      </div>
      <p><a href="/data/build.json" download>{m.method_s10_download()}</a> · <a href="https://github.com/sebastianvelace/Breathing-Comets" rel="external">{m.method_s10_repo()}</a></p>
    </section>
  </main>
</div>
<footer>{m.method_credits()}<LegalLinks /></footer>

<style>
  header{display:flex;justify-content:space-between;gap:24px;padding:24px var(--gutter);border-bottom:1px solid var(--rule)}nav{display:flex;gap:24px;flex-wrap:wrap}
  .layout{display:grid;grid-template-columns:240px minmax(0,1fr);gap:clamp(24px,5vw,80px);max-width:1180px;margin:auto;padding:56px var(--gutter)}
  aside{position:sticky;top:24px;align-self:start;font-size:14px}.toc-title{color:var(--graphite);margin-bottom:10px}aside ol{list-style:none;margin:0;padding:0;display:grid;gap:2px}aside a{display:block;padding:7px 0 7px 12px;border-left:1px solid var(--rule);color:var(--ink-2);text-decoration:none;transition:color 200ms var(--ease),border-color 200ms var(--ease)}aside a:hover{color:var(--accent);border-color:var(--accent)}
  main{max-width:720px;min-width:0}.intro{font-size:20px;color:var(--ink-2)}section{margin:64px 0;scroll-margin-top:24px}h1{font-size:clamp(44px,6vw,72px)}h2{font-size:clamp(28px,3.4vw,40px);margin-bottom:18px}
  main p,li{font-size:17px;line-height:1.68;color:var(--ink-2)}li{margin-bottom:8px}a{color:var(--accent)}.scroll{overflow:auto;margin:18px 0}
  table{width:100%;border-collapse:collapse;text-align:left;font:13px var(--font-data);font-variant-numeric:tabular-nums}th{font-weight:400;color:var(--graphite)}td,th{padding:10px 8px;border-bottom:1px solid var(--rule);white-space:nowrap}.r{text-align:right}tbody th{color:var(--ink)}
  .pair{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:22px 0}.pic{background:var(--plate);border:1px solid var(--rule);padding:8px;line-height:0}.pic img{width:100%;height:auto;image-rendering:pixelated}.pair figcaption{grid-column:1/-1;color:var(--graphite)}
  .caveat{border-left:2px solid var(--accent);padding-left:14px}
  @media(max-width:900px){.layout{grid-template-columns:minmax(0,1fr)}aside{display:none}header{flex-wrap:wrap}h1{font-size:44px}}
</style>
