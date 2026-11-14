import { test, expect } from "@playwright/test";

const URL = "/explore?target=barnard&ui=story";

test("tour is offered, not forced: no overlay on a normal visit", async ({ page }) => {
  await page.goto(URL);
  await expect(page.getByTestId("timeline")).toBeVisible();
  await expect(page.getByTestId("tour")).toHaveCount(0);
  await expect(page.getByTestId("tour-open")).toBeVisible();
});

test("guided tour dims the page, walks six steps and closes with the keyboard", async ({ page }) => {
  await page.goto(`${URL}&tour=1`);
  const tour = page.getByTestId("tour");
  await expect(tour).toBeVisible();
  const dialog = page.getByRole("dialog", { name: "Guided tour of the explorer" });
  await expect(dialog).toBeVisible();
  const title = page.getByTestId("tour-title");
  await expect(title).toHaveText("Start with a target");
  await expect(dialog).toContainText("1 of 6");

  // Everything outside the spotlight is covered by a dark shadow of the highlighted box.
  const shadow = await page.locator(".spot").evaluate((el) => getComputedStyle(el).boxShadow);
  expect(shadow).toContain("rgba(8, 8, 7, 0.74)");

  const expected = [
    "Three ways to look",
    "A real SPHEREx plate",
    "Move through time and color",
    "Read the field notes",
    "Story, Lab and sharing",
  ];
  for (const text of expected) {
    await page.keyboard.press("ArrowRight");
    await expect(title).toHaveText(text);
  }
  await page.keyboard.press("ArrowLeft");
  await expect(title).toHaveText("Read the field notes");
  await page.keyboard.press("ArrowRight");
  await page.getByRole("button", { name: "Done" }).click();
  await expect(tour).toHaveCount(0);
});

test("Escape closes the tour, focus returns, and the page was not operated", async ({ page }) => {
  await page.goto(URL);
  await expect(page.getByTestId("timeline")).toBeVisible();
  const open = page.getByTestId("tour-open");
  await open.focus();
  await open.click();
  await expect(page.getByTestId("tour")).toBeVisible();
  // The dimmed page must not react to clicks (the catcher absorbs them).
  await page.mouse.click(700, 500);
  await expect(page.getByTestId("tour")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByTestId("tour")).toHaveCount(0);
  await expect(open).toBeFocused();
});

test("first-visit nudge appears once and is remembered", async ({ page }) => {
  await page.goto(URL);
  const nudge = page.getByRole("complementary", { name: "New here?" });
  await expect(nudge).toBeVisible({ timeout: 8000 });
  await nudge.getByRole("button", { name: "Not now" }).click();
  await expect(nudge).toHaveCount(0);
  await page.reload();
  await page.waitForTimeout(3200);
  await expect(page.getByRole("complementary", { name: "New here?" })).toHaveCount(0);
});

test("tour works in Spanish and on a phone", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto(`/es${URL}&tour=1`);
  await expect(page.getByTestId("tour-title")).toHaveText("Empieza por un objetivo");
  await expect(page.getByRole("dialog")).toContainText("1 de");
  const { sw, cw } = await page.evaluate(() => ({
    sw: document.documentElement.scrollWidth,
    cw: document.documentElement.clientWidth,
  }));
  expect(sw).toBeLessThanOrEqual(cw);
  await page.keyboard.press("Escape");
  await expect(page.getByTestId("tour")).toHaveCount(0);
});
