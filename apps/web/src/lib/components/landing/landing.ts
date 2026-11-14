import media from "../../../../static/media/landing/landing-media.json";
import cometJson from "../../../../static/data/comets/3i-atlas/landing.json";
import type { Grid } from "#lib/data/types.js";
import { propagate, worldToPixel } from "#lib/data/coordinates.js";

export type PlateImage = {
  src: string;
  width: number;
  height: number;
  obs_id: string;
  date: string;
  mjd: number;
  lam_um: number;
  det: number;
  collection: string;
  kind: string;
  k: number;
};

export type TargetPlate = {
  slug: string;
  name: string;
  det: number;
  grid: Grid & { pixel_arcsec: number };
  n_frames: number;
  n_visits: number;
  poster: PlateImage;
  pm?: {
    ra0: number;
    dec0: number;
    pmra_masyr: number;
    pmdec_masyr: number;
    ref_epoch_jyear: number;
  } | null;
};

export type BarnardPlate = TargetPlate & {
  epochs: PlateImage[];
  difference: {
    sigma: number;
    reference_count: number | null;
    diff_lambda: PlateImage;
    raw: {
      src: string;
      width: number;
      height: number;
      kind: "raw_subtraction";
      a: PlateImage;
      b: PlateImage;
    };
  };
  gaia_counterpart: {
    source_id: string;
    ra: number;
    dec: number;
    pmra: number;
    pmdec: number;
    ref_epoch: number;
  } | null;
};

export const landingMedia = media as unknown as {
  generated: string;
  credits: string[];
  plates: Record<string, TargetPlate> & { barnard: BarnardPlate };
};

export const TARGET_ORDER = [
  "barnard",
  "eps-indi-b",
  "wise-0855",
  "rw-aur",
  "r-dra",
] as const;

/** UTC calendar date of a data timestamp (data dates stay ISO, never localized). */
export const isoDate = (date: string) => date.slice(0, 10);

/** Wavelength in µm with a decimal point regardless of locale. */
export const fmtLam = (um: number, digits = 2) => um.toFixed(digits);

/** Pixel position of a Gaia source in a stack grid at a given MJD (same math as the Explorer). */
export function gaiaPixel(
  star: NonNullable<BarnardPlate["gaia_counterpart"]>,
  grid: Grid,
  mjd: number,
): [number, number] {
  const [ra, dec] = propagate(
    star.ra,
    star.dec,
    star.pmra,
    star.pmdec,
    star.ref_epoch,
    mjd,
  );
  return worldToPixel(ra, dec, grid);
}

export { fmtSciUnicode } from "#lib/data/format.js";

/** Contract for the coordinator-produced 3I/ATLAS packet (not yet published). */
export type CometPacket = {
  target: string;
  plates: {
    poster: string;
    /** Optional: enables the scale bar and the N/E mark; omitted plates show neither. */
    pixel_arcsec?: number;
    nx?: number;
    north_up?: boolean;
    epochs: {
      image: string;
      width?: number;
      height?: number;
      mjd: number;
      lambda_um: number;
      obs_id: string;
      credit: string;
    }[];
  };
  measurements: {
    label: string;
    label_es?: string;
    caveat_es?: string;
    value: number;
    lo: number;
    hi: number;
    unit: string;
    caveat: string;
    source: string;
  }[];
  validation: {
    caveat_es?: string;
    species: string;
    measured: number;
    published_lo: number;
    published_hi: number;
    unit: string;
    caveat: string;
    source: string;
  }[];
  credits: string[];
};

export const COMET_PACKET_URL = "/data/comets/3i-atlas/landing.json";

export type CometState =
  | { status: "idle" | "loading" }
  | { status: "missing"; reason: string }
  | { status: "ready"; packet: CometPacket };

const isNum = (x: unknown) => typeof x === "number" && Number.isFinite(x);
const isStr = (x: unknown) => typeof x === "string" && x.length > 0;

/** Strict validation: anything that does not match the agreed contract is treated as missing. */
export function parseCometPacket(value: unknown): CometPacket | null {
  const p = value as CometPacket;
  if (!p || typeof p !== "object" || !isStr(p.target)) return null;
  if (!p.plates || !isStr(p.plates.poster) || !Array.isArray(p.plates.epochs))
    return null;
  if (
    !p.plates.epochs.every(
      (e) =>
        isStr(e.image) &&
        isNum(e.mjd) &&
        isNum(e.lambda_um) &&
        isStr(e.obs_id) &&
        isStr(e.credit),
    )
  )
    return null;
  if (
    !Array.isArray(p.measurements) ||
    !p.measurements.every(
      (m) =>
        isStr(m.label) &&
        isNum(m.value) &&
        isNum(m.lo) &&
        isNum(m.hi) &&
        typeof m.unit === "string" &&
        isStr(m.caveat) &&
        isStr(m.source),
    )
  )
    return null;
  if (
    !Array.isArray(p.validation) ||
    !p.validation.every(
      (v) =>
        isStr(v.species) &&
        isNum(v.measured) &&
        isNum(v.published_lo) &&
        isNum(v.published_hi) &&
        typeof v.unit === "string" &&
        isStr(v.caveat) &&
        isStr(v.source),
    )
  )
    return null;
  if (!Array.isArray(p.credits) || !p.credits.every(isStr)) return null;
  return p;
}

let pending: Promise<CometState> | null = null;

/** Fetch the 3I packet once per page. A 404 or a SPA fallback page both mean "not published yet". */
export function loadCometPacket(fetcher: typeof fetch = fetch) {
  pending ??= fetcher(COMET_PACKET_URL, { headers: { accept: "application/json" } })
    .then(async (response): Promise<CometState> => {
      if (!response.ok)
        return { status: "missing", reason: `HTTP ${response.status}` };
      const text = await response.text();
      let json: unknown;
      try {
        json = JSON.parse(text);
      } catch {
        return { status: "missing", reason: "not JSON" };
      }
      const packet = parseCometPacket(json);
      return packet
        ? { status: "ready", packet }
        : { status: "missing", reason: "contract mismatch" };
    })
    .catch(() => ({ status: "missing", reason: "network" }) as CometState);
  return pending;
}

/** Test hook: forget the cached request. */
export function resetCometPacket() {
  pending = null;
}

/** Spanish text when the packet provides it, English otherwise. */
export const localized = (en: string, es: string | undefined, locale: string) =>
  locale === "es" && es ? es : en;

/**
 * The published 3I/ATLAS packet, validated at build time so the prerendered page starts with
 * it. If the file ever stops matching the contract, the page falls back to the pending state
 * and to the deferred fetch above.
 */
export const bundledComet: CometState = (() => {
  const packet = parseCometPacket(cometJson);
  return packet ? { status: "ready", packet } : { status: "idle" };
})();
