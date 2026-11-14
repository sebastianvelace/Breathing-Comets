<script lang="ts">
  import { neo, neoObjects } from '#lib/data/neo.js';
  import validation from '../../../static/data/neo/validation.json';
  import diameters from '../../../static/data/neo/validation_diameters.json';
  import NeoPlot from '#lib/components/NeoPlot.svelte';
  import SpectrumPlot from '#lib/components/SpectrumPlot.svelte';
  import type { SpectrumPoint } from '#lib/data/types.js';
  import { getLocale, localizeHref } from '#lib/paraglide/runtime.js';
  import * as m from '#lib/paraglide/messages.js';
  let filter = $state(''), tier = $state(''), selected = $state('');
  let points = $state.raw<(SpectrumPoint & {ra: number; dec: number})[]>([]);
  let loading = $state(false), error = $state(false);
  const rows = $derived(neoObjects.filter(o => (!tier || o.tier === tier) && o.pdes.toLowerCase().includes(filter.toLowerCase())));
  const object = $derived(neoObjects.find(o => o.slug === selected));
  const percent = (value: number) => (value * 100).toFixed(0);
  $effect(() => {
    if (!selected) return;
    const controller = new AbortController();
    points = []; error = false; loading = true;
    fetch('/data/neo/' + selected + '.json', {signal: controller.signal})
      .then(r => {if (!r.ok) throw new Error(String(r.status)); return r.json();})
      .then(data => points = data.points)
      .catch(e => {if(e.name !== 'AbortError') error = true;})
      .finally(() => {if (!controller.signal.aborted) loading = false;});
    return () => controller.abort();
  });
</script>

<svelte:head>
  <title>{m.neo_title()} · Breathing Comets</title>
  <meta name="description" content={m.neo_intro()}/>
  <link rel="canonical" href={'https://breathingcomets.org' + localizeHref('/neo')}/>
  <link rel="alternate" hreflang="en" href="https://breathingcomets.org/neo"/>
  <link rel="alternate" hreflang="es" href="https://breathingcomets.org/es/neo"/>
