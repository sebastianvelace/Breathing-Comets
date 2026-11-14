<script lang="ts">
  import { untrack } from "svelte";
  // Decorative sky: static SVG dots drifting as whole layers (compositor-only transforms).
  // No canvas, no requestAnimationFrame, no per-frame JavaScript.
  let {
    count = 110,
    constellations = true,
    fixed = false,
    seed = 7,
  }: { count?: number; constellations?: boolean; fixed?: boolean; seed?: number } = $props();

  const W = 1600,
    H = 1000;
  function rng(a: number) {
    return () => {
      a |= 0;
      a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  // Generated once: the sky is static decoration, so the initial props are the only ones read.
  const init = untrack(() => ({ seed, count }));
  const r = rng(init.seed);
  const star = () => ({
    x: +(r() * W).toFixed(1),
    y: +(r() * H).toFixed(1),
    r: +(0.5 + r() * r() * 1.5).toFixed(2),
    o: +(0.25 + r() * 0.7).toFixed(2),
  });
  const far = Array.from({ length: Math.round(init.count * 0.65) }, star);
  const near = Array.from({ length: Math.round(init.count * 0.35) }, star);
  const twinkles = Array.from({ length: 7 }, (_, i) => ({
    x: +(8 + r() * 84).toFixed(1),
    y: +(8 + r() * 84).toFixed(1),
    d: +(i * 0.9).toFixed(1),
  }));

  // Hand-placed figures: nodes joined by hairlines, like a sky chart.
  const figures = [
    { pts: [[1010, 150], [985, 205], [968, 268]], links: [[0, 1], [1, 2]] },
    { pts: [[1180, 330], [1280, 240], [1400, 330], [1408, 332]], links: [[0, 1], [1, 2]] },
    { pts: [[980, 620], [1004, 672], [1082, 694], [1140, 686], [1048, 766], [1000, 890]], links: [[0, 1], [1, 2], [2, 3], [0, 2], [1, 4], [2, 4], [3, 4], [4, 5]] },
    { pts: [[250, 760], [330, 800], [420, 770], [470, 840]], links: [[0, 1], [1, 2], [2, 3]] },
  ];
</script>

<div class="sky" class:fixed aria-hidden="true">
  <svg class="layer far" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">
    {#each far as s, i (i)}<circle cx={s.x} cy={s.y} r={s.r} opacity={s.o} />{/each}
  </svg>
  <svg class="layer near" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">
    {#each near as s, i (i)}<circle cx={s.x} cy={s.y} r={s.r * 1.25} opacity={s.o} />{/each}
  </svg>
  {#if constellations}
    <svg class="layer figures" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">
      {#each figures as f, k (k)}
        <g>
          {#each f.links as [a, b], j (j)}
            <line x1={f.pts[a][0]} y1={f.pts[a][1]} x2={f.pts[b][0]} y2={f.pts[b][1]} />
          {/each}
          {#each f.pts as [x, y], j (j)}<circle cx={x} cy={y} r="2.6" />{/each}
        </g>
      {/each}
    </svg>
  {/if}
  {#each twinkles as t, i (i)}
    <i class="twinkle" style:left="{t.x}%" style:top="{t.y}%" style:animation-delay="-{t.d}s"></i>
  {/each}
</div>

<style>
  .sky {
    position: absolute;
    inset: 0;
    overflow: hidden;
    pointer-events: none;
    background:
      radial-gradient(55% 60% at 80% 30%, rgba(46, 84, 201, 0.2), transparent 70%),
      radial-gradient(45% 55% at 12% 85%, rgba(72, 52, 170, 0.14), transparent 70%);
  }
  .sky.fixed {
    position: fixed;
    z-index: 0;
  }
  .layer {
    position: absolute;
    inset: -4%;
    width: 108%;
    height: 108%;
    fill: #dbe6ff;
    will-change: transform;
  }
  .far {
    animation: drift-a 90s ease-in-out infinite alternate;
  }
  .near {
    fill: #ffffff;
    animation: drift-b 70s ease-in-out infinite alternate;
  }
  .figures {
    fill: #a9c4ff;
    opacity: 0.55;
    animation: drift-a 120s ease-in-out infinite alternate-reverse;
  }
  .figures line {
    stroke: #a9c4ff;
    stroke-width: 1;
    stroke-opacity: 0.3;
    vector-effect: non-scaling-stroke;
  }
  .twinkle {
    position: absolute;
    width: 3px;
    height: 3px;
    border-radius: 50%;
    background: #fff;
    box-shadow: 0 0 8px 2px rgba(150, 190, 255, 0.7);
    animation: twinkle 6.3s ease-in-out infinite;
  }
  @keyframes drift-a {
    from { transform: translate3d(-1.5%, -1%, 0); }
    to { transform: translate3d(1.5%, 1.2%, 0); }
  }
  @keyframes drift-b {
    from { transform: translate3d(2%, 1.5%, 0); }
    to { transform: translate3d(-2%, -1.5%, 0); }
  }
  @keyframes twinkle {
    0%, 100% { opacity: 0.15; transform: scale(0.7); }
    50% { opacity: 1; transform: scale(1.15); }
  }
  @media (prefers-reduced-motion: reduce) {
    .layer,
    .twinkle {
      animation: none;
    }
  }
</style>
