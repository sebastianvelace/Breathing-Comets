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

for (const width of [390, 1024, 1280, 1440]) {
  test(`Lab controls stay usable with the layers expanded at ${width}px`, async ({page}) => {
    await page.setViewportSize({width,height:900});
    await page.addInitScript(() => localStorage.setItem('bc.tour.v1','dismissed'));
    await page.goto('/explore?target=barnard&ui=lab');
    await expect(page.getByTestId('share-view')).toBeEnabled();
    await expect(page.getByRole('button',{name:'Lab',exact:true})).toHaveAttribute('aria-pressed','true');
    await page.locator('.lab-layers > summary').click();
    await expect(page.getByLabel('Pixel grid',{exact:true})).toBeVisible();
    const play = page.getByTestId('timeline').getByRole('button',{name:'Play',exact:true});
    await play.scrollIntoViewIfNeeded();
    expect(await play.evaluate(el => {
      const r=el.getBoundingClientRect();
      const hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);
      return hit===el || !!hit && el.contains(hit);
    })).toBe(true);
    const slider=page.getByRole('slider',{name:'Observation timeline'});
    const initial=await slider.inputValue();
    await play.click();
    await expect.poll(()=>slider.inputValue()).not.toBe(initial);
    await page.getByTestId('timeline').getByRole('button',{name:'Pause',exact:true}).click();
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth)).toBe(true);
  });
}

test('mobile navigation connects the three workspaces and exposes a guided comparison', async ({page}) => {
  await page.setViewportSize({width:375,height:812});
  await page.goto('/');
  const nav=page.getByTestId('product-nav');
  await expect(nav.getByRole('link',{name:'Asteroids',exact:true})).toBeVisible();
  await nav.getByRole('link',{name:'Asteroids',exact:true}).click();
  await expect(page.getByRole('heading',{level:1})).toHaveText('Small-Body Lab');
  await nav.getByRole('link',{name:'Comets',exact:true}).click();
  await expect(page.getByRole('heading',{level:1})).toHaveText('Comet atlas');
  await nav.getByRole('link',{name:'Explore',exact:true}).click();
  await expect(page.getByTestId('share-view')).toBeEnabled();
  await expect(page.getByTestId('observation-guide')).toContainText('Find the moving star');
  await page.getByTestId('observation-guide').locator('summary').click();
  await page.getByRole('button',{name:'Start a visit comparison'}).click();
  await expect(page.getByRole('radio',{name:'Blink',exact:true})).toHaveAttribute('data-state','on');
  const first=await page.getByRole('combobox',{name:'Date A',exact:true}).locator('option:checked').innerText();
  const last=await page.getByRole('combobox',{name:'Date B',exact:true}).locator('option:checked').innerText();
  expect(first.slice(0,10)).not.toBe(last.slice(0,10));
  expect(Math.abs(Number(first.split(' · ')[1].split(' ')[0])-Number(last.split(' · ')[1].split(' ')[0]))).toBeLessThan(0.1);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth)).toBe(true);
});

test('a selected asteroid exposes its size and interval beside the catalog', async ({page}) => {
  await page.goto('/neo');
  await expect(page.getByLabel('Filter designation')).toBeEnabled();
  await page.getByLabel('Filter designation').fill('2025 YH5');
  await page.getByRole('button',{name:'2025 YH5',exact:true}).click();
  const detail=page.locator('#neo-inspection');
  await expect(detail.getByText('0.949 km',{exact:true})).toBeVisible();
  await expect(detail).toContainText('0.610–1.363 km');
  await expect(detail).toContainText('A single visit does not measure rotational variability.');
  await expect(detail.getByTestId('spectrum-plot')).toHaveAttribute('data-points',/[1-9]\d*/);
});

for (const locale of ['en','es']) {
  test(`first-visit invitation leaves the mobile image controls reachable in ${locale}`, async ({page}) => {
    await page.setViewportSize({width:375,height:812});
    await page.goto(`${locale==='es'?'/es':''}/explore?target=barnard`);
    await expect(page.getByRole('button',{name:locale==='es'?'Empezar recorrido':'Start tour',exact:true})).toBeVisible({timeout:10000});
    const reset=page.getByRole('button',{name:locale==='es'?'Restablecer vista':'Reset view',exact:true});
    await reset.scrollIntoViewIfNeeded();
    expect(await reset.evaluate(el=>{
      const r=el.getBoundingClientRect(),hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);
      return hit===el || !!hit && el.contains(hit);
    })).toBe(true);
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth)).toBe(true);
  });
}
