<script lang="ts">
  import {onMount} from 'svelte';
  let mounted = $state(false);
  onMount(() => {mounted = true;});
  import Plate from "#lib/components/landing/Plate.svelte";
  import SpectrumPlot from "#lib/components/SpectrumPlot.svelte";
  import { classLabel, statusLabel, type CometStatus } from "#lib/data/comets.js";
  import { fmtSciUnicode } from "#lib/data/format.js";
  import { getLocale, localizeHref } from "#lib/paraglide/runtime.js";
  import * as m from "#lib/paraglide/messages.js";
  import type { PageProps } from "./$types";

  let { data }: PageProps = $props();
  const d = $derived(data.detail);
  const isoDate = (s: string) => s.slice(0, 10);
  const sig = (v: number | null | undefined, n = 2) => (v === null || v === undefined ? "—" : v.toFixed(n));

  let epochId = $state<string>("");
  let index = $state(0);
  let sweeping = $state(false);
  const epoch = $derived(d.epochs.find((e) => e.id === epochId) ?? d.epochs.find(e => e.id === "2025-08") ?? d.epochs[d.epochs.length - 1]);
  const frame = $derived(epoch.frames[Math.min(index, epoch.frames.length - 1)]);
  const spectra = $derived(d.spectrum.by_epoch[epoch.id]);
  const census = $derived(d.census);
  const other = getLocale() === "en" ? "es" : "en";

  // Start on the epoch that carries the validated figure (August for 3I), else the last one.
  $effect(() => {
    const first = d.epochs.find((e) => e.id === "2025-08") ?? d.epochs[d.epochs.length - 1];
    epochId = first.id;
    index = 0;
  });
  $effect(() => {
    epochId;
    index = 0;
    sweeping = false;
  });
  // Warm the browser cache for every frame of the epoch.
  $effect(() => {
    for (const f of epoch.frames) {
      const img = new Image();
      img.src = f.src;
    }
  });
  $effect(() => {
    if (!sweeping) return;
    const timer = window.setInterval(() => (index = (index + 1) % epoch.frames.length), 420);
    return () => window.clearInterval(timer);
  });

  const note = $derived(
    d.slug === "29p-schwassmann-wachmann"
      ? m.cd_29p_note()
      : epoch.id === "2025-08"
        ? m.cd_3i_note_aug()
        : m.cd_3i_note_dec(),
  );
</script>

<svelte:head>
  <title>{d.name} · {m.comets_title()} · Breathing Comets</title>
  <meta name="description" content={m.cd_plate_note()} />
  <link rel="canonical" href={"https://breathingcomets.org" + localizeHref(`/comets/${d.slug}`)} />
  <link rel="alternate" hreflang="en" href={`https://breathingcomets.org/comets/${d.slug}`} />
  <link rel="alternate" hreflang="es" href={`https://breathingcomets.org/es/comets/${d.slug}`} />
</svelte:head>

<header>
  <a class="brand" href={localizeHref("/")}>BREATHING COMETS</a>
  <nav>
    <a href={localizeHref("/comets")}>{m.cd_back()}</a>
    <a href={localizeHref("/explore")}>{m.open_sky()}</a>
    <a lang={other} href={localizeHref(`/comets/${d.slug}`, { locale: other })} data-sveltekit-reload>{other.toUpperCase()}</a>
  </nav>
</header>

