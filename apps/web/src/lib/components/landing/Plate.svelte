<script lang="ts">
  import type { Snippet } from "svelte";

  let {
    arcsecPerPx,
    viewPx,
    scaleLabel = "1′",
    scaleArcsec = 60,
    caption,
    credit,
    size = "large",
    compass = true,
    children,
  }: {
    /** Angular size of one image pixel; omit when unknown (no scale bar is drawn). */
    arcsecPerPx?: number;
    /** Number of image pixels across the visible field. */
    viewPx: number;
    scaleLabel?: string;
    scaleArcsec?: number;
    caption?: Snippet;
    credit?: string;
    size?: "large" | "small";
    /** Show the N↑ E← orientation mark; only when the image is known to be north-up. */
    compass?: boolean;
    children: Snippet;
  } = $props();

  const barPercent = $derived(
    arcsecPerPx ? Math.min(100, (scaleArcsec / arcsecPerPx / viewPx) * 100) : 0,
  );
</script>

<figure class="plate {size}">
  <div class="field">
    <span class="reg tl" aria-hidden="true"></span>
    <span class="reg tr" aria-hidden="true"></span>
    <span class="reg bl" aria-hidden="true"></span>
    <span class="reg br" aria-hidden="true"></span>
    <div class="sky">{@render children()}</div>
    {#if barPercent > 0}
      <div class="scale" aria-hidden="true">
        <span class="bar" style:width="{barPercent}%"></span>
        <span class="label">{scaleLabel}</span>
      </div>
    {/if}
    {#if compass}<span class="compass" aria-hidden="true">N↑ E←</span>{/if}
  </div>
  {#if caption || credit}
    <figcaption>
      {#if caption}{@render caption()}{/if}
      {#if credit}<span class="credit">{credit}</span>{/if}
    </figcaption>
  {/if}
</figure>

<style>
  .plate {
    margin: 0;
    min-width: 0;
  }
  .field {
    position: relative;
    background: var(--plate);
    border: 1px solid var(--rule);
    padding: 22px 22px 34px;
  }
  .small .field {
    padding: 12px 12px 26px;
  }
  .sky {
    position: relative;
    overflow: hidden;
    line-height: 0;
  }
  .sky :global(img),
  .sky :global(svg) {
    display: block;
    width: 100%;
    height: auto;
    image-rendering: pixelated;
  }
  .reg {
    position: absolute;
    width: 11px;
    height: 11px;
  }
  .reg::before,
  .reg::after {
    content: "";
    position: absolute;
    background: var(--plate-dim);
  }
  .reg::before {
    left: 5px;
    top: 0;
    width: 1px;
    height: 11px;
  }
  .reg::after {
    top: 5px;
    left: 0;
    width: 11px;
    height: 1px;
  }
  .tl {
    top: 5px;
    left: 5px;
  }
  .tr {
    top: 5px;
    right: 5px;
  }
  .bl {
    bottom: 5px;
    left: 5px;
  }
  .br {
    bottom: 5px;
    right: 5px;
  }
  .small .reg {
    display: none;
  }
  .scale {
    position: absolute;
    left: 22px;
    right: 22px;
    bottom: 9px;
    display: flex;
    align-items: center;
    gap: 8px;
    font: 11px/1 var(--font-data);
    color: var(--plate-ink);
  }
  .small .scale {
    left: 12px;
    right: 12px;
    bottom: 7px;
  }
  .bar {
    position: relative;
    display: block;
    height: 1px;
    background: var(--plate-ink);
  }
  .bar::before,
  .bar::after {
    content: "";
    position: absolute;
    top: -3px;
    width: 1px;
    height: 7px;
    background: var(--plate-ink);
  }
  .bar::before {
    left: 0;
  }
  .bar::after {
    right: 0;
  }
  .compass {
    position: absolute;
    right: 24px;
    bottom: 9px;
    font: 11px/1 var(--font-data);
    color: var(--plate-dim);
  }
  .small .compass {
    display: none;
  }
  figcaption {
    margin-top: 10px;
    font: 12px/1.6 var(--font-data);
    font-variant-numeric: tabular-nums;
    color: var(--graphite);
    overflow-wrap: anywhere;
  }
  .credit {
    display: block;
  }
</style>
