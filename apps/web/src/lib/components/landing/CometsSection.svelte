<script lang="ts">
  import * as m from "#lib/paraglide/messages.js";
  import Plate from "./Plate.svelte";
  import { getLocale } from "#lib/paraglide/runtime.js";
  import { fmtLam, fmtSciUnicode, localized, type CometState } from "./landing.js";

  const locale = getLocale();

  let { comet }: { comet: CometState } = $props();

  const lead = $derived(
    comet.status === "ready" ? comet.packet.measurements[0] : undefined,
  );
  const rest = $derived(
    comet.status === "ready" ? comet.packet.measurements.slice(1) : [],
  );
</script>

<section class="section" id="comets" aria-labelledby="s4-title">
  <div class="text">
    <p class="num">§4</p>
    <h2 id="s4-title">{m.landing_s4_title()}</h2>
    <p>{m.landing_s4_p1()}</p>
    <p>{m.landing_s4_p2()}</p>
    <p class="margin-note">{m.landing_s4_note()}</p>
  </div>

  <div class="figure" data-testid="comet-panel" data-status={comet.status}>
    {#if comet.status === "ready"}
      {@const packet = comet.packet}
      <Plate
        arcsecPerPx={packet.plates.pixel_arcsec}
        viewPx={packet.plates.nx ?? 1}
        compass={packet.plates.north_up === true}
        credit={packet.credits.join(" · ")}
      >
        <img
          src={packet.plates.poster}
          alt={m.landing_s4_alt({ target: packet.target })}
          loading="lazy"
          decoding="async"
        />
        {#snippet caption()}
          {#if packet.plates.epochs[0]}
            {@const e = packet.plates.epochs[0]}
            <span>{packet.target} · SPHEREx · {fmtLam(e.lambda_um)} µm · MJD {e.mjd.toFixed(2)} · obs {e.obs_id}</span>
          {:else}
            <span>{packet.target}</span>
          {/if}
        {/snippet}
      </Plate>
      {#if lead}
        <div class="figure-number">
          <p class="label">{localized(lead.label, lead.label_es, locale)}</p>
          <p class="big mono-num">
            {fmtSciUnicode(lead.value)} <span class="unit">{lead.unit}</span>
          </p>
          <p class="range mono">
            {m.landing_range({ lo: fmtSciUnicode(lead.lo), hi: fmtSciUnicode(lead.hi) })}
          </p>
          <p class="caveat">{localized(lead.caveat, lead.caveat_es, locale)}</p>
          <p class="source mono">{lead.source}</p>
        </div>
      {/if}
      {#if rest.length}
        <dl class="more">
          {#each rest as item (item.label)}
            <div>
              <dt>{localized(item.label, item.label_es, locale)}</dt>
              <dd class="mono">
                {fmtSciUnicode(item.value)} {item.unit}
                ({m.landing_range({ lo: fmtSciUnicode(item.lo), hi: fmtSciUnicode(item.hi) })})
              </dd>
              <dd class="caveat">{localized(item.caveat, item.caveat_es, locale)}</dd>
              <dd class="source mono">{item.source}</dd>
            </div>
          {/each}
        </dl>
      {/if}
    {:else}
      <div class="pending" role="status">
        <p class="state mono">
          {comet.status === "missing" ? m.landing_status_pending() : m.landing_loading()}
        </p>
        <p>{m.landing_s4_pending()}</p>
        {#if comet.status === "missing"}
          <p class="mono reason">/data/comets/3i-atlas/landing.json · {comet.reason}</p>
        {/if}
      </div>
    {/if}
  </div>
</section>

<style>
  .figure-number {
    margin-top: 28px;
    border-top: 1px solid var(--rule);
    padding-top: 18px;
  }
  .label {
    font-size: 14px;
    color: var(--ink-2);
    margin-bottom: 4px;
  }
  .big {
    font-family: var(--font-data);
    font-variant-numeric: tabular-nums;
    font-size: clamp(32px, 4.4vw, 52px);
    line-height: 1.1;
    margin-bottom: 6px;
  }
  .unit {
    font-size: 0.45em;
    color: var(--ink-2);
  }
  .range,
  .source,
  .reason {
    color: var(--graphite);
  }
  .caveat {
    font-size: 14px;
    color: var(--ink-2);
    border-left: 2px solid var(--co2);
    padding-left: 10px;
    margin: 8px 0;
  }
  .more {
    margin: 20px 0 0;
  }
  .more > div {
    border-top: 1px solid var(--rule);
    padding: 12px 0;
  }
  .more dt {
    font-size: 14px;
  }
  .more dd {
    margin: 2px 0;
  }
  .pending {
    border: 1px solid var(--rule);
    padding: 24px;
    background: var(--paper-2);
  }
  .state {
    letter-spacing: 0.12em;
    color: var(--signal);
    margin-bottom: 10px;
  }
  .pending p:last-child {
    margin-bottom: 0;
  }
</style>
