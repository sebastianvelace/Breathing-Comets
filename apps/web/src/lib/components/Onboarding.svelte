<script lang="ts">
  import { tick, untrack } from "svelte";
  import * as m from "#lib/paraglide/messages.js";

  let { open = $bindable(false), offer = $bindable(false) }: { open?: boolean; offer?: boolean } = $props();

  const KEY = "bc.tour.v1";
  type Step = { selector: string; title: () => string; body: () => string };
  const steps: Step[] = [
    { selector: ".search-section", title: () => m.tour_s1_title(), body: () => m.tour_s1_body() },
    { selector: ".toolbar", title: () => m.tour_s2_title(), body: () => m.tour_s2_body() },
    { selector: ".plate", title: () => m.tour_s3_title(), body: () => m.tour_s3_body() },
    { selector: ".timeline", title: () => m.tour_s4_title(), body: () => m.tour_s4_body() },
    { selector: ".field-notes", title: () => m.tour_s5_title(), body: () => m.tour_s5_body() },
    { selector: ".header-actions", title: () => m.tour_s6_title(), body: () => m.tour_s6_body() },
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
  let place = $state<{ top?: number; bottom?: number }>({ bottom: 16 });

  const step = $derived(list[i]);
  const last = $derived(i === list.length - 1);

  function begin() {
    offer = false;
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
      if (!open) offer = true;
    }, 2500);
    return () => clearTimeout(id);
  });
</script>

<svelte:window onkeydown={onkey} />

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
      style:left={rect ? `clamp(12px, ${rect.left}px, calc(100vw - min(400px, 100vw - 24px) - 12px))` : undefined}
    >
      {#key i}
        <div class="content">
          <div class="head">
            <span class="badge" aria-hidden="true">{i + 1}</span>
            <div>
              <p class="count" aria-live="polite">{m.tour_step_of({ n: String(i + 1), total: String(list.length) })}</p>
              <h2 data-testid="tour-title">{step.title()}</h2>
            </div>
          </div>
          <p class="body">{step.body()}</p>
        </div>
      {/key}
      <div class="row">
        <div class="dots" aria-hidden="true">
          {#each list as _, k (k)}<span class:on={k === i} class:past={k < i}></span>{/each}
        </div>
        <span class="spacer"></span>
        <button class="ghost" onclick={() => close(false)}>{m.tour_skip()}</button>
        {#if i > 0}<button class="soft" onclick={() => go(-1)} aria-label={m.tour_back()}>←</button>{/if}
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
  /* A soft, rounded window of light: the huge outer shadow darkens everything else. */
  .spot {
    position: fixed;
    pointer-events: none;
    border-radius: 22px;
    box-shadow:
      0 0 0 2px rgba(140, 180, 255, 0.85),
      0 0 46px 8px rgba(100, 150, 255, 0.4),
      0 0 0 100vmax rgba(3, 6, 18, 0.76);
    transition:
      top 450ms var(--ease),
      left 450ms var(--ease),
      width 450ms var(--ease),
      height 450ms var(--ease);
  }
  .spot::after {
    content: "";
    position: absolute;
    inset: -6px;
    border-radius: 28px;
    border: 2px solid rgba(140, 180, 255, 0.6);
    animation: halo 2.4s var(--ease) infinite;
  }
  @keyframes halo {
    from {
      opacity: 0.9;
      transform: scale(1);
    }
    to {
      opacity: 0;
      transform: scale(1.035);
    }
  }
  .card {
    color: #e8ecf8;
    background: linear-gradient(160deg, rgba(24, 36, 78, 0.92), rgba(9, 14, 34, 0.94));
    backdrop-filter: blur(16px) saturate(1.3);
    box-shadow:
      inset 0 0 0 1px rgba(140, 180, 255, 0.22),
      0 24px 70px -20px rgba(0, 0, 0, 0.8),
      0 0 60px -20px rgba(90, 140, 255, 0.5);
  }
  .card {
    position: fixed;
    width: min(400px, calc(100vw - 24px));
    padding: 22px 22px 18px;
    border-radius: 28px;
    transition:
      top 450ms var(--ease),
      bottom 450ms var(--ease),
      left 450ms var(--ease);
  }
  .content {
    animation: step-in 420ms var(--ease) both;
  }
  @keyframes step-in {
    from {
      opacity: 0;
      transform: translateY(8px);
    }
  }
  .head {
    display: flex;
    gap: 14px;
    align-items: center;
    margin-bottom: 12px;
  }
  .badge {
    flex: none;
    display: grid;
    place-items: center;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    font: 600 18px var(--font-display);
    color: #061033;
    background: radial-gradient(circle at 30% 25%, #cfe0ff, #7aa7ff 60%, #4a7bf0);
    box-shadow: 0 0 24px rgba(122, 167, 255, 0.6);
  }
  .count {
    margin: 0 0 2px;
    font-size: 12px;
    color: #9db4e8;
  }
  h2 {
    margin: 0;
    font: 600 21px/1.2 var(--font-display);
    letter-spacing: -0.02em;
    color: #f2f5ff;
  }
  .body {
    margin: 0 0 18px;
    font-size: 15px;
    line-height: 1.6;
    color: #c0cae6;
  }
  .dots {
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .dots span {
    width: 7px;
    height: 7px;
    border-radius: 99px;
    background: rgba(160, 185, 240, 0.25);
    transition:
      width 300ms var(--ease),
      background 300ms var(--ease);
  }
  .dots span.past {
    background: rgba(140, 180, 255, 0.6);
  }
  .dots span.on {
    width: 22px;
    background: #7aa7ff;
  }
  .row {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .spacer {
    flex: 1;
  }
  .card button {
    min-height: 40px;
    padding: 8px 18px;
    font-size: 14px;
    color: #e8ecf8;
    border: 0;
    border-radius: 999px;
    background: rgba(160, 185, 240, 0.14);
  }
  .card button:hover {
    background: rgba(160, 185, 240, 0.24);
  }
  .card button.soft {
    padding-inline: 14px;
  }
  .card button.primary {
    background: #7aa7ff;
    color: #061033;
    font-weight: 600;
    box-shadow: 0 8px 24px -8px rgba(122, 167, 255, 0.9);
  }
  .card button.primary:hover {
    background: #a6c4ff;
  }
  .card button.ghost {
    background: transparent;
    color: #9aa7cc;
    padding-inline: 10px;
  }
  .card button.ghost:hover {
    color: #e8ecf8;
    background: transparent;
  }
  @media (prefers-reduced-motion: reduce) {
    .spot,
    .card,
    .dots span {
      transition: none;
    }
    .spot::after,
    .content {
      animation: none;
    }
    .spot::after {
      opacity: 0;
    }
  }
</style>
