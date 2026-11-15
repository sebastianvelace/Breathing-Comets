<script lang="ts">
  import LegalLinks from "#lib/components/LegalLinks.svelte";
  import ProductNav from "#lib/components/ProductNav.svelte";
  import {onMount} from 'svelte';
  let mounted = $state(false);
  onMount(() => {mounted = true;});
  import { cometAtlas, classLabel, STATUSES, statusLabel, velocityDropPercent, type CometStatus } from "#lib/data/comets.js";
  import { fmtSciUnicode } from "#lib/data/format.js";
  import CometPlot from "#lib/components/CometPlot.svelte";
  import { getLocale, localizeHref } from "#lib/paraglide/runtime.js";
  import * as m from "#lib/paraglide/messages.js";

  let filter = $state(""), status = $state(""), selected = $state("");
  const rows = $derived(
    cometAtlas.comets.filter((c) => (!status || c.co2.status === status) && c.name.toLowerCase().includes(filter.toLowerCase())),
  );
  const chosen = $derived(cometAtlas.comets.find((c) => c.slug === selected));
  const drop = velocityDropPercent(cometAtlas.comets);
  const label = (s: string) => statusLabel(s as CometStatus);
  const klass = classLabel;
  const pick = (slug: string) => {
    selected = slug === selected ? "" : slug;
    if (selected) document.getElementById(`comet-${slug}`)?.scrollIntoView?.({ block: "nearest" });
  };
  const sig = (v: number | null | undefined, d = 2) => (v === null || v === undefined ? "—" : v.toFixed(d));
  const other = getLocale() === "en" ? "es" : "en";
  const detailSlugs = ["3i-atlas", "29p-schwassmann-wachmann"];
  const co2Count = (s: string) => (cometAtlas.counts as Record<string, number>)[s];
</script>

<svelte:head>
  <title>{m.comets_title()} · Breathing Comets</title>
  <meta name="description" content={m.comets_intro()} />
  <link rel="canonical" href={"https://breathingcomets.org" + localizeHref("/comets")} />
  <link rel="alternate" hreflang="en" href="https://breathingcomets.org/comets" />
  <link rel="alternate" hreflang="es" href="https://breathingcomets.org/es/comets" />
</svelte:head>

<header class="product-header">
  <a class="brand" href={localizeHref("/")}>BREATHING COMETS</a>
    <div class="product-navigation"><ProductNav active="comets" /></div>
  <nav>
    <a lang={other} href={localizeHref("/comets", { locale: other })} data-sveltekit-reload>{other.toUpperCase()}</a>
  </nav>
</header>

