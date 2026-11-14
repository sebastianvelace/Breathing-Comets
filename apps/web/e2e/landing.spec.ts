import { test, expect, type Page } from "@playwright/test";

const SLUGS = ["barnard", "eps-indi-b", "wise-0855", "rw-aur", "r-dra"];

// Test-only contract fixture for the pending 3I packet. Images reuse existing
// landing plates purely so the browser has something to decode; values are fake.
const fixture = {
  target: "3I/ATLAS",
  plates: {
    poster: "/media/landing/barnard-d4-poster.webp",
    epochs: [
      { image: "/media/landing/barnard-d4-visit0.webp", mjd: 60900.5, lambda_um: 4.3, obs_id: "TEST_A", credit: "test" },
      { image: "/media/landing/barnard-d4-visit6.webp", mjd: 61000.5, lambda_um: 4.4, obs_id: "TEST_B", credit: "test" },
    ],
  },
  measurements: [
    { label: "Q(TEST)", value: 2.5e26, lo: 2e26, hi: 3e26, unit: "s⁻¹", caveat: "TEST CAVEAT", source: "TEST SOURCE" },
  ],
  validation: [
    { species: "TEST-IN", measured: 2, published_lo: 1, published_hi: 3, unit: "s⁻¹", caveat: "c", source: "s" },
    { species: "TEST-OUT", measured: 9, published_lo: 1, published_hi: 3, unit: "s⁻¹", caveat: "c", source: "s" },
  ],
  credits: ["TEST CREDIT"],
};

async function noHorizontalScroll(page: Page) {
  const { sw, cw } = await page.evaluate(() => ({
    sw: document.documentElement.scrollWidth,
    cw: document.documentElement.clientWidth,
  }));
  expect(sw).toBeLessThanOrEqual(cw);
}

test("hero opens the Barnard story with real frames", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("The sky is breathing.");
  const cta = page.getByRole("link", { name: "Open the sky" });
  await expect(cta).toHaveAttribute("href", "/explore?target=barnard&ui=story");
  await cta.click();
  await expect(page).toHaveURL(/\/explore\?target=barnard&ui=story$/);
  await expect
    .poll(async () => Number(await page.getByTestId("timeline").getAttribute("data-frame-count")))
    .toBeGreaterThanOrEqual(10);
});

test("all five target entries open real Explorer stacks", async ({ page }) => {
  await page.goto("/");
  for (const slug of SLUGS) {
    const link = page.locator(`[data-slug="${slug}"] a.open`);
    await expect(link).toHaveAttribute("href", `/explore?target=${slug}&ui=story`);
    await expect(page.locator(`[data-slug="${slug}"] img`)).toHaveAttribute(
      "src",
      new RegExp(`/media/landing/${slug}-d\\d-poster\\.webp$`),
    );
  }
  for (const slug of SLUGS) {
    await page.goto(`/explore?target=${slug}&ui=story`);
    await expect
      .poll(async () => Number(await page.getByTestId("timeline").getAttribute("data-frame-count")))
      .toBeGreaterThan(0);
  }
});

test("every field-note value is shown with its caveat", async ({ page }) => {
  await page.goto("/");
  for (const slug of SLUGS) {
    const card = page.locator(`[data-slug="${slug}"]`);
    expect(await card.locator("dd.value").count()).toBeGreaterThan(0);
    await expect(card.locator(".caveat")).not.toBeEmpty();
  }
});

test("internal links and anchors resolve", async ({ page, request }) => {
  await page.goto("/");
  const hrefs = await page.locator("a[href]").evaluateAll((as) =>
    as.map((a) => a.getAttribute("href")!),
  );
  for (const href of new Set(hrefs)) {
    if (href.startsWith("#")) {
      expect(await page.locator(href).count(), href).toBe(1);
    } else if (href.startsWith("/")) {
      expect((await request.get(href)).status(), href).toBe(200);
    }
  }
});

test("3I packet missing: honest pending state, Barnard stand-in labelled", async ({ page }) => {
  await page.route("**/data/comets/3i-atlas/landing.json", (route) =>
    route.fulfill({ status: 404, body: "" }),
  );
  await page.goto("/");
  await expect(page.getByTestId("comet-panel")).toHaveAttribute("data-status", "missing");
  await expect(page.getByTestId("comet-panel").locator("img")).toHaveCount(0);
  await expect(page.getByText("Stand-in plate: this is Barnard's Star, not 3I/ATLAS.", { exact: false })).toBeVisible();
  await expect(page.getByTestId("comet-validation")).toContainText("PENDING");
});

