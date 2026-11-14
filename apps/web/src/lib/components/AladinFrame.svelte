<script lang="ts">
  import { onMount } from "svelte";
  import type { Catalog, Viewer, Survey } from "aladin-lite";
  import * as m from "#lib/paraglide/messages.js";
  import { hips, frequencyForFrame, channels } from "#lib/astro/hips.js";
  import type { GaiaStar } from "#lib/data/types.js";

  let element: HTMLDivElement;
  let status = $state("loading");
  let currentFrame = $state(0);
  let viewer: Viewer | undefined,
    survey: Survey | undefined,
    twomass: Survey | undefined,
    gaia: Catalog | undefined;
  let factory: typeof import("aladin-lite").default;
  let desired = {
    ra: 0,
    dec: 0,
    fov: 0.25,
    frame: 0,
    twomass: 0,
    gaia: true,
    stars: [] as GaiaStar[],
  };
  let starsReference: GaiaStar[] | undefined;
  const tell = (message: Record<string, unknown>) =>
    parent.postMessage(message, location.origin);

  function apply() {
    if (!viewer || !survey?.added) return;
    currentFrame = desired.frame;
    survey.setFrequency({
      value: frequencyForFrame(desired.frame),
      unit: "Hz",
    });
    const [ra, dec] = viewer.getRaDec();
    if (
      Math.hypot(
        (((ra - desired.ra + 540) % 360) - 180) *
          Math.cos((dec * Math.PI) / 180),
        dec - desired.dec,
      ) > 1e-6
    )
      viewer.gotoRaDec(desired.ra, desired.dec);
    viewer.setFoV(desired.fov * 3);
    if (desired.twomass > 0 && !twomass) {
      twomass = viewer.newImageSurvey(hips.twomass_url, {
        name: "2MASS Color",
        successCallback: (layer) => layer.setOpacity(desired.twomass),
        errorCallback: () =>
          tell({ type: "aladin-source-error", source: "2mass" }),
      });
      viewer.setOverlayImageLayer(twomass, "2mass");
    }
    twomass?.setOpacity(desired.twomass);
    if (!gaia) {
      gaia = factory.catalog({
        name: "Gaia DR3",
        sourceSize: 6,
        color: "#F2A03D",
      });
      viewer.addCatalog(gaia);
    }
    if (starsReference !== desired.stars) {
      gaia.removeAll();
      gaia.addSources(
        desired.stars.map((star) =>
          factory.source(star.ra, star.dec, {
            source_id: star.source_id,
            ref_epoch: star.ref_epoch,
          }),
        ),
      );
      starsReference = desired.stars;
    }
    if (desired.gaia) gaia.show();
    else gaia.hide();
  }

  onMount(() => {
    let alive = true,
      initialized = false;
    let firstState: () => void;
    const bootstrap = new Promise<void>((resolve) => (firstState = resolve));
    function message(event: MessageEvent) {
      if (
        event.origin !== location.origin ||
        event.source !== parent ||
        !event.data
      )
        return;
      if (
        event.data.type === "aladin-catalog" &&
        Array.isArray(event.data.stars)
      ) {
        desired.stars = event.data.stars.slice(0, 10000);
        if (initialized) apply();
        return;
      }
      if (event.data.type !== "aladin-state") return;
      const state = event.data.state;
      if (
        !state ||
        ![state.ra, state.dec, state.fov, state.frame, state.twomass].every(
          Number.isFinite,
        ) ||
        state.ra < 0 ||
        state.ra >= 360 ||
        Math.abs(state.dec) > 90 ||
        state.fov < 0.05 ||
        state.fov > 0.5 ||
        !Number.isInteger(state.frame) ||
        state.frame < 0 ||
        state.frame >= channels.length
      )
        return;
      desired = {
        ...desired,
        ra: state.ra,
        dec: state.dec,
        fov: state.fov,
        frame: state.frame,
        twomass: Math.max(0, Math.min(1, state.twomass)),
        gaia: !!state.gaia,
      };
      firstState();
      if (initialized) apply();
    }
    window.addEventListener("message", message);
    tell({ type: "aladin-listening" });
    (async () => {
      await bootstrap;
      factory = (await import("aladin-lite")).default;
      await factory.init;
      if (!alive) return;
      viewer = factory.aladin(element, {
        fov: desired.fov * 3,
        target: `${desired.ra} ${desired.dec}`,
        projection: "TAN",
        cooFrame: "ICRSd",
        showCooGridControl: false,
        showLayersControl: false,
        showGotoControl: false,
        showSimbadPointerControl: false,
        showFrame: false,
        showFullscreenControl: false,
        showZoomControl: false,
        showProjectionControl: false,
        showFov: false,
        showCooLocation: false,
        showStatusBar: false,
        showReticle: true,
        reticleColor: "#F2A03D",
        survey: hips.url,
      });
      survey = viewer.newImageSurvey(hips.url, {
        name: hips.title,
        imgFormat: "png",
        successCallback: () => {
          if (!alive) return;
          initialized = true;
          status = "ready";
          apply();
          tell({ type: "aladin-ready" });
        },
        errorCallback: () => {
          if (alive) {
            status = "error";
            tell({ type: "aladin-source-error", source: "spherex_hips" });
          }
        },
      });
      viewer.setBaseImageLayer(survey);
      viewer.on("positionChanged", (position) => {
        if (initialized && !position.dragging)
          tell({ type: "aladin-position", ra: position.ra, dec: position.dec });
      });
      viewer.on("zoomChanged", (fov) => {
        if (initialized) tell({ type: "aladin-zoom", fov: fov / 3 });
      });
    })().catch(() => {
      if (alive) {
        status = "error";
        tell({ type: "aladin-source-error", source: "aladin" });
      }
    });
    return () => {
      alive = false;
      window.removeEventListener("message", message);
    };
  });
</script>

<svelte:head><title>Aladin · Breathing Comets</title></svelte:head>
<div
  class="reference-sky"
  bind:this={element}
  data-testid="aladin-sky"
  data-ready={status === "ready"}
  data-frame={currentFrame}
></div>
{#if status !== "ready"}<p class="loading mono" role="status">
    {status === "error" ? m.aladin_unavailable() : m.aladin_loading()}
  </p>{/if}

<style>
  .reference-sky {
    position: fixed;
    inset: 0;
    width: 100vw;
    height: 100vh;
  }
  .loading {
    position: fixed;
    left: 15px;
    top: 15px;
    max-width: 80%;
    background: var(--plate);
    color: var(--plate-ink);
    padding: 10px;
    pointer-events: none;
  }
  :global(.aladin-box[name^="cube_displayer"]) {
    display: none !important;
  }
</style>