<main>
  <h1>{m.comets_title()}</h1>
  <p class="intro">{m.comets_intro()}</p>
  <p class="mono" data-testid="comet-counts">
    {m.comets_counts({ n: cometAtlas.counts.comets, detected: co2Count("detected"), systematics: co2Count("with_systematics"), marginal: co2Count("marginal"), none: co2Count("not_detected") })}
  </p>

  <div class="featured-comets">
    <p>{m.comets_overview()}</p>
    <a href={localizeHref('/comets/3i-atlas')}>3I/ATLAS →</a>
    <a href={localizeHref('/comets/29p-schwassmann-wachmann')}>29P →</a>
  </div>
  <section class="honesty" aria-label={m.comets_honesty_title()}>
    <p>{m.comets_honesty_census()}</p>
    <details><summary>{m.comets_limits_toggle()}</summary><ul>
      <li data-testid="velocity-note">{m.comets_honesty_velocity({ percent: drop })}</li>
      <li>{m.comets_honesty_far({ au: cometAtlas.method.far_au })}</li>
      <li>{m.comets_honesty_systematics()}</li>
    </ul></details>
  </section>

  <section class="chart">
    <h2>{m.comets_chart()}</h2>
    <CometPlot comets={rows} {selected} onselect={pick} />
    <div class="inspection" aria-live="polite">
      {#if chosen}
        {#if chosen.co2.status === "with_systematics"}<p class="caveat">{m.comets_honesty_systematics()}</p>{/if}
        {#if chosen.flags.includes("far_unreliable")}<p class="caveat">{m.comets_honesty_far({au:cometAtlas.method.far_au})}</p>{/if}
        <h3>{m.comets_detail({ name: chosen.name, r: sig(chosen.r_au), delta: sig(chosen.delta_au) })}</h3>
        <p class="mono">{m.comets_detail_q({ q50: fmtSciUnicode(chosen.co2.q50), q16: fmtSciUnicode(chosen.co2.q16), q84: fmtSciUnicode(chosen.co2.q84), alt_tau: fmtSciUnicode(chosen.co2.q50_alt_tau_g), alt_v: fmtSciUnicode(chosen.co2.q50_alt_velocity) })}</p>
        <p class="mono">{m.comets_detail_diag({ snr: sig(chosen.co2.snr_det, 1), err: sig(chosen.co2.flux_rel_err, 3), core: chosen.co2.n_core, chi2: sig(chosen.co2.chi2_red, 1), t: chosen.co2.t_rot_k ?? "—" })}</p>
        {#if chosen.flags.includes("far_unreliable")}<p class="caveat">{m.comets_honesty_far({ au: cometAtlas.method.far_au })}</p>{/if}
        {#if chosen.co2.status === "with_systematics"}<p class="caveat">{m.comets_honesty_systematics()}</p>{/if}
        {#if chosen.flags.includes("zero_core")}<p class="caveat">{m.comets_honesty_zero_core()}</p>{/if}
      {:else}<p class="muted">{m.comets_pick()}</p>{/if}
    </div>
  </section>

  <section>
    <h2>{m.comets_table()}</h2>
    <div class="filters">
      <label>{m.comets_filters_search()}<input type="search" bind:value={filter} disabled={!mounted} /></label>
      <label>{m.comets_filters_status()}
        <select bind:value={status} disabled={!mounted}><option value="">{m.comets_all()}</option>{#each STATUSES as s (s)}<option value={s}>{label(s)}</option>{/each}</select>
      </label>
    </div>
    <div class="scroll">
      <table class="catalog">
        <thead><tr>
          <th>{m.comets_col_comet()}</th><th class="r">{m.comets_col_r()}</th><th class="r">{m.comets_col_delta()}</th>
          <th class="r">{m.comets_col_q()}</th><th class="r">{m.comets_col_snr()}</th><th class="r">{m.comets_col_err()}</th>
          <th class="r">{m.comets_col_core()}</th><th class="r">{m.comets_col_chi2()}</th><th>{m.comets_col_status()}</th>
          <th>{m.comets_col_co()}</th><th>{m.comets_col_h2o()}</th>
        </tr></thead>
        <tbody>
          {#each rows as c (c.slug)}
            <tr id="comet-{c.slug}" class:chosen={selected === c.slug} data-testid="comet-row" data-slug={c.slug} data-status={c.co2.status}>
              <td><button disabled={!mounted} onclick={() => pick(c.slug)} aria-pressed={selected === c.slug}>{c.name}</button>
                {#if detailSlugs.includes(c.slug)}<a class="badge" href={localizeHref(`/comets/${c.slug}`)} data-testid="detail-link">{m.comets_open_detail()}</a>{/if}
                {#if c.flags.includes("far_unreliable")}<span class="badge">{m.comets_flag_far()}</span>{/if}
                {#if c.flags.includes("zero_core")}<span class="badge" data-testid="zero-core">{m.comets_flag_zero_core()}</span>{/if}</td>
              <td class="r">{sig(c.r_au)}</td><td class="r">{sig(c.delta_au)}</td>
              <td class="r" data-testid="q">{fmtSciUnicode(c.co2.q16)} · <b>{fmtSciUnicode(c.co2.q50)}</b> · {fmtSciUnicode(c.co2.q84)}</td>
              <td class="r">{sig(c.co2.snr_det, 1)}</td><td class="r">{sig(c.co2.flux_rel_err, 3)}</td>
              <td class="r">{c.co2.n_core}</td><td class="r">{sig(c.co2.chi2_red, 1)}</td>
              <td data-testid="status">{label(c.co2.status)}</td>
              <td>{#if c.co}{klass(c.co.class)}{#if c.co.class === "candidate" || c.co.class === "robust_detection"}<span class="badge">{m.comets_co_ratio({ ratio: sig(c.co.ratio_co_co2, 1) })}</span>{/if}{:else}—{/if}</td>
              <td>{#if c.h2o}{klass(c.h2o.class)}{#if c.h2o.class === "detection"}<span class="badge">{fmtSciUnicode(c.h2o.q50)}</span>{/if}{:else}—{/if}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
    {#if !rows.length}<p>{m.comets_no_match()}</p>{/if}
  </section>

  <section class="validation" aria-labelledby="val-title">
    <h2 id="val-title">{m.comets_validation()}</h2>
    <p>{m.comets_validation_intro()}</p>
    <div class="scroll">
      <table data-testid="comet-validation">
        <thead><tr><th>{m.comets_val_col_result()}</th><th class="r">{m.comets_val_col_measured()}</th><th class="r">{m.comets_val_col_published()}</th><th>{m.comets_val_col_check()}</th></tr></thead>
        <tbody>
          {#each cometAtlas.validation as v (v.id)}
            {@const inside = v.measured >= v.published_lo && v.measured <= v.published_hi}
            <tr>
              <th scope="row">{v.comet} · {v.species === "CO2" ? "CO₂" : v.species} · {v.epoch}</th>
              <td class="r mono">{fmtSciUnicode(v.measured)} s⁻¹</td>
              <td class="r mono">{fmtSciUnicode(v.published_lo)}–{fmtSciUnicode(v.published_hi)}</td>
              <td data-testid="check"><span class:ok={inside} class:off={!inside}>{inside ? m.comets_val_inside() : m.comets_val_outside()}</span></td>
            </tr>
            <tr class="sub"><td colspan="4">
              {#if v.species === "CO2"}
                {m.comets_val_stat({ err: fmtSciUnicode(v.stat_err), chi2: sig(v.chi2_red, 1), lo: fmtSciUnicode(v.measured_lo), hi: fmtSciUnicode(v.measured_hi) })}
                <br />{m.comets_val_interval_source()}
              {:else}
                {m.comets_val_co_ratio({ chi2: sig(v.chi2_red, 1), ratio: sig(v.ratio_co_co2, 1), lo: sig(v.ratio_16, 1), hi: sig(v.ratio_84, 1) })}
              {/if}
              <br /><span class="src">{v.source}</span>
            </td></tr>
          {/each}
        </tbody>
      </table>
    </div>
    {#each cometAtlas.pending as p (p.id)}<p class="caveat" data-testid="comet-pending">{m.comets_val_pending({ reason: p.reason })}</p>{/each}
  </section>

  <section class="method">
    <h2>{m.comets_method()}</h2>
    <p>{m.comets_method_text()}</p>
    <p class="mono">{cometAtlas.method.status_rule}</p>
    <p class="mono">{m.comets_sources({ sources: cometAtlas.method.sources.join(", ") })}</p>
    <a href="/data/comets/index.json" download>{m.comets_download()}</a> · <a href={localizeHref("/method")} data-testid="method-link">{m.method_title()}</a>
  </section>
</main>
<footer>{m.comets_credits()}<LegalLinks /></footer>

<style>
  header{display:flex;justify-content:space-between;gap:24px;padding:24px var(--gutter);border-bottom:1px solid var(--rule)}nav{display:flex;gap:24px;flex-wrap:wrap}main{max-width:1440px;margin:auto;padding:40px var(--gutter)}.intro{max-width:640px;font-size:20px}section{margin-bottom:56px}h2{font-size:32px}h3{font-size:22px}
  .honesty{max-width:760px;border-top:1px solid var(--ink);padding-top:12px;margin-top:32px}.honesty li{margin-bottom:8px;font-size:15px;color:var(--ink-2)}
  .chart{max-width:960px}.inspection{min-height:110px;margin-top:12px}.caveat{border-left:2px solid var(--accent);padding-left:14px;font-size:14px}
  .filters{display:flex;gap:24px;flex-wrap:wrap;margin-bottom:16px}label{display:grid;gap:6px}.scroll{overflow:auto}
  table{width:100%;border-collapse:collapse;text-align:left;font:12px var(--font-data)}th{font-weight:400;color:var(--graphite)}td,th{padding:12px 10px;border-bottom:1px solid var(--rule);white-space:nowrap}.r{text-align:right}
  .catalog button{padding:3px 0;min-height:40px;border:0;text-align:left;color:var(--accent);text-decoration:underline;text-underline-offset:4px}.catalog button[aria-pressed=true]{background:transparent;color:var(--signal)}.chosen{background:var(--paper-2)}.badge{display:block;color:var(--graphite);font-size:11px}
  .validation{max-width:960px}.validation tr.sub td{white-space:normal;color:var(--ink-2);padding-top:0}.src{color:var(--graphite)}.ok{color:var(--co)}.off{color:var(--signal)}
  .method{max-width:680px;font-size:15px}.method a{color:var(--accent)}
  @media(max-width:850px){main{padding-top:40px}header{flex-wrap:wrap}h1{font-size:44px}}

.featured-comets{display:flex;flex-wrap:wrap;gap:8px;margin:24px 0}.featured-comets p{flex:1 1 400px;max-width:70ch;color:var(--ink-2);margin-bottom:6px}.featured-comets a{display:inline-flex;align-items:center;min-height:42px;border:1px solid var(--rule);border-radius:var(--r-pill);padding:8px 18px;text-decoration:none;color:var(--accent)}.honesty p,.honesty li{font-size:14px}.honesty summary{font-weight:500}.honesty{margin-bottom:28px}
</style>
