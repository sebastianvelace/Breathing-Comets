import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";

const atlas = JSON.parse(readFileSync("static/data/comets/index.json", "utf8"));

test("every census comet is plotted and tabulated with its status", async ({ page }) => {
  await page.goto("/comets");
  await expect(page.getByTestId("comet-plot")).toHaveAttribute("data-points", String(atlas.comets.length));
  await expect(page.getByTestId("comet-row")).toHaveCount(atlas.comets.length);
  for (const slug of ["3i-atlas", "c-2025-a6-lemmon"]) {
    await expect(page.locator(`[data-testid=comet-row][data-slug="${slug}"]`)).toHaveAttribute("data-status", "with_systematics");
  }
  await expect(page.getByTestId("comet-counts")).toContainText(
    `${atlas.counts.comets} comets · ${atlas.counts.detected} detected · ${atlas.counts.with_systematics} with systematics`,
  );
});

test("honesty notes and the far-comet flag are visible", async ({ page }) => {
  await page.goto("/comets");
  await expect(page.getByText("census by pass, not a real-time monitor", { exact: false })).toBeVisible();
  await expect(page.getByTestId("velocity-note")).toContainText("about 40%");
  const far = page.locator('[data-testid=comet-row][data-slug="c-2014-un271-bernardinelli-bernstein"]');
  await expect(far).toContainText("Far: unreliable");
});

test("selecting a point from the keyboard shows the numbers and diagnostics", async ({ page }) => {
  await page.goto("/comets");
  await page.waitForLoadState("networkidle"); // Enter toggles the selection, so it must not be retried
  const point = page.locator('g[data-slug="c-2022-n2-panstarrs"]');
  await point.focus();
  await page.keyboard.press("Enter");
  const row = atlas.comets.find((c: { slug: string }) => c.slug === "c-2022-n2-panstarrs");
  await expect(page.getByText("C/2022 N2 (PANSTARRS) · r_h 3.83 au")).toBeVisible();
  await expect(page.getByText(`S/N ${row.co2.snr_det.toFixed(1)}`, { exact: false })).toBeVisible();
  await expect(page.locator('[data-testid=comet-row][data-slug="c-2022-n2-panstarrs"]')).toHaveClass(/chosen/);
});

test("status filter narrows table and plot", async ({ page }) => {
  await page.goto("/comets");
  await page.waitForLoadState("networkidle");
  await page.getByLabel("Status").selectOption("with_systematics");
  await expect(page.getByTestId("comet-row")).toHaveCount(atlas.counts.with_systematics);
  await expect(page.getByTestId("comet-plot")).toHaveAttribute("data-points", String(atlas.counts.with_systematics));
});

test("validation compares measured and published values and keeps H2O pending", async ({ page }) => {
  await page.goto("/comets");
  const table = page.getByTestId("comet-validation");
  await expect(table.getByTestId("check")).toHaveCount(2);
  await expect(table.getByTestId("check").first()).toContainText("inside the published range");
  await expect(table).toContainText("1.17 × 10²⁷ s⁻¹");
  await expect(table).toContainText("arXiv:2508.15469");
  await expect(page.getByTestId("comet-pending")).toContainText("H₂O");
});

test("Spanish atlas keeps decimal points; mobile does not scroll sideways", async ({ page }) => {
  await page.goto("/es/comets");
  await expect(page.locator("h1")).toHaveText("Atlas de cometas");
  const text = await page.locator("main").innerText();
  expect(text).toContain("1.17 × 10²⁷");
  expect(text).not.toMatch(/\d,\d/);
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto("/es/comets");
  const { sw, cw } = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
  expect(sw).toBeLessThanOrEqual(cw);
});

test("landing leads to the atlas", async ({ page }) => {
  await page.goto("/");
  await page.getByTestId("meet-comets").click();
  await expect(page).toHaveURL(/\/comets$/);
});
