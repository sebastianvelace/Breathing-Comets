<script lang="ts">
  import {onMount} from 'svelte';
  import * as m from "#lib/paraglide/messages.js";
  import Plate from "./Plate.svelte";
  import { fmtLam, isoDate, landingMedia } from "./landing.js";

  const barnard = landingMedia.plates.barnard;
  const d = barnard.difference;
  const raw = d.raw;
  const diff = d.diff_lambda;

  let split = $state(50);
  let mounted = $state(false);
  onMount(() => {mounted = true;});
</script>

<section class="section" id="diff" aria-labelledby="s2-title">
  <div class="text">
    <h2 id="s2-title">{m.landing_s2_title()}</h2>
    <p>{m.landing_s2_p1()}</p>
    <p>{m.landing_s2_p2({ a: fmtLam(raw.a.lam_um), b: fmtLam(raw.b.lam_um) })}</p>
    <p>{m.landing_s2_p3()}</p>
    <p class="margin-note">
      {m.landing_s2_note({ n: d.reference_count ?? "—" })}
    </p>
  </div>

  <div class="figure">
    <Plate
      arcsecPerPx={barnard.grid.pixel_arcsec}
      viewPx={barnard.grid.nx}
      credit={landingMedia.credits[0]}
    >
      <div class="compare" data-testid="diff-compare" style:--split="{split}%">
        <img
          src={raw.src}
          width={raw.width}
          height={raw.height}
          alt={m.landing_s2_alt_raw()}
          loading="lazy"
          decoding="async"
        />
        <img
          class="top"
          src={diff.src}
          width={diff.width}
          height={diff.height}
          alt={m.landing_s2_alt_diff()}
          loading="lazy"
          decoding="async"
        />
        <span class="divider" aria-hidden="true"></span>
        <span class="tag left" aria-hidden="true">{m.landing_s2_raw_label()}</span>
        <span class="tag right" aria-hidden="true">Diff λ</span>
      </div>
      {#snippet caption()}
        <span class="row"
          ><b>{m.landing_s2_raw_label()}</b> D{raw.b.det} {fmtLam(raw.b.lam_um)} µm ({isoDate(raw.b.date)}) − {fmtLam(raw.a.lam_um)} µm ({isoDate(raw.a.date)})</span
        >
        <span class="row"
          ><b>Diff λ</b> D{diff.det} {fmtLam(diff.lam_um)} µm · {isoDate(diff.date)} · obs {diff.obs_id}</span
        >
      {/snippet}
    </Plate>
    <label class="slider">
      <span>{m.landing_s2_slider()}</span>
      <input
        type="range"
        disabled={!mounted}
        min="0"
        max="100"
        step="1"
        bind:value={split}
        aria-valuetext={m.landing_s2_slider_value({ pct: split })}
      />
    </label>
    <div class="legend mono" aria-label={m.landing_s2_legend()}>
      <span><i class="sw neg"></i>−5σ</span>
      <span><i class="sw zero"></i>0</span>
      <span><i class="sw pos"></i>+5σ</span>
      <span class="sat"><i class="sw white"></i>{m.landing_saturated()}</span>
      <span class="sigma">σ = {d.sigma.toPrecision(2)} MJy/sr</span>
    </div>
  </div>
</section>

<style>
  .compare {
    position: relative;
    aspect-ratio: 1;
  }
  .compare img {
    position: absolute;
    inset: 0;
  }
  .compare .top {
    clip-path: inset(0 0 0 var(--split));
  }
  .divider {
    position: absolute;
    top: 0;
    bottom: 0;
    left: var(--split);
    width: 1px;
    background: var(--plate-ink);
  }
  .tag {
    position: absolute;
    top: 8px;
    padding: 3px 6px;
    font: 11px/1.2 var(--font-data);
    color: var(--plate-ink);
    background: var(--plate);
    line-height: 1.2;
  }
  .tag.left {
    left: 8px;
  }
  .tag.right {
    right: 8px;
  }
  .row {
    display: block;
  }
  .row b {
    font-weight: 400;
    color: var(--ink);
    margin-right: 6px;
  }
  .slider {
    display: grid;
    gap: 2px;
    margin-top: 14px;
    font-size: 14px;
    color: var(--ink-2);
  }
  .slider input {
    width: 100%;
  }
  .legend {
    display: flex;
    flex-wrap: wrap;
    gap: 6px 16px;
    margin-top: 6px;
    color: var(--graphite);
  }
  .sw {
    display: inline-block;
    width: 10px;
    height: 10px;
    margin-right: 6px;
    vertical-align: -1px;
    border: 1px solid var(--rule);
  }
  .neg {
    background: var(--co-on-plate);
  }
  .zero {
    background: var(--plate);
  }
  .pos {
    background: var(--co2-on-plate);
  }
  .white {
    background: #ffffff;
  }
</style>
