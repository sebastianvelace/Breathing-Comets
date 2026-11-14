<script lang="ts">
  import { onMount } from "svelte";
  import { localizeHref } from "#lib/paraglide/runtime.js";
  import * as m from "#lib/paraglide/messages.js";
  import { channels } from "#lib/astro/hips.js";
  import type { GaiaStar } from "#lib/data/types.js";

  let {
    ra,
    dec,
    fov,
    channel = $bindable(0),
    twomass = 0,
    showGaia = true,
    stars = [],
    onchannel,
    onmove,
  }: {
    ra: number;
    dec: number;
    fov: number;
    channel?: number;
    twomass?: number;
    showGaia?: boolean;
    stars?: GaiaStar[];
    onchannel: () => void;
    onmove: (ra: number, dec: number, fov?: number) => void;
  } = $props();
  let iframe: HTMLIFrameElement;
  let ready = $state(false),
    listening = $state(false),
    sourceError = $state("");
  let pending: ReturnType<typeof setTimeout> | undefined;
  let nextPosition: { ra: number; dec: number; fov?: number } | undefined;
  function schedule(
    position: Partial<{ ra: number; dec: number; fov: number }>,
  ) {
    nextPosition = { ra, dec, fov, ...nextPosition, ...position };
    clearTimeout(pending);
    pending = setTimeout(() => {
      if (nextPosition) {
        onmove(nextPosition.ra, nextPosition.dec, nextPosition.fov);
        nextPosition = undefined;
      }
    }, 150);
  }
  function sendState() {
    iframe?.contentWindow?.postMessage(
      {
        type: "aladin-state",
        state: { ra, dec, fov, frame: channel, twomass, gaia: showGaia },
      },
      location.origin,
    );
  }
  onMount(() => {
    function message(event: MessageEvent) {
      if (
        event.origin !== location.origin ||
        event.source !== iframe.contentWindow ||
        !event.data
      )
        return;
      const data = event.data;
      if (data.type === "aladin-listening") {
        listening = true;
        sendState();
      } else if (data.type === "aladin-ready") {
        ready = true;
        sendState();
      } else if (data.type === "aladin-source-error")
        sourceError = String(data.source);
      else if (
        data.type === "aladin-position" &&
        Number.isFinite(data.ra) &&
        Number.isFinite(data.dec) &&
        Math.hypot(
          (((data.ra - ra + 540) % 360) - 180) *
            Math.cos((dec * Math.PI) / 180),
          data.dec - dec,
        ) > 1e-5
      ) {
        schedule({ ra: data.ra, dec: data.dec });
      } else if (
        data.type === "aladin-zoom" &&
        Number.isFinite(data.fov) &&
        Math.abs(data.fov - fov) > 1e-5
      ) {
        schedule({ fov: Math.max(0.05, Math.min(0.5, data.fov)) });
      }
    }
    window.addEventListener("message", message);
    return () => {
      window.removeEventListener("message", message);
      clearTimeout(pending);
    };
  });
  $effect(() => {
    void ra;
    void dec;
    void fov;
    void channel;
    void twomass;
    void showGaia;
    if (listening) sendState();
  });
  $effect(() => {
    if (ready)
      iframe.contentWindow?.postMessage(
        { type: "aladin-catalog", stars },
        location.origin,
      );
  });
</script>

<section class="aladin-reference" aria-label={m.reference_sky()}>
  <header>
    <h3>{m.reference_sky()}</h3>
    <span class="mono">IRSA · SPHEREx DR1</span>
  </header>
  <iframe
    bind:this={iframe}
    src={localizeHref("/aladin")}
    title={m.reference_sky()}
    data-testid="aladin-frame"
  ></iframe>
  <div class="channel-controls">
    <label for="hips-channel">{m.hips_channel()}</label><input
      id="hips-channel"
      type="range"
      min="0"
      max={channels.length - 1}
      step="1"
      bind:value={channel}
      aria-label={m.hips_channel()}
      onchange={onchannel}
    /><input
      type="number"
      min="0"
      max={channels.length - 1}
      bind:value={channel}
      aria-label={m.hips_frame()}
      onchange={() => {
        channel = Math.max(
          0,
          Math.min(channels.length - 1, Math.round(Number(channel)) || 0),
        );
        onchannel();
      }}
    />
  </div>
  <p class="mono" data-testid="hips-channel-label">
    {m.frame()}
    {channels[channel]?.frame} · D{channels[channel]?.detector} · {channels[
      channel
    ]?.wavelength_um.toFixed(3)} µm
  </p>
  {#if channel === 50 || channel === 51}<p class="source-status mono">
      {m.hips_blank_channel()}
    </p>{/if}
  {#if sourceError}<p class="source-status mono" role="status">
      {m.reference_unavailable()} ({sourceError})
    </p>{/if}
  <p class="reference-note">{m.hips_reference_note()}</p>
</section>

<style>
  .aladin-reference {
    min-width: 0;
    border-top: 1px solid var(--rule);
    margin-top: 24px;
    padding-top: 18px;
  }
  header {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    align-items: baseline;
  }
  h3 {
    font: 20px var(--font-display);
    margin-bottom: 12px;
  }
  header span {
    color: var(--graphite);
    font-size: 10px;
  }
  iframe {
    display: block;
    width: 100%;
    height: 380px;
    border: 1px solid var(--rule);
    background: var(--plate);
  }
  .channel-controls {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 12px;
    margin-top: 10px;
  }
  .channel-controls input[type="range"] {
    flex: 1;
    min-width: 80px;
  }
  .channel-controls input[type="number"] {
    width: 65px;
    padding: 5px;
    color: var(--ink);
    background: var(--paper);
    border: 1px solid var(--rule);
  }
  p.mono {
    font-size: 11px;
    margin-bottom: 8px;
  }
  .reference-note,
  .source-status {
    font-size: 12px;
    color: var(--graphite);
  }
  @media (max-width: 767px) {
    iframe {
      height: 300px;
    }
  }
</style>
