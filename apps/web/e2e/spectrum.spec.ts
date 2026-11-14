import { test, expect } from "@playwright/test";

test("a real sky click streams at least fifty forced-ePSF points", async ({
  page,
}) => {
  test.setTimeout(120000);
  await page.goto("/explore?ra=150.609552&dec=2.116248&det=4&fov=0.05");
  const canvas = page.locator("canvas").first();
  await expect(canvas).toBeVisible({ timeout: 60000 });
  const box = await canvas.boundingBox();
  expect(box).not.toBeNull();
  await canvas.click({ position: { x: box!.width / 2, y: box!.height / 2 } });
  await expect(
    page.getByRole("heading", { name: "Selected position spectrum" }),
  ).toBeVisible();
  await expect
    .poll(
      async () =>
        Number(
          await page.getByTestId("spectrum-plot").getAttribute("data-points"),
        ),
      { timeout: 90000 },
    )
    .toBeGreaterThanOrEqual(50);
});
