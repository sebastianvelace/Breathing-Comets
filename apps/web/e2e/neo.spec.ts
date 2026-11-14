import { test, expect } from '@playwright/test';
import catalog from '../static/data/neo/index.json' with {type: 'json'};

test('every published diameter retains its interval, evidence tier and systematic floor', async ({ page }) => {
  await page.goto('/neo');
  const rows = page.getByTestId('neo-size-row');
  await expect(rows).toHaveCount(catalog.objects.length);
  for (const object of catalog.objects) {
    const row = page.locator(`[data-slug="${object.slug}"]`);
    await expect(row.getByTestId('diameter')).toContainText(`${object.D_km.toFixed(3)} km`);
    await expect(row.getByTestId('diameter')).toContainText(`±${catalog.method.floor_fraction * 100}%`);
    await expect(row.getByTestId('interval')).toHaveText(`${object.D16.toFixed(3)}–${object.D84.toFixed(3)} km`);
    await expect(row.getByTestId('tier')).toHaveText(object.tier === 'provisional' ? 'Provisional' : object.tier);
    await expect(row.getByTestId('single-visit')).toHaveCount(object.single_visit ? 1 : 0);
  }
  await page.getByRole('button', {name: '2025 YH5', exact: true}).click();
  await expect(page.getByTestId('spectrum-plot')).toHaveAttribute('data-points', /[1-9]\d*/);
  await expect(page.getByText('A single visit does not measure rotational variability.', {exact: false})).toBeVisible();
  await page.getByLabel('Filter designation').fill('2025 YH5');
  await expect(rows).toHaveCount(1);
});

test('NEO Spanish page preserves decimal points and fits a mobile viewport', async ({ page }) => {
  await page.setViewportSize({width: 390, height: 844});
  await page.goto('/es/neo');
  await expect(page.getByRole('heading', {level: 1})).toHaveText('Laboratorio de cuerpos menores');
  await expect(page.locator('[data-slug="2025-yh5"]').getByTestId('interval')).toHaveText('0.610–1.363 km');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});
