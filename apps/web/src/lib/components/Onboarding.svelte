<script lang="ts">
  import { tick, untrack } from "svelte";
  import * as m from "#lib/paraglide/messages.js";

  let { open = $bindable(false) }: { open?: boolean } = $props();

  const KEY = "bc.tour.v1";
  type Step = { selector: string; title: () => string; body: () => string };
  const steps: Step[] = [
    { selector: ".search-section", title: () => m.tour_s1_title(), body: () => m.tour_s1_body() },
    { selector: ".toolbar", title: () => m.tour_s2_title(), body: () => m.tour_s2_body() },
    { selector: ".plate", title: () => m.tour_s3_title(), body: () => m.tour_s3_body() },
    { selector: ".timeline", title: () => m.tour_s4_title(), body: () => m.tour_s4_body() },
    { selector: ".field-notes", title: () => m.tour_s5_title(), body: () => m.tour_s5_body() },
    { selector: ".site-header nav", title: () => m.tour_s6_title(), body: () => m.tour_s6_body() },
  ];

  const read = () => {
    try {
      return localStorage.getItem(KEY);
    } catch {
      return null;
    }
  };
  const remember = (value: string) => {
    try {
      localStorage.setItem(KEY, value);
    } catch {
      /* private mode: the nudge just shows again next visit */
    }
  };

  const visible = (selector: string) => {
    const el = document.querySelector<HTMLElement>(selector);
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0 ? el : null;
  };

  // Only the steps whose element exists and is displayed (e.g. no "Lab" switch on phones).
  let list = $state<Step[]>([]);
  let i = $state(0);
  let rect = $state<{ top: number; left: number; width: number; height: number } | null>(null);
  let cardEl: HTMLElement | undefined = $state();
  let opener: Element | null = null;
  let nudge = $state(false);
  let place = $state<{ top?: number; bottom?: number }>({ bottom: 16 });

  const step = $derived(list[i]);
  const last = $derived(i === list.length - 1);

  function begin() {
    nudge = false;
    list = steps.filter((s) => visible(s.selector));
    if (!list.length) {
      open = false;
      return;
    }
    i = 0;
    opener = document.activeElement;
    focusStep();
  }

  async function focusStep() {
    const el = step && visible(step.selector);
    if (el) {
      const r = el.getBoundingClientRect();
      const inView = r.top >= 0 && r.bottom <= innerHeight;
      if (!inView) {
        const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
        el.scrollIntoView({ block: r.height > innerHeight * 0.7 ? "start" : "center", behavior: reduce ? "auto" : "smooth" });
      }
    }
    await tick();
    cardEl?.querySelector<HTMLElement>("[data-primary]")?.focus({ preventScroll: true });
  }

  function close(done: boolean) {
    remember(done ? "done" : "dismissed");
    open = false;
    rect = null;
    (opener as HTMLElement | null)?.focus?.();
  }

  function go(delta: number) {
    const next = i + delta;
    if (next < 0) return;
    if (next >= list.length) return close(true);
    i = next;
    focusStep();
  }

  // Keep the spotlight glued to its element while the page scrolls, resizes or reflows.
  $effect(() => {
    if (!open) return;
    untrack(begin);
    let frame = 0;
    const track = () => {
      const el = step && visible(step.selector);
      if (el) {
        const r = el.getBoundingClientRect();
        const pad = 8;
        const top = Math.max(r.top - pad, 4);
        const bottom = Math.min(r.bottom + pad, innerHeight - 4);
        const next = {
          top,
          left: Math.max(r.left - pad, 4),
          width: Math.min(r.width + pad * 2, innerWidth - 8),
          height: Math.max(bottom - top, 24),
        };
        if (!rect || next.top !== rect.top || next.left !== rect.left || next.width !== rect.width || next.height !== rect.height) rect = next;
        // Beside the highlighted element when there is room; overlaid on the far edge otherwise.
        const h = (cardEl?.offsetHeight ?? 260) + 28;
        const below = innerHeight - (top + next.height);
        const wanted: { top?: number; bottom?: number } =
          below >= h ? { top: top + next.height + 12 }
          : top >= h ? { bottom: innerHeight - top + 12 }
          : top + next.height / 2 > innerHeight / 2 ? { top: 16 }
          : { bottom: 16 };
        if (wanted.top !== place.top || wanted.bottom !== place.bottom) place = wanted;
      }
      frame = requestAnimationFrame(track);
    };
    frame = requestAnimationFrame(track);
    return () => cancelAnimationFrame(frame);
  });

  function onkey(e: KeyboardEvent) {
    if (!open) return;
    if (e.key === "Escape") {
      e.preventDefault();
      close(false);
    } else if (e.key === "ArrowRight") {
      e.preventDefault();
      go(1);
    } else if (e.key === "ArrowLeft") {
      e.preventDefault();
      go(-1);
    } else if (e.key === "Tab" && cardEl) {
      const items = [...cardEl.querySelectorAll<HTMLElement>("button")];
      const first = items[0], end = items[items.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        end.focus();
      } else if (!e.shiftKey && document.activeElement === end) {
        e.preventDefault();
        first.focus();
      }
    }
  }

  // First visit: a quiet, non-blocking offer instead of a modal that interrupts the reader.
  $effect(() => {
    if (read()) return;
    const id = setTimeout(() => {
      if (!open) nudge = true;
    }, 2500);
    return () => clearTimeout(id);
  });
