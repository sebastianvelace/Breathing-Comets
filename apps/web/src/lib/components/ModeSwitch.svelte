<script lang="ts">
  import { ToggleGroup } from "bits-ui";
  import * as m from "#lib/paraglide/messages.js";
  let {
    value,
    onchange,
    showCube = false,
  }: {
    value: string;
    showCube?: boolean;
    onchange: (value: string) => void;
  } = $props();
</script>

<ToggleGroup.Root
  type="single"
  {value}
  onValueChange={(v) => {
    if (v) onchange(v);
  }}
  aria-label={m.mode()}
  class="mode-switch"
>
  <ToggleGroup.Item value="epoch">{m.epoch()}</ToggleGroup.Item
  ><ToggleGroup.Item value="blink">{m.blink()}</ToggleGroup.Item
  ><ToggleGroup.Item value="diff">{m.diff()}</ToggleGroup.Item>
  {#if showCube}<ToggleGroup.Item value="cube">{m.cube()}</ToggleGroup.Item
    >{/if}
</ToggleGroup.Root>

<style>
  /* One soft pill holding the options, instead of three boxed buttons. */
  :global(.mode-switch) {
    display: inline-flex;
    gap: 2px;
    padding: 4px;
    border-radius: var(--r-pill);
    background: color-mix(in srgb, var(--ink) 7%, transparent);
  }
  :global(.mode-switch button) {
    border: 0;
    min-height: 36px;
    padding: 6px 18px;
    white-space: nowrap;
    color: var(--ink-2);
  }
  :global(.mode-switch button:hover) {
    color: var(--ink);
  }
  :global(.mode-switch button[data-state="on"]) {
    background: var(--accent);
    color: var(--accent-ink);
    box-shadow: 0 6px 18px -8px var(--accent);
  }
</style>
