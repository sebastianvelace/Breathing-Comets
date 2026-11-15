import {test, expect} from '@playwright/test';

test('language switch translates the catalog without a manual reload', async ({page}) => {
  await page.goto('/neo');
  await expect(page.getByLabel('Filter designation')).toBeEnabled();
  await page.getByRole('link', {name:'ES',exact:true}).click();
  await expect(page.locator('html')).toHaveAttribute('lang','es');
  await expect(page.getByRole('heading',{level:1})).toHaveText('Laboratorio de cuerpos menores');
  await page.getByRole('link',{name:'EN',exact:true}).click();
  await expect(page.getByRole('heading',{level:1})).toHaveText('Small-Body Lab');
});

test('language switch preserves the current target, observation and comparison', async ({page}) => {
  await page.goto('/explore?target=barnard');
  await expect(page.getByTestId('share-view')).toBeEnabled();
  await page.getByRole('button',{name:'WISE 0855−0714',exact:true}).click();
  await expect(page.getByTestId('share-view')).toBeEnabled();
  await page.getByRole('slider',{name:'Observation timeline'}).press('End');
  await page.getByRole('radio',{name:'Blink',exact:true}).click();
  await expect(page).toHaveURL(/mode=blink/);
  const before = new URL(page.url());
  await page.getByRole('link',{name:'ES · Language',exact:true}).click();
  await expect(page.getByTestId('share-view')).toBeEnabled();
  await expect(page.getByRole('radio',{name:'Parpadeo',exact:true})).toHaveAttribute('data-state','on');
  const after = new URL(page.url());
  for (const key of ['target','ra','dec','fov','det','t','a','b','mode','layers','stretch','lut','ui'])
    expect(after.searchParams.get(key),key).toBe(before.searchParams.get(key));
  expect(after.searchParams.get('lang')).toBe('es');
  await page.reload();
  await expect(page.getByTestId('share-view')).toBeEnabled();
  await expect(page.getByRole('button',{name:'WISE 0855−0714',exact:true})).toHaveAttribute('aria-pressed','true');
  await expect(page.getByRole('radio',{name:'Parpadeo',exact:true})).toHaveAttribute('data-state','on');
});

test('sharing cannot copy the previous target while the new data are pending', async ({page,context}) => {
  await context.grantPermissions(['clipboard-read','clipboard-write']);
  let release!: () => void;
  const gate = new Promise<void>(resolve => {release=resolve;});
  await page.route('**/data/targets/wise-0855/manifest.json',async route => {await gate; await route.continue();});
  await page.goto('/explore?target=barnard');
  const share = page.getByTestId('share-view');
  await expect(share).toBeEnabled();
  await page.getByRole('button',{name:'WISE 0855−0714',exact:true}).click();
  await expect(share).toBeDisabled();
  release();
  await expect(share).toBeEnabled();
  await share.click();
  const copied = await page.evaluate(() => navigator.clipboard.readText());
  expect(new URL(copied).searchParams.get('target')).toBe('wise-0855');
  expect(new URL(copied).searchParams.get('det')).toBe('6');
});

test('a delayed name lookup cannot replace a target selected afterwards', async ({page}) => {
  let release!: () => void;
  const gate = new Promise<void>(resolve => {release=resolve;});
  await page.route('**/v1/resolve?*',async route => {
    await gate;
    await route.fulfill({json:{name:'M 31',kind:'fixed',ra:10.684708,dec:41.268750}}).catch(()=>{});
  });
  await page.goto('/explore?target=barnard');
  await expect(page.getByTestId('share-view')).toBeEnabled();
  await page.getByRole('combobox',{name:'Search the sky — a star, a comet, or coordinates'}).fill('M31');
  await page.getByRole('button',{name:'Go',exact:true}).click();
  await expect(page.getByText('Resolving sky position…')).toBeVisible();
  await page.getByRole('button',{name:'WISE 0855−0714',exact:true}).click();
  release();
  await expect(page.getByTestId('share-view')).toBeEnabled();
  await expect(page).toHaveURL(/target=wise-0855/);
  await expect(page.getByRole('button',{name:'WISE 0855−0714',exact:true})).toHaveAttribute('aria-pressed','true');
});
