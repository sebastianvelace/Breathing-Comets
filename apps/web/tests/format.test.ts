import { expect, it } from "vitest";
import { fmtTicks } from "../src/lib/data/format";

it("keeps one decimal when it already separates the ticks", () => {
  expect(fmtTicks([0.8, 0.9, 1.0, 1.1])).toEqual(["0.8", "0.9", "1.0", "1.1"]);
});

it("adds decimals until wavelength ticks are distinct", () => {
  expect(fmtTicks([3.9, 3.95, 4.0, 4.05, 4.1])).toEqual(["3.90", "3.95", "4.00", "4.05", "4.10"]);
  expect(fmtTicks([4.2, 4.225, 4.25])).toEqual(["4.200", "4.225", "4.250"]);
});
