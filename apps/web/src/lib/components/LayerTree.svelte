<script lang="ts">
  import * as m from "#lib/paraglide/messages.js";
  let {
    detector,
    layers,
    twomass,
    onchange,
    onopacity,
  }: {
    detector: number;
    layers: string[];
    twomass: number;
    onchange: (key: string, enabled: boolean) => void;
    onopacity: (value: number, commit: boolean) => void;
  } = $props();
</script>

<aside class="layer-tree" aria-label={m.layers()}>
  <h2>{m.layers()}</h2>
  <p class="source mono">SPHEREx · D{detector}</p>
  <label
    ><input
      type="checkbox"
      checked={layers.includes("gaia")}
      onchange={(e) => onchange("gaia", e.currentTarget.checked)}
    />{m.gaia()}</label
  >
  <label
    ><input
      type="checkbox"
      checked={layers.includes("grid")}
      onchange={(e) => onchange("grid", e.currentTarget.checked)}
    />{m.pixel_grid()}</label
  >
  <label
    ><input
      type="checkbox"
      checked={layers.includes("flags")}
      onchange={(e) => onchange("flags", e.currentTarget.checked)}
    />{m.quality_flags()}</label
  >
  <label
    ><input
      type="checkbox"
      checked={layers.includes("jpl")}
      onchange={(e) => onchange("jpl", e.currentTarget.checked)}
    />{m.known_objects()}</label
  >
  <p class="source mono">{m.reference_sky()}</p>
  <p class="reference">IRSA · DR1</p>
  <label for="twomass-opacity">2MASS · {m.opacity()}</label>
  <input
    id="twomass-opacity"
    type="range"
    min="0"
    max="1"
    step="0.05"
    value={twomass}
    aria-label={m.twomass_opacity()}
    oninput={(e) => onopacity(Number(e.currentTarget.value), false)}
    onchange={(e) => onopacity(Number(e.currentTarget.value), true)}
  />
  <p class="note">{m.flags_note()}</p>
</aside>

<style>
  .layer-tree {
    background: transparent;
    color: var(--plate-ink);
    border: 0;
    padding: 8px 0 18px;
    width: 100%;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    column-gap: 24px;
    box-shadow: none;
  }
  h2 {
    display: none;
    font: 12px var(--font-data);
    letter-spacing: 0.08em;
    margin: 0 0 22px;
  }
  .source {
    font-size: 11px;
    color: var(--plate-dim);
    border-top: 1px solid var(--rule);
    grid-column: 1 / -1;
    padding-top: 14px;
    margin-top: 18px;
  }
  label {
    display: flex;
    gap: 9px;
    align-items: center;
    font-size: 14px;
    margin: 12px 0;
  }
  input[type="checkbox"] {
    accent-color: var(--accent-on-plate);
  }
  input[type="range"] {
    width: 100%;
    accent-color: var(--accent-on-plate);
  }
  .reference,
  .note {
    font-size: 11px;
    color: var(--plate-dim);
  }
  .note {
    line-height: 1.5;
    margin: 12px 0 0;
    grid-column: 1 / -1;
  }
  @media (max-width: 480px) { .layer-tree { grid-template-columns: 1fr; } }
</style>
