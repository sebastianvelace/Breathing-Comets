export type Mode = "epoch" | "blink" | "diff" | "sum" | "rgb" | "cube";
export type View = {
  target: string;
  ra: number;
  dec: number;
  fov: number;
  det: number;
  ch?: number;
  t?: number;
  a?: number;
  b?: number;
  mode: Mode;
  layers: string[];
  stretch: string;
  lut: string;
  ui: "story" | "lab";
  lang: "en" | "es";
};
const modes: Mode[] = ["epoch", "blink", "diff", "sum", "rgb", "cube"];
export function parseView(params: { get(key: string): string | null }): View {
  const number = (key: string, fallback?: number) => {
    const value = params.get(key);
    return value !== null && value.trim() && Number.isFinite(Number(value))
      ? Number(value)
      : fallback;
  };
  return {
    target:
      params.get("target") ??
      (params.get("ra") !== null && params.get("dec") !== null
        ? ""
        : "barnard"),
    ra: ((number("ra", 0)! % 360) + 360) % 360,
    dec: Math.max(-90, Math.min(90, number("dec", 0)!)),
    fov: Math.max(0.05, Math.min(0.5, number("fov", 0.25)!)),
    det: Math.max(1, Math.min(6, Math.round(number("det",
      ["eps-indi-b", "wise-0855", "rw-aur", "r-dra"].includes(params.get("target") ?? "") ? 6 : 4)!))),
    ch: number("ch"),
    t: number("t"),
    a: number("a"),
    b: number("b"),
    mode: modes.includes(params.get("mode") as Mode)
      ? (params.get("mode") as Mode)
      : "epoch",
    layers: (params.get("layers") ?? "gaia").split(",").filter(Boolean),
    stretch: params.get("stretch") ?? "asinh:0.5:99.5",
    lut: params.get("lut") ?? "plate",
    ui: params.get("ui") === "lab" ? "lab" : "story",
    lang: params.get("lang") === "es" ? "es" : "en",
  };
}
export function serializeView(view: View): URLSearchParams {
  const p = new URLSearchParams();
  p.set("target", view.target);
  p.set("ra", view.ra.toFixed(6));
  p.set("dec", view.dec.toFixed(6));
  p.set("fov", String(view.fov));
  p.set("det", String(view.det));
  for (const key of ["ch", "t", "a", "b"] as const)
    if (view[key] !== undefined) p.set(key, view[key]!.toFixed(3));
  p.set("mode", view.mode);
  p.set("layers", view.layers.join(","));
  p.set("stretch", view.stretch);
  p.set("lut", view.lut);
  p.set("ui", view.ui);
  p.set("lang", view.lang);
  return p;
}
export function nearestFrame(times: number[], mjd?: number) {
  return mjd === undefined
    ? 0
    : times.reduce(
        (best, time, i) =>
          Math.abs(time - mjd) < Math.abs(times[best] - mjd) ? i : best,
        0,
      );
}
