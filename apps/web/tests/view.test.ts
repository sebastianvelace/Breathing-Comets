import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { parseView, serializeView, nearestFrame } from "../src/lib/state/view";

it("direct target links use the same prepared detector as the target picker", () => {
  for (const slug of ["eps-indi-b", "wise-0855", "rw-aur", "r-dra"]) {
    expect(parseView(new URLSearchParams({target: slug})).det).toBe(6);
    expect(parseView(new URLSearchParams({target: slug, det: "4"})).det).toBe(4);
  }
  expect(parseView(new URLSearchParams({target: "barnard"})).det).toBe(4);
});
import {
  worldToPixel,
  pixelToWorld,
  propagate,
  fmtSci,
} from "../src/lib/data/coordinates";
import { parseSpxf, decodedSpxfStream } from "../src/lib/data/spxf";

describe("shared scientific view", () => {
  it("round trips every URL field at the specified precision", () => {
    const v = parseView(
      new URLSearchParams(
        "target=wise-0855&ra=133.759765&dec=-7.242182&fov=0.25&det=6&ch=4.623&t=61041.125&mode=blink&a=60900.001&b=61200.002&layers=gaia,jpl,grid&stretch=asinh:0.5:99.5&lut=plate&ui=lab&lang=es",
      ),
    );
    expect(parseView(serializeView(v))).toEqual(v);
    expect(serializeView(v).get("ra")).toBe("133.759765");
    expect(serializeView(v).get("t")).toBe("61041.125");
  });
  it("rejects nonfinite numbers and bounds coordinates", () => {
    const v = parseView(
      new URLSearchParams("ra=-1&dec=100&det=200&fov=NaN&t=Infinity"),
    );
    expect(v.ra).toBe(359);
    expect(v.dec).toBe(90);
    expect(v.det).toBe(6);
    expect(v.fov).toBe(0.25);
    expect(v.t).toBeUndefined();
  });
  it("matches rounded shared MJD values to actual frames", () => {
    expect(nearestFrame([61000.123456, 61001.234567], 61001.235)).toBe(1);
  });
  it("parses a complete real Python-produced stack", () => {
    const raw = gunzipSync(
      readFileSync("static/data/targets/barnard/D4.spxf.gz"),
    );
    const parsed = parseSpxf(
      raw.buffer.slice(raw.byteOffset, raw.byteOffset + raw.byteLength),
    );
    expect(parsed.header.grid.nx).toBe(147);
    expect(parsed.frames.length).toBeGreaterThanOrEqual(10);
    expect(parsed.frames.every((f) => f.flux.some(Number.isFinite))).toBe(true);
  });
  it("propagates Barnard to the supplied reference position", () => {
    const data = JSON.parse(readFileSync("static/data/targets.json", "utf8"))
      .targets[0];
    const [ra, dec] = propagate(
      data.ra_j2000,
      data.dec_j2000,
      data.pmra_masyr,
      data.pmdec_masyr,
      2000,
      61041,
    );
    expect(
      Math.abs(ra - data.pos_2026_01_01[0]) *
        Math.cos((dec * Math.PI) / 180) *
        3600,
    ).toBeLessThan(0.1);
    expect(Math.abs(dec - data.pos_2026_01_01[1]) * 3600).toBeLessThan(0.1);
  });
  it.each(
    Array.from({ length: 20 }, (_, i) => ({
      ra: (359.99 + i * 19) % 360,
      dec: -89 + (i * 178) / 19,
      x: 14 + i * 5.8,
      y: 136 - i * 5.3,
    })),
  )("round trips TAN coordinates $ra, $dec", ({ ra, dec, x, y }) => {
    const grid = {
      nx: 147,
      ny: 147,
      crval: [ra, dec] as [number, number],
      crpix: [74, 74] as [number, number],
      cdelt_deg: [-6.15 / 3600, 6.15 / 3600] as [number, number],
      north_up: true,
    };
    const world = pixelToWorld(x, y, grid),
      pixel = worldToPixel(...world, grid);
    expect(pixel[0]).toBeCloseTo(x, 7);
    expect(pixel[1]).toBeCloseTo(y, 7);
  });
  it("formats scientific values with a decimal dot", () => {
    expect(fmtSci(1.23456)).toBe("1.23");
    expect(fmtSci(NaN)).toBe("—");
    expect(fmtSci(1.17e27)).toBe("1.17e27");
  });
});

it.each([true, false])(
  "decodes real stack with compressed=%s, including HTTP-decoded bodies",
  async (compressed) => {
    const file = readFileSync("static/data/targets/barnard/D4.spxf.gz");
    const bytes = compressed ? file : gunzipSync(file);
    const stream = await decodedSpxfStream(new Response(bytes));
    const data = parseSpxf(await new Response(stream).arrayBuffer());
    expect(data.frames.length).toBe(24);
  },
);

it("uses the live API when coordinates are shared without a target", () => {
  expect(parseView(new URLSearchParams("ra=150.4&dec=1.6")).target).toBe("");
});
