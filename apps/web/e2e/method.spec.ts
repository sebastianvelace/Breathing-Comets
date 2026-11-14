import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";

const build = JSON.parse(readFileSync("static/data/build.json", "utf8"));
const calibration = JSON.parse(readFileSync("static/data/calibration.json", "utf8"));
const group = (n: number) => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, " ");

test("method page renders all ten sections with data-driven tables", async ({ page }) => {
  await page.goto("/method");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Method");
  await expect(page.locator("main section")).toHaveCount(10);
  await expect(page.getByTestId("method-detectors").locator("tbody tr")).toHaveCount(6);
  await expect(page.getByTestId("method-shift")).toContainText("+6.3");
  await expect(page.getByTestId("method-photometry").locator("tbody tr")).toHaveCount(calibration.validation.length);
  await expect(page.getByTestId("method-build")).toContainText(group(build.exposure_index.rows_d4_d6));
  await expect(page.getByTestId("method-build")).toContainText(build.data_version.spectral_wcs);
});

test("claims carry their caveats: status counts, NEO median by construction, pending injection", async ({ page }) => {
  await page.goto("/method");
  await expect(page.getByTestId("method-status")).toContainText("with systematics");
  await expect(page.getByTestId("method-neo")).toContainText("by construction");
  await expect(page.getByTestId("method-neo")).toContainText("1.02");
  await expect(page.getByText("Pending: a published injection", { exact: false })).toBeVisible();
  await expect(page.getByText("0 false positives out of 79", { exact: false })).toBeVisible();
});

test("table of contents jumps to its section", async ({ page }) => {
  await page.goto("/method");
  await page.getByRole("link", { name: "4. Diff λ: the same sky at the same color" }).click();
  await expect(page).toHaveURL(/#s4$/);
  await expect(page.locator("#s4")).toBeInViewport();
});

test("Spanish method keeps decimal points and has no ambiguous commas; mobile fits", async ({ page }) => {
  await page.goto("/es/method");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Método");
  const text = await page.locator("main").innerText();
  expect(text).not.toMatch(/\d,\d/);
  expect(text).toContain("+6.3");
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto("/es/method");
  const { sw, cw } = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
  expect(sw).toBeLessThanOrEqual(cw);
});

test("landing footer and atlas link to the method", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "Method and checks" }).click();
  await expect(page).toHaveURL(/\/method$/);
  await page.goto("/comets");
  await page.getByTestId("method-link").click();
  await expect(page).toHaveURL(/\/method$/);
});
