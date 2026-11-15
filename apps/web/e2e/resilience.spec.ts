import {test, expect, devices} from '@playwright/test';

test('all prepared targets and the 3I landing remain available when the live API fails', async ({page}) => {
  await page.route('https://api.breathingcomets.org/**', route => route.abort());
  for (const slug of ['barnard','eps-indi-b','wise-0855','rw-aur','r-dra']) {
    await page.goto(`/explore?target=${slug}&ui=story`);
    await expect(page.getByTestId('timeline')).toHaveAttribute('data-frame-count', '24');
    await expect(page.locator('canvas').first()).toBeVisible();
    await page.getByText('Diff λ', {exact: true}).click();
    await expect(page).toHaveURL(/mode=diff/);
    await expect(page.locator('[data-stack-kind="diff"] canvas')).toBeVisible();
  }
  await page.goto('/');
  await expect(page.getByTestId('hero-plate')).toHaveAttribute('data-frames', '12');
  const image = page.getByTestId('hero-plate').locator('img').first();
  await expect(image).toHaveAttribute('src', /\/media\/landing\/3i-d5-/);
  await expect.poll(() => image.evaluate((img: HTMLImageElement) => img.complete && img.naturalWidth > 0)).toBe(true);
});

test('iPhone playback, comparison and sharing fit the viewport', async ({browser, baseURL}) => {
  const {defaultBrowserType, ...iphone} = devices['iPhone 15'];
  const context = await browser.newContext({...iphone, baseURL});
  const page = await context.newPage();
  await page.goto('/explore?target=barnard&ui=story');
  await expect(page.getByTestId('timeline')).toHaveAttribute('data-frame-count', '24');
  const timeline = page.getByRole('slider', {name: 'Observation timeline'});
  const before = await timeline.inputValue();
  await page.getByTestId('timeline').getByRole('button', {name: 'Play', exact: true}).click();
  await expect.poll(() => timeline.inputValue()).not.toBe(before);
  await page.getByTestId('timeline').getByRole('button', {name: 'Pause', exact: true}).click();
  await page.getByText('Blink', {exact: true}).click();
  await expect(page).toHaveURL(/mode=blink/);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  const url = page.url();
  const restored = await context.newPage();
  await restored.goto(url);
  await expect(restored.getByText('Blink', {exact: true})).toHaveAttribute('data-state','on');
  await context.close();
});
