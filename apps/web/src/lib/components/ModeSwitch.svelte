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
  :global(.mode-switch) {
    display: flex;
    gap: 0;
  }
  :global(.mode-switch button) {
    border-right-width: 0;
    white-space: nowrap;
  }
  :global(.mode-switch button:last-child) {
    border-right-width: 1px;
  }
  :global(.mode-switch button[data-state="on"]) {
    background: var(--co2);
    color: var(--paper);
    border-color: var(--co2);
  }
</style>
