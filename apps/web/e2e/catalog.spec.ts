import {test, expect} from '@playwright/test';
import {readFileSync} from 'node:fs';

test('a free-field Gaia counterpart survives a detector change without requerying the catalog', async ({page}) => {
  // Reuse real packaged observations as transport fixtures, without remote queries.
  let catalogs=0;
  await page.route('**/v1/gaia?*',route=> {
    catalogs++;
    return route.fulfill({contentType:'application/json',body:readFileSync(new URL('../static/data/targets/barnard/gaia.json',import.meta.url))});
  });
  await page.route('**/v1/stack?*',route=> {
    const det=new URL(route.request().url()).searchParams.get('det');
    return route.fulfill({contentType:'application/octet-stream',body:readFileSync(new URL(`../static/data/targets/barnard/D${det}.spxf.gz`,import.meta.url))});
  });
  await page.goto('/explore?ra=269.446268&dec=4.768204&fov=.25&det=4');
  await expect(page.getByTestId('share-view')).toBeEnabled();
  await expect(page.getByTestId('gaia-cross')).toBeVisible();
  await page.getByLabel('Detector',{exact:true}).selectOption('6');
  await expect(page.getByTestId('share-view')).toBeEnabled();
  await expect(page.getByTestId('gaia-cross')).toBeVisible();
  expect(catalogs).toBe(1);
});
