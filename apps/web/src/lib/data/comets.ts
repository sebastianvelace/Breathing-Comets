import atlas from "../../../static/data/comets/index.json";
import * as m from "#lib/paraglide/messages.js";

export type CometStatus = "detected" | "with_systematics" | "marginal" | "not_detected";
type Raw = (typeof atlas.comets)[number];
export type CometEntry = Omit<Raw, "flags"> & { flags: string[] };
export const cometAtlas = { ...atlas, comets: atlas.comets as CometEntry[] };
export const STATUSES: CometStatus[] = ["detected", "with_systematics", "marginal", "not_detected"];

export function statusLabel(status: CometStatus): string {
  switch (status) {
    case "detected": return m.comets_status_detected();
    case "with_systematics": return m.comets_status_with_systematics();
    case "marginal": return m.comets_status_marginal();
    case "not_detected": return m.comets_status_not_detected();
  }
}

export function classLabel(k: string): string {
  switch (k) {
    case "no_coverage": return m.comets_class_no_coverage();
    case "no_data": return m.comets_class_no_data();
    case "upper_limit": return m.comets_class_upper_limit();
    case "candidate": return m.comets_class_candidate();
    case "robust_detection": return m.comets_class_robust_detection();
    default: return m.comets_class_detection();
  }
}

/** Median fractional drop of Q when the outflow speed is 0.50 instead of 0.85 r^-0.5 km/s (from the data). */
export function velocityDropPercent(comets: CometEntry[]): number {
  const v = comets.map((c) => c.co2.sys_v).sort((a, b) => a - b);
  return Math.round((1 - v[Math.floor(v.length / 2)]) * 100);
}
