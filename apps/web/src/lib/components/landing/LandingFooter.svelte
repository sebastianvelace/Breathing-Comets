<script lang="ts">
  import { page } from "$app/state";
  import * as m from "#lib/paraglide/messages.js";
  import { getLocale, localizeHref } from "#lib/paraglide/runtime.js";
  import { landingMedia } from "./landing.js";

  const locale = getLocale();
</script>

<footer class="foot">
  <div class="cols">
    <div>
      <p class="h">{m.landing_footer_data()}</p>
      <ul>
        {#each landingMedia.credits as credit (credit)}
          <li>{credit}</li>
        {/each}
        <li>{m.landing_footer_simbad()}</li>
      </ul>
      <p>{m.landing_footer_not_nasa()}</p>
    </div>
    <div>
      <p class="h">{m.landing_footer_ai_title()}</p>
      <p>{m.landing_footer_ai()}</p>
      <p class="h">{m.landing_footer_media_title()}</p>
      <p>{m.landing_footer_media({ date: landingMedia.generated })}</p>
    </div>
    <div>
      <p class="h">{m.landing_footer_links()}</p>
      <ul>
        <li><a href="{localizeHref('/explore')}?target=rw-aur&ui=story">{m.landing_footer_explorer()}</a></li>
        <li><a href={localizeHref("/method")}>{m.landing_footer_method()}</a></li>
        <li><a href={localizeHref("/about")}>{m.landing_footer_about()}</a></li>
        <li>
          <a href="https://github.com/sebastianvelace/Breathing-Comets" rel="external">{m.landing_footer_code()}</a>
        </li>
        <li>
          <a href={localizeHref(page.url.pathname, { locale: "en" })} hreflang="en" lang="en" aria-current={locale === "en" ? "true" : undefined} data-sveltekit-reload>English</a>
          ·
          <a href={localizeHref(page.url.pathname, { locale: "es" })} hreflang="es" lang="es" aria-current={locale === "es" ? "true" : undefined} data-sveltekit-reload>Español</a>
        </li>
      </ul>
    </div>
  </div>
  <p class="brand-line">BREATHING COMETS · NASA SPACE APPS 2026</p>
</footer>

<style>
  .foot {
    max-width: 1280px;
    margin: 0 auto;
    padding: 48px var(--gutter) 40px;
    border-top: 1px solid var(--ink);
    font: 12px/1.7 var(--font-data);
    color: var(--graphite);
  }
  .cols {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 260px), 1fr));
    gap: 28px 48px;
  }
  .h {
    color: var(--ink);
    margin-bottom: 6px;
  }
  ul {
    list-style: none;
    margin: 0 0 12px;
    padding: 0;
  }
  a {
    color: var(--ink-2);
    display: inline-block;
    padding: 4px 0;
  }
  a[aria-current="true"] {
    color: var(--ink);
    text-decoration-color: var(--co2);
  }
  .brand-line {
    margin: 36px 0 0;
    letter-spacing: 0.2em;
  }
</style>
