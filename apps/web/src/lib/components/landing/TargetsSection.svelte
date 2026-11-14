<script lang="ts">
  import { m } from "#lib/paraglide/messages.js";
  import { localizeHref } from "#lib/paraglide/runtime.js";
  import { noteText } from "#lib/data/notes.js";
  import * as barnard from "../../../../static/data/targets/barnard.json";
  import * as epsIndiB from "../../../../static/data/targets/eps-indi-b.json";
  import * as wise0855 from "../../../../static/data/targets/wise-0855.json";
  import * as rwAur from "../../../../static/data/targets/rw-aur.json";
  import * as rDra from "../../../../static/data/targets/r-dra.json";
  import Plate from "./Plate.svelte";
  import { fmtLam, isoDate, landingMedia, TARGET_ORDER } from "./landing.js";

  type Notes = {
    name: string;
    notes: { key: string; label: string; value: string; ref: string }[];
    caveat: string;
  };
  // Only name/notes/caveat are read, so the spectra and light curves are tree-shaken.
  const sources: Record<string, Notes> = {
    barnard: { name: barnard.name, notes: barnard.notes, caveat: barnard.caveat },
    "eps-indi-b": { name: epsIndiB.name, notes: epsIndiB.notes, caveat: epsIndiB.caveat },
    "wise-0855": { name: wise0855.name, notes: wise0855.notes, caveat: wise0855.caveat },
    "rw-aur": { name: rwAur.name, notes: rwAur.notes, caveat: rwAur.caveat },
    "r-dra": { name: rDra.name, notes: rDra.notes, caveat: rDra.caveat },
  };

  const roles: Record<string, () => string> = {
    barnard: m.landing_s6_role_barnard,
    "eps-indi-b": m.landing_s6_role_eps,
    "wise-0855": m.landing_s6_role_wise,
    "rw-aur": m.landing_s6_role_rwaur,
    "r-dra": m.landing_s6_role_rdra,
  };

  const targets = TARGET_ORDER.map((slug) => ({
    slug,
    plate: landingMedia.plates[slug],
    ...sources[slug],
  }));
</script>

<section class="section wide" id="targets" aria-labelledby="s6-title">
  <div class="text">
    <p class="num">§6</p>
    <h2 id="s6-title">{m.landing_s6_title()}</h2>
    <p>{m.landing_s6_p1()}</p>
  </div>

  <div class="rail-wrap">
    <ol class="rail" aria-label={m.landing_s6_list()} data-testid="targets-rail">
      {#each targets as t, i (t.slug)}
        <li class="card" data-slug={t.slug}>
          <Plate
            size="small"
            arcsecPerPx={t.plate.grid.pixel_arcsec}
            viewPx={t.plate.grid.nx}
            scaleLabel="5′"
            scaleArcsec={300}
          >
            <img
              src={t.plate.poster.src}
              width={t.plate.poster.width}
              height={t.plate.poster.height}
              alt={m.landing_s6_alt({ name: t.name, det: t.plate.det, lam: fmtLam(t.plate.poster.lam_um) })}
              loading="lazy"
              decoding="async"
            />
            {#snippet caption()}
              <span>D{t.plate.det} · {fmtLam(t.plate.poster.lam_um)} µm · {isoDate(t.plate.poster.date)}</span>
              <span class="obs">obs {t.plate.poster.obs_id}</span>
            {/snippet}
          </Plate>
          <p class="idx mono">{String(i + 1).padStart(2, "0")}</p>
          <h3>{t.name}</h3>
          <p class="role">{roles[t.slug]()}</p>
          <dl class="notes">
            {#each t.notes as note (note.key)}
              <div>
                <dt>{noteText(t.slug, `${note.key}_label`, note.label)}</dt>
                <dd class="value">{noteText(t.slug, `${note.key}_value`, note.value)}</dd>
                <dd class="ref">{noteText(t.slug, `${note.key}_ref`, note.ref)}</dd>
              </div>
            {/each}
          </dl>
          <p class="caveat">
            <span class="sr-only">{m.landing_caveat()}: </span>{noteText(t.slug, "caveat", t.caveat)}
          </p>
          <a class="open" href="{localizeHref('/explore')}?target={t.slug}&ui=story"
            >{m.landing_s6_open({ name: t.name })}<span aria-hidden="true"> →</span></a
          >
        </li>
      {/each}
    </ol>
  </div>
  <p class="hint mono">{m.landing_s6_hint()}</p>
</section>

<style>
  .rail-wrap {
    border-top: 1px solid var(--rule);
    border-bottom: 1px solid var(--rule);
  }
  .rail {
    list-style: none;
    margin: 0;
    padding: 24px 0 28px;
    display: grid;
    grid-auto-flow: column;
    grid-auto-columns: minmax(250px, 1fr);
    gap: 28px;
    overflow-x: auto;
    overscroll-behavior-x: contain;
    scroll-snap-type: x mandatory;
    scrollbar-color: var(--rule) transparent;
  }
  .rail:focus-visible {
    outline: 2px solid var(--co2);
    outline-offset: 4px;
  }
  .card {
    /* Contains the absolutely positioned sr-only text inside the scroll rail. */
    position: relative;
    scroll-snap-align: start;
    min-width: 0;
    display: flex;
    flex-direction: column;
  }
  .obs {
    display: block;
  }
  .idx {
    margin: 16px 0 2px;
    color: var(--graphite);
  }
  h3 {
    font-size: 24px;
    margin-bottom: 6px;
  }
  .role {
    font-size: 15px;
    color: var(--ink-2);
    margin-bottom: 12px;
  }
  .notes {
    margin: 0 0 10px;
  }
  .notes div {
    border-top: 1px solid var(--rule);
    padding: 8px 0;
  }
  dt {
    font-size: 13px;
    color: var(--ink-2);
  }
  dd {
    margin: 0;
  }
  .value {
    font-family: var(--font-data);
    font-variant-numeric: tabular-nums;
    font-size: 15px;
  }
  .ref {
    font: 12px/1.5 var(--font-data);
    color: var(--graphite);
  }
  .caveat {
    font-size: 13px;
    color: var(--ink-2);
    border-left: 2px solid var(--co2);
    padding-left: 10px;
  }
  .open {
    margin-top: auto;
    padding-top: 8px;
    color: var(--co2);
    font-weight: 500;
    min-height: 40px;
    display: inline-flex;
    align-items: center;
  }
  .hint {
    margin-top: 10px;
    color: var(--graphite);
  }
  @media (min-width: 1280px) {
    .rail {
      grid-auto-columns: minmax(0, 1fr);
    }
    .hint {
      display: none;
    }
  }
</style>
