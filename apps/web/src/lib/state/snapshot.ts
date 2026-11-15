import type { Manifest, Stack } from "#lib/data/types.js";
import type { View } from "./view.js";

/** Identify the requested data, independently of playback and presentation. */
export function acquisitionKey(view: View): string {
  return JSON.stringify(view.target
    ? [view.target, view.det]
    : ["", view.det, view.ra, view.dec, view.fov]);
}

/** Capture the displayed observation without mutating the request state. */
export function snapshot(view: View, manifest: Manifest, base: Stack, index: number, a: number, b: number): View {
  return {
    ...view,
    ra: manifest.ra,
    dec: manifest.dec,
    fov: manifest.fov_deg,
    t: base.header.frames[index]?.mjd,
    ch: view.mode === "cube" ? view.ch : base.header.frames[index]?.lam_um,
    a: base.header.frames[a]?.mjd,
    b: base.header.frames[b]?.mjd,
  };
}
