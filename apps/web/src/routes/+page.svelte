<script lang="ts">
  import { localizeHref } from "#lib/paraglide/runtime.js";
    import { m } from '#lib/paraglide/messages.js';
</script>
<svelte:head>
    <title>Breathing Comets</title>
    <meta name="description" content={m.service_preparing()} />
</svelte:head>
<main>
    <h1>Breathing Comets</h1>
    <p>{m.service_preparing()}</p>
<a class="open-sky" href={localizeHref("/explore")+"?target=barnard&ui=story"}>{m.open_sky()} →</a></main>
