<script lang="ts">
  import * as m from "#lib/paraglide/messages.js";
  import { localizeHref } from "#lib/paraglide/runtime.js";

  const explore = (slug: string) => `${localizeHref("/explore")}?target=${slug}&ui=story`;
  const routes = [
    { name: "Barnard's Star", href: explore("barnard"), why: () => m.landing_close_r_barnard() },
    { name: "WISE 0855−0714", href: explore("wise-0855"), why: () => m.landing_close_r_wise() },
    { name: "RW Aurigae", href: explore("rw-aur"), why: () => m.landing_close_r_rwaur() },
    { name: "3I/ATLAS", href: localizeHref("/comets/3i-atlas"), why: () => m.landing_close_r_3i() },
  ];
</script>

<section class="close" id="start" aria-labelledby="close-title">
  <div class="lead">
    <h2 id="close-title">{m.landing_close_title()}</h2>
    <p>{m.landing_close_body()}</p>
    <div class="actions">
      <a class="cta primary" href={explore("barnard")} data-testid="close-open-sky"
        >{m.landing_hero_cta_sky()}<span aria-hidden="true" class="arrow"> →</span></a
      >
      <a class="cta secondary" href={localizeHref("/comets")}>{m.landing_hero_cta_comets()}</a>
    </div>
  </div>
  <div class="routes">
    <p class="label mono">{m.landing_close_routes()}</p>
    <ul>
      {#each routes as r (r.name)}
        <li>
          <a href={r.href}>
            <span class="name">{r.name}</span>
            <span class="why">{r.why()}</span>
            <span class="go" aria-hidden="true">→</span>
          </a>
        </li>
      {/each}
    </ul>
  </div>
</section>

<style>
  .close {
    max-width: 1280px;
    margin: 0 auto;
    padding: clamp(72px, 10vw, 140px) var(--gutter);
    border-top: 1px solid var(--rule);
    display: grid;
    grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr);
    gap: clamp(36px, 6vw, 96px);
    align-items: end;
  }
  h2 {
    font-size: clamp(44px, 6.4vw, 96px);
    line-height: 0.98;
    letter-spacing: -0.02em;
    margin: 0 0 24px;
    text-wrap: balance;
  }
  .lead p {
    font-size: 18px;
    line-height: 1.65;
    color: var(--ink-2);
    max-width: 46ch;
    margin: 0 0 32px;
  }
  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
  }
  .cta {
    display: inline-flex;
    align-items: center;
    min-height: 52px;
    padding: 12px 26px;
    font-weight: 500;
    text-decoration: none;
    border: 1px solid var(--co2);
    transition:
      background 200ms var(--ease),
      color 200ms var(--ease),
      border-color 200ms var(--ease),
      transform 200ms var(--ease);
  }
  .cta.primary {
    background: var(--co2);
    color: #17160f;
  }
  .cta.primary:hover {
    background: var(--ink);
    border-color: var(--ink);
    transform: translateY(-2px);
  }
  .cta.secondary {
    color: var(--ink);
    border-color: color-mix(in srgb, var(--ink) 30%, transparent);
  }
  .cta.secondary:hover {
    border-color: var(--co2);
    color: var(--co2);
  }
  .arrow {
    margin-left: 8px;
    transition: transform 250ms var(--ease);
  }
  .cta:hover .arrow {
    transform: translateX(5px);
  }
  .label {
    margin: 0 0 8px;
    color: var(--graphite);
    font-size: 12px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }
  ul {
    list-style: none;
    margin: 0;
    padding: 0;
    border-top: 1px solid var(--rule);
  }
  li a {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    grid-template-areas: "name go" "why go";
    gap: 2px 16px;
    align-items: center;
    padding: 16px 4px;
    min-height: 64px;
    border-bottom: 1px solid var(--rule);
    text-decoration: none;
    color: var(--ink);
    transition:
      padding 250ms var(--ease),
      background 250ms var(--ease);
  }
  li a:hover,
  li a:focus-visible {
    padding-inline: 14px;
    background: color-mix(in srgb, var(--co2) 9%, transparent);
  }
  .name {
    grid-area: name;
    font-family: var(--font-display, inherit);
    font-size: 22px;
  }
  .why {
    grid-area: why;
    font-size: 14px;
    color: var(--graphite);
  }
  .go {
    grid-area: go;
    color: var(--co2);
    transition: transform 250ms var(--ease);
  }
  li a:hover .go {
    transform: translateX(4px);
  }
  @media (max-width: 860px) {
    .close {
      grid-template-columns: minmax(0, 1fr);
      align-items: start;
    }
  }
  @media (prefers-reduced-motion: reduce) {
    .cta,
    li a,
    .arrow,
    .go {
      transition: none;
    }
  }
</style>
