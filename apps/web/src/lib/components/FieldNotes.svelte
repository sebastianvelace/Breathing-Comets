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
    ready,
  }: {
    manifest: Manifest;
    spectrum: SpectrumPoint[];
    oncompare: () => void;
    onplay: () => void;
    playing: boolean;
    ready: boolean;
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
  // The manifest carries one target-level caveat; show it once, next to the
  // measurement it qualifies, instead of under every note.
  const caveatKey: Record<string, string> = {
    barnard: "pm",
    "eps-indi-b": "plx",
    "wise-0855": "w2",
    "r-dra": "period",
    "rw-aur": "anti",
  };
  const caveatNote = $derived(
    manifest.field_notes.find((n) => n.key === caveatKey[manifest.slug])?.key ??
      manifest.field_notes.at(-1)?.key,
  );
</script>

<aside class="field-notes">
  <p class="eyebrow mono">{m.field_notes()}</p>
  <h2>{manifest.name}</h2>
  <p class="intro">{intro}</p>
  <button class="compare" onclick={oncompare} disabled={!ready}
    >{m.compare()} <span aria-hidden="true">↔</span></button
  >
  <button class="play-note" onclick={onplay} disabled={!ready}
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
        {#if note.key === caveatNote}<p class="caveat" data-testid="field-caveat">
            {noteText(manifest.slug, "caveat", manifest.caveat)}
          </p>{/if}
      </section>{/each}
  </div>
  {#if spectrum.length}<section class="spectrum">
      <h3>{m.reference_spectrum()}</h3>
      <SpectrumPlot points={spectrum} label={m.reference_spectrum()} />
      <p class="caveat">{m.reference_caption()}</p>
    </section>{/if}
</aside>

<style>
  .field-notes {
    min-width: 0;
    align-self: start;
    padding: 24px;
    border-radius: var(--r-lg);
    background: color-mix(in srgb, var(--ink) 5%, transparent);
  }
  .eyebrow {
    color: var(--graphite);
    letter-spacing: 0.08em;
    margin-bottom: 20px;
  }
  h2 {
    font-size: 30px;
    margin-bottom: 14px;
  }
  .intro {
    font-size: 16px;
    line-height: 1.55;
    color: var(--ink-2);
    margin-bottom: 20px;
  }
  .compare,
  .play-note {
    width: 100%;
    text-align: left;
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
  }
  .compare,
  .play-note {
    align-items: center;
    background: color-mix(in srgb, var(--ink) 6%, transparent);
    border-color: transparent;
    border-radius: var(--r-md);
    padding: 10px 16px;
  }
  .compare:hover,
  .play-note:hover {
    background: color-mix(in srgb, var(--accent) 18%, transparent);
  }
  .play-note {
    margin-bottom: 8px;
  }
  .notes section,
  .spectrum {
    margin-top: 12px;
    padding: 16px;
    border-radius: var(--r-md);
    background: color-mix(in srgb, var(--ink) 4%, transparent);
  }
  h3 {
    font: 500 12px/1.4 var(--font-ui);
    letter-spacing: 0.02em;
    margin-bottom: 6px;
    color: var(--graphite);
  }
  .measurement {
    font: 600 22px/1.25 var(--font-display);
    letter-spacing: -0.02em;
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
      padding: 18px;
    }
  }
  @media (max-width: 767px) {
    .field-notes {
      margin-top: 24px;
    }
    .intro {
      max-width: 500px;
    }
    .notes {
      display: block;
    }
    h2 {
      font-size: 30px;
    }
  }
</style>