</svelte:head>
<header><a class="brand" href={localizeHref('/')}>BREATHING COMETS</a><nav><a href={localizeHref('/explore')}>{m.open_sky()}</a><a lang={getLocale() === 'en' ? 'es' : 'en'} href={localizeHref('/neo', {locale: getLocale() === 'en' ? 'es' : 'en'})}>{getLocale() === 'en' ? 'ES' : 'EN'}</a></nav></header>
<main>
  <h1>{m.neo_title()}</h1><p class="intro">{m.neo_intro()}</p>
  <p class="mono">{m.neo_counts({a: neo.counts.A, b: neo.counts.B, p: neo.counts.provisional, pha: neo.counts.pha_AB})}</p>
  <section class="plots">
    <div><h2>{m.neo_dh()}</h2><NeoPlot objects={neoObjects} validation={diameters.points} kind="catalog" {selected} onselect={slug => selected = slug}/><p class="muted">{m.neo_plot_note()}</p></div>
    <div><h2>{m.neo_validation_title()}</h2><p>{m.neo_validation_summary({lower: percent(1-neo.method.cv_p16), upper: percent(neo.method.cv_p84-1), n: neo.method.cv_n})}</p>
      {#if diameters.points.length}<NeoPlot objects={neoObjects} validation={diameters.points} kind="validation" {selected} onselect={() => {}}/>{/if}
      {#if diameters.points.length < neo.method.cv_n}<p class="caveat" data-testid="neo-reference-caveat">{m.neo_validation_missing({available: diameters.points.length, total: neo.method.cv_n})}</p>{/if}
      <details><summary>{m.neo_ratio_table()}</summary><div class="scroll"><table><thead><tr><th>{m.neo_object()}</th><th>{m.neo_ratio()}</th></tr></thead><tbody>{#each validation.cv as row}<tr><td>{row.key}</td><td>{row.D_ratio.toFixed(3)}</td></tr>{/each}</tbody></table></div></details>
    </div>
  </section>
  <section><h2>{m.neo_catalog()}</h2>
    <div class="filters"><label>{m.neo_search()}<input type="search" bind:value={filter}/></label><label>{m.neo_tier()}<select bind:value={tier}><option value="">{m.neo_all()}</option><option>A</option><option>B</option><option value="provisional">{m.neo_provisional()}</option></select></label></div>
    <p>{m.neo_floor({percent: percent(neo.method.floor_fraction)})}</p>
    <div class="scroll"><table class="catalog"><thead><tr><th>{m.neo_object()}</th><th>{m.neo_diameter()}</th><th>{m.neo_interval()}</th><th>{m.neo_tier()}</th><th>H / pV</th></tr></thead><tbody>
      {#each rows as o}<tr id={'neo-'+o.slug} class:chosen={selected === o.slug} data-testid="neo-size-row" data-slug={o.slug}>
        <td><button onclick={() => selected = o.slug} aria-pressed={selected === o.slug}>{o.pdes}</button>{#if o.pha}<span class="badge" title={m.neo_hazard()}>PHA</span>{/if}{#if o.single_visit}<span class="badge" data-testid="single-visit">{m.neo_single()}</span>{/if}</td>
        <td data-testid="diameter">{o.D_km.toFixed(3)} km<span class="floor">±{percent(neo.method.floor_fraction)}%</span></td>
        <td data-testid="interval">{o.D16.toFixed(3)}–{o.D84.toFixed(3)} km</td><td data-testid="tier">{o.tier === 'provisional' ? m.neo_provisional() : o.tier}</td><td>{o.H.toFixed(2)} / {o.pV.toFixed(3)}</td>
      </tr>{/each}
    </tbody></table></div>{#if !rows.length}<p>{m.neo_no_match()}</p>{/if}
  </section>
  <section class="inspection" aria-live="polite"><h2>{object?.pdes ?? m.neo_points()}</h2>
    {#if object}<p>{m.neo_observations({n: object.n_exp, visits: object.n_visits, snr: object.snr})}</p><p class="mono">{object.D_km.toFixed(3)} [{object.D16.toFixed(3)}–{object.D84.toFixed(3)}] km · {m.neo_tier()} {object.tier === 'provisional' ? m.neo_provisional() : object.tier} · ±{percent(neo.method.floor_fraction)}%</p>
      {#if object.single_visit}<p class="caveat">{m.neo_single_note()}</p>{/if}{#if object.flag}<p class="caveat">{m.neo_low_albedo()}</p>{/if}
      {#if loading}<p>{m.neo_loading()}</p>{:else if error}<p role="alert">{m.neo_error()}</p>{:else if points.length}<SpectrumPlot {points} label={object.pdes + ' · ' + m.neo_points()}/><a href={localizeHref('/explore') + `?ra=${points[0].ra.toFixed(6)}&dec=${points[0].dec.toFixed(6)}&ui=lab`}>{m.neo_view_sky()}</a>{/if}
    {:else}<p>{m.neo_selection()}</p>{/if}
  </section>
  <section class="method"><h2>{m.neo_method()}</h2><p>{m.neo_method_text({model: neo.method.model, eta: neo.method.eta, sigma: neo.method.eta_sigma, trail: neo.method.trail_max_px})}</p><p>{neo.method.photometry}</p><a href={diameters.source}>{m.neo_source()}</a> · <a href="/data/neo/index.json" download>{m.neo_download()}</a></section>
</main>
<footer>SPHEREx: NASA/JPL-Caltech/IRSA · NEOWISE: NASA/JPL-Caltech/IPAC</footer>

<style>
header{display:flex;justify-content:space-between;gap:24px;padding:24px var(--gutter);border-bottom:1px solid var(--rule)}nav{display:flex;gap:24px}main{max-width:1440px;margin:auto;padding:64px var(--gutter)}.intro{max-width:640px;font-size:20px}.plots{display:grid;grid-template-columns:1fr 1fr;gap:48px;margin-top:56px}.plots>div{min-width:0}section{margin-bottom:56px}h2{font-size:32px}.caveat{border-left:2px solid var(--accent);padding-left:14px;font-size:14px}.filters{display:flex;gap:24px;flex-wrap:wrap;margin-bottom:16px}label{display:grid;gap:6px}.scroll{overflow:auto}table{width:100%;border-collapse:collapse;text-align:left;font:12px var(--font-data)}th{font-weight:400;color:var(--graphite)}td,th{padding:12px 10px;border-bottom:1px solid var(--rule);white-space:nowrap}.catalog button{padding:3px 0;min-height:40px;border:0;text-align:left;color:var(--accent);text-decoration:underline;text-underline-offset:4px}.catalog button[aria-pressed=true]{background:transparent;color:var(--signal)}.chosen{background:var(--paper-2)}.badge,.floor{display:block;color:var(--graphite);font-size:11px}.inspection{max-width:800px}.method{max-width:680px;font-size:15px}details .scroll{max-height:250px}@media(max-width:850px){.plots{grid-template-columns:1fr;gap:28px}main{padding-top:40px}header{flex-wrap:wrap}.brand{font-size:12px}nav{font-size:14px}h1{font-size:44px}}
</style>
