<script lang="ts">
  import * as m from "#lib/paraglide/messages.js";
  import { localizeHref } from "#lib/paraglide/runtime.js";
</script>

<nav class="legal-links" aria-label={m.legal_terms() + " · " + m.legal_privacy()} data-testid="legal-links">
  <a href={localizeHref("/terms")}>{m.legal_terms()}</a>
  <span aria-hidden="true">·</span>
  <a href={localizeHref("/privacy")}>{m.legal_privacy()}</a>
  <span aria-hidden="true">·</span>
  <span>{m.legal_not_nasa()}</span>
</nav>

<style>
  .legal-links { display: flex; flex-wrap: wrap; gap: 4px 10px; margin-top: 10px; font: 12px/1.6 var(--font-data); color: var(--graphite); }
  a { color: inherit; text-decoration: underline; text-underline-offset: 3px; }
  a:hover { color: var(--accent); }
</style>
