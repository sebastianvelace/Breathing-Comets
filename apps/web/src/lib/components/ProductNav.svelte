<script lang="ts">
  import * as m from "#lib/paraglide/messages.js";
  import { localizeHref } from "#lib/paraglide/runtime.js";
  let { active = "" }: { active?: "" | "explore" | "comets" | "neo" } = $props();
</script>

<nav class="product-nav" aria-label={m.nav_main()} data-testid="product-nav">
  <a href={localizeHref("/explore")} aria-current={active === "explore" ? "page" : undefined}>{m.nav_explore()}</a>
  <a href={localizeHref("/comets")} aria-current={active === "comets" ? "page" : undefined}>{m.nav_comets()}</a>
  <a href={localizeHref("/neo")} aria-current={active === "neo" ? "page" : undefined}>{m.nav_asteroids()}</a>
</nav>

<style>
  .product-nav { display: flex; align-items: center; gap: 4px; }
  a { display: inline-flex; align-items: center; justify-content: center; min-height: 42px; padding: 8px 14px; border-radius: var(--r-pill); text-decoration: none; font-size: 14px; font-weight: 500; color: var(--ink-2); white-space: nowrap; }
  a:hover { color: var(--ink); background: color-mix(in srgb, var(--ink) 7%, transparent); }
  a[aria-current] { color: var(--accent); background: color-mix(in srgb, var(--accent) 12%, transparent); }
  @media (max-width: 700px) { .product-nav { width: 100%; } a { flex: 1; padding: 8px 12px; } }
</style>
