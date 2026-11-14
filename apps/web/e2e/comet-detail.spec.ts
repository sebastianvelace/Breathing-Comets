import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";

const read = (slug: string) => JSON.parse(readFileSync(`static/data/comets/${slug}.json`, "utf8"));

test("atlas links to both detail pages", async ({ page }) => {
  await page.goto("/comets");
  await expect(page.getByTestId("detail-link")).toHaveCount(2);
  await page.locator('[data-testid=detail-link]').first().click();
  await expect(page).toHaveURL(/\/comets\/(3i-atlas|29p-schwassmann-wachmann)$/);
});

test("29P page shows real frames ordered by wavelength and the CO/CO2 spectra", async ({ page }) => {
  const d = read("29p-schwassmann-wachmann");
  await page.goto("/comets/29p-schwassmann-wachmann");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("29P/Schwassmann-Wachmann");
  const slider = page.getByRole("slider");
  await expect(slider).toHaveAttribute("max", String(d.epochs[0].frames.length - 1));
  const frame = page.getByTestId("detail-frame");
  // The static HTML is interactive before Svelte hydrates; retry until the handler is attached.
  await expect(async () => {
    await slider.focus();
    await page.keyboard.press("Home");
    const first = Number(await frame.getAttribute("data-lam"));
    await page.keyboard.press("End");
    await expect.poll(async () => Number(await frame.getAttribute("data-lam")), { timeout: 1500 }).toBeGreaterThan(first);
  }).toPass({ timeout: 20000 });
  await expect(page.getByTestId("detail-spectrum")).toHaveAttribute("data-points", "32");
  await expect(page.getByTestId("detail-spectrum-co")).toHaveAttribute("data-points", "18");
  await expect(page.getByTestId("detail-validation")).toContainText("4.50 × 10²⁸");
  await expect(page.getByTestId("detail-status")).toHaveAttribute("data-status", "detected");
});

test("3I page: August epoch is the validated one, December carries its caveat", async ({ page }) => {
  await page.goto("/comets/3i-atlas");
  await expect(page.getByRole("button", { name: "2025-08" })).toHaveAttribute("aria-pressed", "true");
  await expect(page.getByTestId("detail-spectrum")).toHaveAttribute("data-points", "23");
  await expect(page.getByTestId("detail-validation").first()).toContainText("1.17 × 10²⁷");
  await expect(page.getByTestId("detail-status")).toHaveCount(0);
  await page.getByRole("button", { name: "2025-12" }).click();
  await expect(page.getByTestId("detail-spectrum")).toHaveAttribute("data-points", "16");
  await expect(page.getByTestId("detail-status")).toHaveAttribute("data-status", "with_systematics");
  await expect(page.getByText("fits poorly", { exact: false }).first()).toBeVisible();
});

test("sweep animation advances frames and can be paused", async ({ page }) => {
  await page.goto("/comets/29p-schwassmann-wachmann");
  const frame = page.getByTestId("detail-frame");
  const start = await frame.getAttribute("data-lam");
  await page.getByRole("button", { name: "Sweep wavelengths" }).click();
  await expect.poll(() => frame.getAttribute("data-lam"), { timeout: 15000 }).not.toBe(start);
  await page.getByRole("button", { name: "Pause" }).click();
  const frozen = await frame.getAttribute("data-lam");
  await page.waitForTimeout(1000);
  expect(await frame.getAttribute("data-lam")).toBe(frozen);
});

test("Spanish detail page keeps decimal points and fits a phone", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto("/es/comets/3i-atlas");
  await expect(page.getByText("Cuadros reales de SPHEREx", { exact: false })).toBeVisible();
  const text = await page.locator("main").innerText();
  expect(text).not.toMatch(/\d,\d/);
  const { sw, cw } = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
  expect(sw).toBeLessThanOrEqual(cw);
});
