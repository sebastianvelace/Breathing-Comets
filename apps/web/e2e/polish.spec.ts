import { test, expect } from "@playwright/test";

test("searching a comet explains why it moves and links to its tracked page", async ({ page }) => {
  await page.goto("/explore?target=barnard&ui=story");
  const search = page.getByPlaceholder(/Search the sky/);
  await expect(search).toBeEnabled();
  await search.fill("29P");
  await search.press("Enter");
  const link = page.getByTestId("moving-link");
  await expect(link).toBeVisible({ timeout: 30000 });
  await expect(link).toHaveAttribute("href", "/comets/29p-schwassmann-wachmann");
  await expect(page.getByRole("status").first()).toContainText("moves across the sky");
  await link.click();
  await expect(page).toHaveURL(/\/comets\/29p-schwassmann-wachmann$/);
});

test("3I/ATLAS resolves through its C/2025 N1 designation to the detail page, also in Spanish", async ({ page }) => {
  await page.goto("/es/explore?target=barnard&ui=story");
  const search = page.locator("#sky-search");
  await expect(search).toBeEnabled();
  await search.fill("C/2025 N1");
  await search.press("Enter");
  await expect(page.getByTestId("moving-link")).toHaveAttribute("href", "/es/comets/3i-atlas", { timeout: 30000 });
});

test("a target caveat is shown once, beside the measurement it qualifies", async ({ page }) => {
  await page.goto("/explore?target=eps-indi-b&ui=story");
  const caveats = page.getByTestId("field-caveat");
  await expect(caveats).toHaveCount(1);
  await expect(caveats).toContainText("277–294 mas");
  const card = page.locator(".field-notes .notes section", { has: caveats });
  await expect(card).toContainText("Parallax");
  await page.goto("/explore?target=wise-0855&ui=story");
  await expect(page.getByTestId("field-caveat")).toHaveCount(1);
  await expect(page.locator(".field-notes").getByText(/14% of the W2 response/)).toHaveCount(1);
});

test("clicking the sky in Story brings the measured spectrum into view", async ({ page }) => {
  await page.setViewportSize({ width: 1366, height: 860 });
  await page.goto("/explore?target=wise-0855&ui=story");
  await expect
    .poll(async () => Number(await page.getByTestId("timeline").getAttribute("data-frame-count")))
    .toBeGreaterThan(0);
  const canvas = page.locator("canvas").first();
  const box = (await canvas.boundingBox())!;
  await page.mouse.click(box.x + box.width * 0.3, box.y + box.height * 0.4);
  const spectrum = page.getByTestId("story-spectrum");
  await expect(spectrum).toBeInViewport({ timeout: 10000 });
});

test("an unknown address returns a real 404 page", async ({ request }) => {
  test.skip(!process.env.PLAYWRIGHT_BASE_URL, "Cloudflare Pages serves 404.html; the local preview server does not");
  const response = await request.get("/this-part-of-the-sky-is-empty");
  expect(response.status()).toBe(404);
  expect(await response.text()).toContain("This part of the sky is empty.");
});
