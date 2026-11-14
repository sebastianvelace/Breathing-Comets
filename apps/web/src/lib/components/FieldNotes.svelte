<script lang="ts">
  import * as m from "#lib/paraglide/messages.js";
  import { noteText } from "#lib/data/notes.js";
  import type { Manifest, SpectrumPoint } from "#lib/data/types.js";
  import SpectrumPlot from "./SpectrumPlot.svelte";
  let {
    manifest,
    spectrum,
    oncompare,
    onplay,
    playing,
  }: {
    manifest: Manifest;
    spectrum: SpectrumPoint[];
    oncompare: () => void;
    onplay: () => void;
    playing: boolean;
  } = $props();
  const intro = $derived(
    (
      {
        barnard: m.barnard_intro,
        "eps-indi-b": m.eps_indi_b_intro,
        "wise-0855": m.wise_0855_intro,
        "rw-aur": m.rw_aur_intro,
        "r-dra": m.r_dra_intro,
      } as Record<string, () => string>
    )[manifest.slug]?.() ?? "",
  );
</script>

<aside class="field-notes">
  <p class="eyebrow mono">{m.field_notes()}</p>
  <h2>{manifest.name}</h2>
  <p class="intro">{intro}</p>
  <button class="compare" onclick={oncompare}
    >{m.compare()} <span aria-hidden="true">↔</span></button
  >
  <button class="play-note" onclick={onplay}
    >{playing ? m.pause() : m.play()}
    <span aria-hidden="true">{playing ? "Ⅱ" : "▶"}</span></button
  >
  <div class="notes">
    {#each manifest.field_notes as note}<section>
        <h3>{noteText(manifest.slug, `${note.key}_label`, note.label)}</h3>
        <p class="measurement" data-testid="field-measurement">
          {noteText(manifest.slug, `${note.key}_value`, note.value)}
        </p>
        <p class="reference mono">
          {noteText(manifest.slug, `${note.key}_ref`, note.ref)}
        </p>
        <p class="caveat">
          {noteText(manifest.slug, "caveat", manifest.caveat)}
        </p>
      </section>{/each}
  </div>
  {#if spectrum.length}<section class="spectrum">
      <h3>{m.reference_spectrum()}</h3>
      <SpectrumPlot points={spectrum} label={m.reference_spectrum()} />
      <p class="caveat">{m.reference_caption()}</p>
      <p class="caveat">{noteText(manifest.slug, "caveat", manifest.caveat)}</p>
    </section>{/if}
</aside>

<style>
  .field-notes {
    padding: 4px 0 0 28px;
    min-width: 0;
  }
  .eyebrow {
    color: var(--graphite);
    letter-spacing: 0.08em;
    margin-bottom: 20px;
  }
  h2 {
    font-size: 34px;
    margin-bottom: 14px;
  }
  .intro {
    font: 20px/1.4 var(--font-display);
    color: var(--ink-2);
    margin-bottom: 22px;
  }
  .compare,
  .play-note {
    width: 100%;
    text-align: left;
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
  }
  .play-note {
    border: 0;
    padding-left: 0;
    margin-bottom: 25px;
  }
  .notes section,
  .spectrum {
    border-top: 1px solid var(--rule);
    padding-top: 19px;
    margin-top: 16px;
  }
  h3 {
    font: 14px/1.4 var(--font-ui);
    margin-bottom: 8px;
    color: var(--ink-2);
  }
  .measurement {
    font: 23px/1.3 var(--font-display);
    margin-bottom: 7px;
  }
  .reference {
    color: var(--graphite);
    margin-bottom: 8px;
  }
  .caveat {
    font-size: 12px;
    line-height: 1.55;
    color: var(--graphite);
    margin-bottom: 12px;
  }
  @media (max-width: 1000px) {
    .field-notes {
      padding-left: 18px;
    }
  }
  @media (max-width: 767px) {
    .field-notes {
      padding: 30px 0 0;
    }
    .intro {
      max-width: 500px;
    }
    .notes {
      display: block;
    }
    h2 {
      font-size: 38px;
    }
  }
</style>