<main>
  <h1>{d.name}</h1>
  <p class="intro">{note}</p>

  {#if d.epochs.length > 1}
    <div class="epochs" role="group" aria-label={m.cd_epochs()}>
      {#each d.epochs as e (e.id)}
        <button type="button" disabled={!mounted} aria-pressed={epoch.id === e.id} onclick={() => (epochId = e.id)} data-epoch={e.id}>{e.id}</button>
      {/each}
    </div>
  {/if}

  <section class="plate" aria-labelledby="plate-title">
    <h2 id="plate-title">{m.cd_plate()}</h2>
    <div class="plate-grid">
      <div>
        <Plate arcsecPerPx={epoch.grid.pixel_arcsec} viewPx={epoch.grid.nx} compass={epoch.grid.north_up} credit={d.credit}>
          <img
            src={frame.src}
            width={frame.width}
            height={frame.height}
            alt={m.cd_plate_alt({ name: d.name, lam: frame.lam_um.toFixed(2), date: isoDate(frame.date) })}
            data-testid="detail-frame"
            data-lam={frame.lam_um.toFixed(3)}
            data-band={frame.in_co2_band}
          />
          {#snippet caption()}
            <span>SPHEREx D{epoch.det} · {frame.lam_um.toFixed(2)} µm · {isoDate(frame.date)} · obs {frame.obs_id}</span>
            <span class:inband={frame.in_co2_band}>
              {frame.in_co2_band ? m.cd_in_band({ lo: d.co2_band_um[0].toFixed(2), hi: d.co2_band_um[1].toFixed(2) }) : m.cd_out_band()}
            </span>
          {/snippet}
        </Plate>
        <div class="controls">
          <label class="slider">
            <span>{m.cd_slider()}</span>
            <input type="range" disabled={!mounted} min="0" max={epoch.frames.length - 1} step="1" bind:value={index} aria-valuetext={`${frame.lam_um.toFixed(2)} µm`} />
          </label>
          <button type="button" disabled={!mounted} aria-pressed={sweeping} onclick={() => (sweeping = !sweeping)}>{sweeping ? m.cd_pause() : m.cd_sweep()}</button>
          <span class="mono">{m.cd_frame_of({ n: index + 1, total: epoch.frames.length })}</span>
        </div>
      </div>
      <p class="muted note">{m.cd_plate_note()}</p>
    </div>
  </section>

  <section aria-labelledby="spec-title">
    <h2 id="spec-title">{m.cd_spectrum_d5()}</h2>
    <p class="muted">{m.cd_spectrum_d5_note()}</p>
    <div class="spectrum" data-testid="detail-spectrum" data-points={spectra.d5.length}>
      <SpectrumPlot points={spectra.d5} label={`${d.name} · ${epoch.id} · D5`} />
    </div>
    {#if spectra.d6}
      <h2>{m.cd_spectrum_d6()}</h2>
      <p class="muted">{m.cd_spectrum_d6_note()}</p>
      <div class="spectrum" data-testid="detail-spectrum-co" data-points={spectra.d6.length}>
        <SpectrumPlot points={spectra.d6} label={`${d.name} · ${epoch.id} · D6`} />
      </div>
    {/if}
  </section>

  {#if epoch.id === "2025-12"}
    <section aria-labelledby="diag-title">
      <h2 id="diag-title">{m.cd_diag()}</h2>
      <p class="status" data-testid="detail-status" data-status={census.co2.status}>{m.cd_status({ status: statusLabel(census.co2.status as CometStatus) })}</p>
      <p class="big mono">{m.cd_q({ q50: fmtSciUnicode(census.co2.q50), q16: fmtSciUnicode(census.co2.q16), q84: fmtSciUnicode(census.co2.q84) })}</p>
      <p class="mono">{m.cd_diag_line({ snr: sig(census.co2.snr_det, 1), err: sig(census.co2.flux_rel_err, 3), core: census.co2.n_core, chi2: sig(census.co2.chi2_red, 1), t: census.co2.t_rot_k, r: sig(census.r_au), delta: sig(census.delta_au) })}</p>
      <p class="muted">{m.cd_q_alt({ alt_tau: fmtSciUnicode(census.co2.q50_alt_tau_g), alt_v: fmtSciUnicode(census.co2.q50_alt_velocity) })}</p>
      {#if census.aperture}
        <p class="muted">{m.cd_aperture({ q2: fmtSciUnicode(census.aperture.q_2px), q3: fmtSciUnicode(census.aperture.q_3px), q5: fmtSciUnicode(census.aperture.q_5px), q8: fmtSciUnicode(census.aperture.q_8px) })}</p>
      {/if}
      {#if census.co}
        <p class="mono">
          {#if census.co.ratio_co_co2 !== null && (census.co.class === "candidate" || census.co.class === "robust_detection")}
            {m.cd_co({ klass: classLabel(census.co.class), ratio: sig(census.co.ratio_co_co2, 1), lo: sig(census.co.ratio_16, 1), hi: sig(census.co.ratio_84, 1) })}
          {:else}{m.cd_co_none({ klass: classLabel(census.co.class) })}{/if}
        </p>
      {/if}
      {#if census.h2o}<p class="mono">{m.cd_h2o({ klass: classLabel(census.h2o.class) })}</p>{/if}
    </section>
  {/if}

  {#if d.validation.length}
    <section aria-labelledby="val-title">
      <h2 id="val-title">{m.cd_validation()}</h2>
      {#each d.validation as v (v.id)}
        {@const inside = v.measured >= v.published_lo && v.measured <= v.published_hi}
        <p class="mono" data-testid="detail-validation">
          {v.species === "CO2" ? "CO₂" : v.species} · {v.epoch}: {fmtSciUnicode(v.measured)} s⁻¹ ↔ {fmtSciUnicode(v.published_lo)}–{fmtSciUnicode(v.published_hi)} s⁻¹
          <span class:ok={inside} class:off={!inside}>({inside ? m.comets_val_inside() : m.comets_val_outside()})</span>
        </p>
        <p class="muted src">{v.source}</p>
      {/each}
    </section>
  {/if}

  <section class="prov" aria-labelledby="prov-title">
    <h2 id="prov-title">{m.cd_provenance()}</h2>
    <p>{m.cd_prov_track({ track: d.track })}</p>
    <p class="mono">{m.cd_prov_stack({ epoch: epoch.id, det: epoch.det, n: epoch.n_frames_stack, shown: epoch.frames.length })}</p>
    <details>
      <summary>{m.cd_prov_obs()}</summary>
      <p class="mono obs">{epoch.frames.map((f) => f.obs_id).join(" · ")}</p>
    </details>
    <p class="mono">{m.cd_prov_generated({ date: d.generated, generator: d.generator })}</p>
    <p>
      <a href={epoch.stack} download>{m.cd_download_stack()}</a> ·
      <a href={`/data/comets/${d.slug}.json`} download>{m.cd_download_json()}</a>
    </p>
  </section>
</main>
<footer>{m.comets_credits()}</footer>

<style>
  header{display:flex;justify-content:space-between;gap:24px;padding:24px var(--gutter);border-bottom:1px solid var(--rule)}nav{display:flex;gap:24px;flex-wrap:wrap}main{max-width:1280px;margin:auto;padding:56px var(--gutter)}.intro{max-width:640px;font-size:20px}section{margin:56px 0}h2{font-size:30px}
  .epochs{display:flex;gap:8px;margin:20px 0}.plate-grid{display:grid;grid-template-columns:minmax(0,520px) minmax(0,1fr);gap:48px;align-items:start}.plate :global(img){image-rendering:pixelated}
  .controls{display:flex;flex-wrap:wrap;gap:12px 18px;align-items:center;margin-top:12px}.slider{display:grid;gap:2px;flex:1 1 220px;font-size:14px;color:var(--ink-2)}.slider input{width:100%}.inband{color:var(--accent)}
  .note{max-width:44ch;font-size:15px}.spectrum{max-width:960px}.status{font:13px var(--font-data);letter-spacing:.08em}.status[data-status=with_systematics]{color:var(--signal)}.big{font-size:clamp(24px,3.4vw,40px)}
  .ok{color:var(--co)}.off{color:var(--signal)}.src{font-size:12px}.prov{max-width:760px;font-size:15px}.prov a{color:var(--accent)}.obs{overflow-wrap:anywhere}
  @media(max-width:850px){.plate-grid{grid-template-columns:minmax(0,1fr);gap:20px}main{padding-top:36px}header{flex-wrap:wrap}h1{font-size:44px}}
</style>
