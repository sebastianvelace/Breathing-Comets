import { describe, it, expect } from "vitest";
import { existsSync, readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import {
  fmtSciUnicode,
  gaiaPixel,
  landingMedia,
  loadCometPacket,
  parseCometPacket,
  resetCometPacket,
  TARGET_ORDER,
} from "../src/lib/components/landing/landing";

const STATIC = new URL("../static/", import.meta.url);

function stackHeader(path: string) {
  const raw = gunzipSync(readFileSync(new URL(path, STATIC)));
  const length = raw.readUInt32LE(8);
  return JSON.parse(raw.subarray(16, 16 + length).toString("utf8"));
}

// Test-only contract fixture: shape of the agreed 3I packet, NOT product data.
const fixture = () => ({
  target: "3I/ATLAS",
  plates: {
    poster: "/media/test/poster.webp",
    epochs: [
      { image: "/media/test/e0.webp", mjd: 60900.5, lambda_um: 4.3, obs_id: "TEST_0", credit: "test" },
    ],
  },
  measurements: [
    { label: "Q(test)", value: 2, lo: 1, hi: 3, unit: "s⁻¹", caveat: "test caveat", source: "test" },
  ],
  validation: [
    { species: "TEST", measured: 2, published_lo: 1, published_hi: 3, unit: "s⁻¹", caveat: "c", source: "s" },
  ],
  credits: ["test credit"],
});

describe("landing media are derived from the published packages", () => {
  it("references existing WebP files for all five targets", () => {
    for (const slug of TARGET_ORDER) {
      const plate = landingMedia.plates[slug];
      expect(plate, slug).toBeDefined();
      expect(existsSync(new URL(`.${plate.poster.src}`, STATIC))).toBe(true);
      expect(plate.poster.width).toBe(plate.grid.nx);
      expect(plate.poster.height).toBe(plate.grid.ny);
    }
    const barnard = landingMedia.plates.barnard;
    const files = [
      ...barnard.epochs.map((e) => e.src),
      barnard.difference.diff_lambda.src,
      barnard.difference.raw.src,
    ];
    for (const src of files) expect(existsSync(new URL(`.${src}`, STATIC)), src).toBe(true);
  });

  it("uses each stack's own stretch_hint, grid and frame metadata", () => {
    for (const slug of TARGET_ORDER) {
      const plate = landingMedia.plates[slug] as unknown as {
        det: number;
        stretch: { lo: number; hi: number };
        grid: unknown;
        poster: { obs_id: string; k: number; lam_um: number };
      };
      const manifest = JSON.parse(
        readFileSync(new URL(`data/targets/${slug}/manifest.json`, STATIC), "utf8"),
      );
      expect(plate.det).toBe(manifest.default_det);
      const header = stackHeader(`data/targets/${slug}/${manifest.stacks[String(plate.det)]}`);
      expect(plate.stretch.lo).toBe(header.stretch_hint.lo);
      expect(plate.stretch.hi).toBe(header.stretch_hint.hi);
      expect(plate.grid).toEqual(header.grid);
      const frame = header.frames[plate.poster.k];
      expect(frame.obs_id).toBe(plate.poster.obs_id);
      expect(frame.lam_um).toBe(plate.poster.lam_um);
    }
  });

  it("labels the raw subtraction separately from the published Diff λ frame", () => {
    const d = landingMedia.plates.barnard.difference;
    expect(d.raw.kind).toBe("raw_subtraction");
    expect(d.diff_lambda.kind).toBe("diff_lambda");
    expect(d.raw.a.obs_id).not.toBe(d.raw.b.obs_id);
    expect(d.raw.b.obs_id).toBe(d.diff_lambda.obs_id);
    const header = stackHeader("data/targets/barnard/D4.diff.spxf.gz");
    expect(header.kind).toBe("diff");
    expect(header.frames[d.diff_lambda.k].diff_sigma).toBe(d.sigma);
  });

  it("predicts Barnard's Gaia shift between the first and last visit", () => {
    const b = landingMedia.plates.barnard;
    const star = b.gaia_counterpart!;
    expect(star.source_id).toBe("4472832130942575872");
    const first = b.epochs[0],
      last = b.epochs[b.epochs.length - 1];
    const [x0, y0] = gaiaPixel(star, b.grid, first.mjd);
    const [x1, y1] = gaiaPixel(star, b.grid, last.mjd);
    const shift = Math.hypot(x1 - x0, y1 - y0);
    expect(shift).toBeGreaterThan(1.5);
    expect(shift).toBeLessThan(1.9);
    expect(y1).toBeGreaterThan(y0); // moving north
  });
});

describe("scientific number formatting", () => {
  it("keeps a decimal point and Unicode exponents", () => {
    expect(fmtSciUnicode(1.17e27)).toBe("1.17 × 10²⁷");
    expect(fmtSciUnicode(4.0e26)).toBe("4.00 × 10²⁶");
    expect(fmtSciUnicode(2.7e-5)).toBe("2.70 × 10⁻⁵");
    expect(fmtSciUnicode(0.994)).toBe("0.994");
    expect(fmtSciUnicode(Number.NaN)).toBe("—");
  });
});

describe("3I/ATLAS packet contract", () => {
  it("accepts the agreed shape and rejects partial packets", () => {
    expect(parseCometPacket(fixture())).not.toBeNull();
    const noCaveat = fixture();
    noCaveat.measurements[0].caveat = "";
    expect(parseCometPacket(noCaveat)).toBeNull();
    const badEpoch = fixture() as unknown as { plates: { epochs: { mjd: unknown }[] } };
    badEpoch.plates.epochs[0].mjd = "60900";
    expect(parseCometPacket(badEpoch)).toBeNull();
    expect(parseCometPacket({ ...fixture(), validation: undefined })).toBeNull();
    expect(parseCometPacket(null)).toBeNull();
  });

  it("treats 404 and the SPA fallback page as not published", async () => {
    resetCometPacket();
    const notFound = (async () => new Response("", { status: 404 })) as typeof fetch;
    expect(await loadCometPacket(notFound)).toEqual({ status: "missing", reason: "HTTP 404" });
    resetCometPacket();
    const html = (async () =>
      new Response("<!doctype html><html></html>", { status: 200 })) as typeof fetch;
    expect(await loadCometPacket(html)).toEqual({ status: "missing", reason: "not JSON" });
    resetCometPacket();
    const ok = (async () => new Response(JSON.stringify(fixture()))) as typeof fetch;
    expect((await loadCometPacket(ok)).status).toBe("ready");
    resetCometPacket();
  });
});

describe("landing messages", () => {
  const en = JSON.parse(readFileSync(new URL("../messages/landing/en.json", import.meta.url), "utf8"));
  const es = JSON.parse(readFileSync(new URL("../messages/landing/es.json", import.meta.url), "utf8"));
  const keys = (o: Record<string, string>) => Object.keys(o).filter((k) => k !== "$schema");

  it("has identical, prefixed keys and parameters in both languages", () => {
    expect(keys(es).sort()).toEqual(keys(en).sort());
    for (const k of keys(en)) {
      expect(k.startsWith("landing_")).toBe(true);
      const params = (s: string) => [...s.matchAll(/\{(\w+)\}/g)].map((x) => x[1]).sort();
      expect(params(es[k]), k).toEqual(params(en[k]));
    }
  });

  it("contains no hand-written measurements", () => {
    // Standalone numbers are allowed only for instrument/narrative facts, never results.
    // Designations such as 2MASS, D4, DR3 or 3I are not numbers.
    const allowed = /^(102|1930|1|5|4\.5|1\.35|0\.7|12\.3|3|2026)$/;
    for (const dict of [en, es])
      for (const k of keys(dict)) {
        const digits = String(dict[k]).replace(/\{\w+\}|§\d+/g, "").match(/(?<![\w.])\d+(?:\.\d+)?(?!\w)/g) ?? [];
        for (const d of digits) expect(d, `${k}: ${dict[k]}`).toMatch(allowed);
      }
  });

  it("never uses a decimal comma in Spanish numbers", () => {
    for (const k of keys(es)) expect(es[k], k).not.toMatch(/\d,\d/);
  });
});

describe("published 3I/ATLAS packet", () => {
  const packet = JSON.parse(
    readFileSync(new URL("data/comets/3i-atlas/landing.json", STATIC), "utf8"),
  );
  const atlas = JSON.parse(readFileSync(new URL("data/comets/index.json", STATIC), "utf8"));

  it("satisfies the strict contract and its images exist", () => {
    expect(parseCometPacket(packet)).not.toBeNull();
    expect(existsSync(new URL(`.${packet.plates.poster}`, STATIC))).toBe(true);
    expect(packet.plates.epochs.length).toBeGreaterThanOrEqual(10);
    for (const e of packet.plates.epochs) {
      expect(existsSync(new URL(`.${e.image}`, STATIC)), e.image).toBe(true);
      expect(e.width).toBe(packet.plates.nx);
    }
  });

  it("frames come from the stored tracked stack with its stretch", () => {
    const header = stackHeader(`data/comets/3i-atlas/${packet.stack.file}`);
    expect(header.target.track).toBe("2025 N1");
    expect(packet.stack.stretch.lo).toBe(header.stretch_hint.lo);
    expect(packet.stack.stretch.hi).toBe(header.stretch_hint.hi);
    const byObs = new Map<string, { mjd: number; lam_um: number }>(
      header.frames.map((f: { obs_id: string; mjd: number; lam_um: number }) => [f.obs_id, f]),
    );
    for (const e of packet.plates.epochs) {
      const f = byObs.get(e.obs_id)!;
      expect(f, e.obs_id).toBeDefined();
      expect(e.mjd).toBe(f.mjd);
      expect(e.lambda_um).toBe(f.lam_um);
    }
    expect(packet.plates.pixel_arcsec).toBe(header.grid.pixel_arcsec);
  });

  it("measurements and validation equal the atlas, each with a caveat", () => {
    const aug = atlas.validation.find((v: { id: string }) => v.id === "3i-atlas_co2_2025-08");
    expect(packet.measurements[0].value).toBe(aug.measured);
    expect(packet.measurements[0].lo).toBe(aug.measured_lo);
    const dec = atlas.comets.find((c: { slug: string }) => c.slug === "3i-atlas");
    expect(packet.measurements[1].value).toBe(dec.co2.q50);
    expect(packet.measurements[1].caveat).toContain("fits poorly");
    for (const m of packet.measurements) {
      expect(m.caveat.length).toBeGreaterThan(20);
      expect(m.caveat_es.length).toBeGreaterThan(20);
      expect(m.caveat_es).not.toMatch(/\d,\d/);
    }
    expect(packet.validation.length).toBe(atlas.validation.length);
  });
});

describe("derived channel table for the ribbon", () => {
  it("equals the source channels", () => {
    const src = JSON.parse(readFileSync(new URL("data/channels.json", STATIC), "utf8")).channels;
    const lite = JSON.parse(readFileSync(new URL("../src/lib/data/channels-lite.json", import.meta.url), "utf8"));
    expect(lite.rows.length).toBe(src.length);
    lite.rows.forEach(([frame, lam, R]: number[], i: number) => {
      expect(frame).toBe(src[i].frame);
      expect(lam).toBeCloseTo(src[i].wavelength_um, 3);
      expect(R).toBe(Math.round(src[i].R));
    });
  });
});

describe("field-note message table", () => {
  it("covers every note_ message in en.json and es.json", async () => {
    const { noteMessages } = await import("../src/lib/data/noteMessages");
    for (const loc of ["en", "es"]) {
      const keys = Object.keys(
        JSON.parse(readFileSync(new URL(`../messages/${loc}.json`, import.meta.url), "utf8")),
      ).filter((k) => k.startsWith("note_"));
      for (const k of keys) expect(noteMessages[k], `${loc}:${k}`).toBeTypeOf("function");
    }
  });
});
