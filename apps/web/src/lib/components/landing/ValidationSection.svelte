<script lang="ts">
  import * as m from "#lib/paraglide/messages.js";
  import {
    fields,
    n_stars,
    ratio_max,
    ratio_mean,
    ratio_min,
    rule,
    validation as photometry,
  } from "../../../../static/data/calibration.json";
  import { getLocale } from "#lib/paraglide/runtime.js";
  import { fmtSciUnicode, localized, type CometState } from "./landing.js";

  const locale = getLocale();

  let { comet }: { comet: CometState } = $props();

  const CATALOGUE: Record<string, string> = {
    J: "2MASS",
    H: "2MASS",
    Ks: "2MASS",
    W1: "WISE",
    W2: "WISE",
  };
</script>

<section class="section wide" id="validation" aria-labelledby="s5-title">
  <div class="text">
    <p class="num">§5</p>
    <h2 id="s5-title">{m.landing_s5_title()}</h2>
    <p>{m.landing_s5_p1()}</p>
  </div>

  <div class="tables">
    <table data-testid="comet-validation">
      <caption>{m.landing_s5_comets_caption()}</caption>
      <thead>
        <tr>
          <th scope="col">{m.landing_s5_col_species()}</th>
          <th scope="col" class="r">{m.landing_s5_col_measured()}</th>
          <th scope="col" class="r">{m.landing_s5_col_published()}</th>
          <th scope="col">{m.landing_s5_col_check()}</th>
        </tr>
      </thead>
      <tbody>
        {#if comet.status === "ready" && comet.packet.validation.length}
          {#each comet.packet.validation as row (row.species + row.source)}
            {@const inside = row.measured >= row.published_lo && row.measured <= row.published_hi}
            <tr>
              <th scope="row">{row.species}</th>
              <td class="r mono">{fmtSciUnicode(row.measured)} {row.unit}</td>
              <td class="r mono">
                {fmtSciUnicode(row.published_lo)}–{fmtSciUnicode(row.published_hi)}
              </td>
              <td>
                <span class:ok={inside} class:off={!inside}>
                  {inside ? m.landing_s5_inside() : m.landing_s5_outside()}
                </span>
              </td>
            </tr>
            <tr class="sub">
              <td colspan="4"><span class="caveat">{localized(row.caveat, row.caveat_es, locale)}</span> <span class="mono src">{row.source}</span></td>
            </tr>
          {/each}
        {:else}
          <tr>
            <td colspan="4" class="pending">
              <span class="mono state">{comet.status === "missing" || comet.status === "ready" ? m.landing_status_pending() : m.landing_loading()}</span>
              {m.landing_s5_comets_pending()}
            </td>
          </tr>
        {/if}
      </tbody>
    </table>

    <table data-testid="photometry-validation">
      <caption>
        {m.landing_s5_phot_caption({ n: n_stars, fields: fields.join(", ").toUpperCase() })}
      </caption>
      <thead>
        <tr>
          <th scope="col">{m.landing_s5_col_band()}</th>
          <th scope="col">{m.landing_s5_col_catalogue()}</th>
          <th scope="col" class="r">{m.landing_s5_col_stars()}</th>
          <th scope="col" class="r">{m.landing_s5_col_ratio()}</th>
        </tr>
      </thead>
      <tbody>
        {#each photometry as row (row.band)}
          <tr>
            <th scope="row" class="mono">{row.band}</th>
            <td>{CATALOGUE[row.band] ?? "—"}</td>
            <td class="r mono">{row.n}</td>
            <td class="r mono">{row.ratio.toFixed(3)} ± {row.sigma.toFixed(3)}</td>
          </tr>
        {/each}
      </tbody>
    </table>
    <p class="foot">
      {m.landing_s5_phot_note({
        mean: ratio_mean.toFixed(3),
        min: ratio_min.toFixed(3),
        max: ratio_max.toFixed(3),
      })}
      <span class="rule">{rule}</span>
    </p>
  </div>
</section>

<style>
  .tables {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 380px), 1fr));
    gap: 32px 48px;
    align-items: start;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 15px;
  }
  caption {
    text-align: left;
    font-family: var(--font-display);
    font-size: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--ink);
  }
  th,
  td {
    text-align: left;
    padding: 10px 8px 10px 0;
    border-bottom: 1px solid var(--rule);
    vertical-align: top;
  }
  thead th {
    font: 12px/1.3 var(--font-data);
    color: var(--graphite);
    font-weight: 400;
  }
  tbody th {
    font-weight: 400;
  }
  .r {
    text-align: right;
  }
  .mono {
    font-family: var(--font-data);
    font-size: 13px;
    font-variant-numeric: tabular-nums;
  }
  tr.sub td {
    padding-top: 0;
    font-size: 13px;
    color: var(--ink-2);
  }
  .src {
    color: var(--graphite);
  }
  .ok {
    color: var(--co);
  }
  .off {
    color: var(--signal);
  }
  .pending {
    color: var(--ink-2);
    padding: 16px 0;
  }
  .state {
    display: block;
    color: var(--signal);
    letter-spacing: 0.12em;
    margin-bottom: 4px;
  }
  .rule {
    display: block;
    margin-top: 4px;
  }
  .foot {
    grid-column: 1 / -1;
    font: 12px/1.6 var(--font-data);
    color: var(--graphite);
    max-width: 80ch;
  }
</style>