test("3I packet present: comet sections fill in automatically", async ({ page }) => {
  await page.route("**/data/comets/3i-atlas/landing.json", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(fixture) }),
  );
  await page.goto("/");
  const panel = page.getByTestId("comet-panel");
  await expect(panel).toHaveAttribute("data-status", "ready");
  await expect(panel).toContainText("2.50 × 10²⁶");
  await expect(panel).toContainText("TEST CAVEAT");
  const table = page.getByTestId("comet-validation");
  await expect(table.getByRole("row", { name: /TEST-IN/ })).toContainText("within range");
  await expect(table.getByRole("row", { name: /TEST-OUT/ })).toContainText("outside range");
  await expect(page.getByTestId("hero-plate").locator("img").first()).toHaveAttribute(
    "alt",
    "SPHEREx plate of interstellar comet 3I/ATLAS",
  );
});

test("hero loop plays, pauses, and respects reduced motion", async ({ page, browser }) => {
  await page.goto("/");
  const plate = page.getByTestId("hero-plate");
  const pause = page.getByRole("button", { name: "Pause" });
  await expect(pause).toBeVisible({ timeout: 10000 });
  await expect.poll(() => plate.getAttribute("data-frame"), { timeout: 5000 }).not.toBe("0");
  await pause.click();
  const frozen = await plate.getAttribute("data-frame");
  await page.waitForTimeout(1500);
  expect(await plate.getAttribute("data-frame")).toBe(frozen);

  const context = await browser.newContext({ reducedMotion: "reduce" });
  const calm = await context.newPage();
  await calm.goto("/");
  await expect(calm.getByRole("button", { name: "Play" })).toBeEnabled({ timeout: 10000 });
  await calm.waitForTimeout(1500);
  await expect(calm.getByTestId("hero-plate")).toHaveAttribute("data-frame", "0");
  await context.close();
});

test("blink, Diff λ slider and spectrum bands work from the keyboard", async ({ page }) => {
  await page.goto("/");
  const blink = page.getByTestId("blink-plate");
  await blink.scrollIntoViewIfNeeded();
  await expect(blink).toHaveAttribute("data-epoch", "a");
  await page.getByRole("button", { name: /^B · 2026-09-02$/ }).focus();
  await page.keyboard.press("Enter");
  await expect(blink).toHaveAttribute("data-epoch", "b");

  const slider = page.getByRole("slider", { name: /raw subtraction/ });
  await slider.focus();
  await page.keyboard.press("Home");
  await expect(page.getByTestId("diff-compare")).toHaveAttribute("style", /--split: 0%/);

  const spectrum = page.getByTestId("landing-spectrum");
  await spectrum.scrollIntoViewIfNeeded();
  await expect.poll(async () => Number(await spectrum.getAttribute("data-points"))).toBeGreaterThan(50);
  await page.getByRole("button", { name: /CH₄/ }).focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("link", { name: "Open Epsilon Indi B in the Explorer" })).toHaveAttribute(
    "href",
    "/explore?target=eps-indi-b&ui=story",
  );
});

test("visible focus ring on the primary action", async ({ page }) => {
  await page.goto("/");
  const cta = page.getByRole("link", { name: "Open the sky" });
  await cta.focus();
  const outline = await cta.evaluate((el) => getComputedStyle(el).outlineStyle + " " + getComputedStyle(el).outlineWidth);
  expect(outline).toBe("solid 2px");
});

test("/es is Spanish with decimal points", async ({ page }) => {
  await page.goto("/es");
  await expect(page.locator("html")).toHaveAttribute("lang", "es");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("El cielo respira.");
  await expect(page.getByRole("link", { name: "Abre el cielo" })).toHaveAttribute(
    "href",
    "/es/explore?target=barnard&ui=story",
  );
  const notes = await page.locator("#targets").innerText();
  expect(notes).toContain("10.6 ± 0.4″/año");
  expect(notes).not.toMatch(/\d,\d/);
});

test.describe("mobile", () => {
  test.use({ viewport: { width: 375, height: 812 }, isMobile: true, hasTouch: true });
  test("no horizontal scroll in either language", async ({ page }) => {
    for (const path of ["/", "/es"]) {
      await page.goto(path);
      await page.locator("#targets").scrollIntoViewIfNeeded();
      await noHorizontalScroll(page);
    }
  });
});