</script>

<svelte:window onkeydown={onkey} />

{#if nudge && !open}
  <aside class="nudge" aria-label={m.tour_nudge_title()}>
    <p class="t">{m.tour_nudge_title()}</p>
    <p>{m.tour_nudge_body()}</p>
    <div class="row">
      <button class="primary" onclick={() => (open = true)}>{m.tour_start()}</button>
      <button
        onclick={() => {
          remember("dismissed");
          nudge = false;
        }}>{m.tour_not_now()}</button
      >
    </div>
  </aside>
{/if}

{#if open && step}
  <div class="tour" data-testid="tour">
    <!-- Absorbs clicks so the dimmed page cannot be operated by accident. -->
    <div class="catcher" aria-hidden="true"></div>
    {#if rect}
      <div
        class="spot"
        aria-hidden="true"
        style:top="{rect.top}px"
        style:left="{rect.left}px"
        style:width="{rect.width}px"
        style:height="{rect.height}px"
      ></div>
    {/if}
    <div
      class="card"
      role="dialog"
      aria-modal="true"
      aria-label={m.tour_dialog_label()}
      bind:this={cardEl}
      style:top={place.top === undefined ? undefined : `${place.top}px`}
      style:bottom={place.bottom === undefined ? undefined : `${place.bottom}px`}
      style:left={rect ? `clamp(12px, ${rect.left}px, calc(100vw - min(380px, 100vw - 24px) - 12px))` : undefined}
    >
      <p class="count mono" aria-live="polite">{m.tour_step_of({ n: String(i + 1), total: String(list.length) })}</p>
      <h2 data-testid="tour-title">{step.title()}</h2>
      <p class="body">{step.body()}</p>
      <div class="dots" aria-hidden="true">
        {#each list as _, k (k)}<span class:on={k === i}></span>{/each}
      </div>
      <div class="row">
        <button class="ghost" onclick={() => close(false)}>{m.tour_skip()}</button>
        <span class="spacer"></span>
        {#if i > 0}<button onclick={() => go(-1)}>{m.tour_back()}</button>{/if}
        <button class="primary" data-primary onclick={() => go(1)}>{last ? m.tour_done() : m.tour_next()}</button>
      </div>
    </div>
  </div>
{/if}

<style>
  .tour {
    position: fixed;
    inset: 0;
    z-index: 100;
  }
  .catcher {
    position: absolute;
    inset: 0;
  }
  .spot {
    position: fixed;
    pointer-events: none;
    border: 1.5px solid var(--co2);
    /* The huge shadow darkens everything except the highlighted region. */
    box-shadow: 0 0 0 100vmax rgba(8, 8, 7, 0.74);
    transition:
      top 350ms var(--ease),
      left 350ms var(--ease),
      width 350ms var(--ease),
      height 350ms var(--ease);
  }
  .card,
  .nudge {
    background: #14130f;
    color: #ece7dc;
    border: 1px solid #34312a;
    box-shadow: 0 18px 50px rgba(0, 0, 0, 0.5);
  }
  .card {
    position: fixed;
    width: min(380px, calc(100vw - 24px));
    padding: 18px 20px 16px;
  }
  .count {
    margin: 0 0 6px;
    font-size: 11px;
    letter-spacing: 0.12em;
    color: #f2a03d;
  }
  h2 {
    margin: 0 0 8px;
    font: 500 24px/1.15 var(--font-display);
    color: #ece7dc;
  }
  .body {
    margin: 0 0 14px;
    font-size: 15px;
    line-height: 1.55;
    color: #c9c2b4;
  }
  .dots {
    display: flex;
    gap: 6px;
    margin-bottom: 14px;
  }
  .dots span {
    width: 18px;
    height: 2px;
    background: #34312a;
    transition: background 250ms var(--ease);
  }
  .dots span.on {
    background: #f2a03d;
  }
  .row {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .spacer {
    flex: 1;
  }
  .card button,
  .nudge button {
    min-height: 40px;
    padding: 8px 14px;
    font-size: 14px;
    color: #ece7dc;
    background: transparent;
    border: 1px solid #4a463c;
  }
  .card button:hover,
  .nudge button:hover {
    border-color: #f2a03d;
  }
  .card button.primary,
  .nudge button.primary {
    background: #f2a03d;
    border-color: #f2a03d;
    color: #17160f;
    font-weight: 500;
  }
  .card button.ghost {
    border-color: transparent;
    color: #9a9488;
    padding-inline: 4px;
  }
  .nudge {
    position: fixed;
    right: 20px;
    bottom: 20px;
    z-index: 90;
    width: min(320px, calc(100vw - 40px));
    padding: 16px 18px;
    animation: nudge-in 500ms var(--ease) both;
  }
  .nudge p {
    margin: 0 0 12px;
    font-size: 14px;
    line-height: 1.5;
    color: #c9c2b4;
  }
  .nudge .t {
    margin-bottom: 4px;
    font: 500 20px var(--font-display);
    color: #ece7dc;
  }
  @keyframes nudge-in {
    from {
      transform: translateY(16px);
      opacity: 0;
    }
  }
  @media (prefers-reduced-motion: reduce) {
    .spot,
    .dots span {
      transition: none;
    }
    .nudge {
      animation: none;
    }
  }
</style>
