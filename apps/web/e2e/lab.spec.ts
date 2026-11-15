import { test, expect } from '@playwright/test';
import channelData from '../static/data/channels.json' with {type: 'json'};
const channels = channelData.channels;

test('Lab requests the real DR1 HiPS frame 85 and preserves Aladin attribution', async ({page}) => {
  test.setTimeout(120000);
  const tiles: string[] = [];
  page.on('request', r => {if (/_85\.png(?:\?|$)/.test(r.url())) tiles.push(r.url());});
  await page.goto('/explore?target=barnard&ui=lab');
  const iframe = page.frameLocator('[data-testid="aladin-frame"]');
  await expect(iframe.getByTestId('aladin-sky')).toHaveAttribute('data-ready', 'true', {timeout: 60000});
  await page.getByRole('spinbutton', {name: 'HiPS frame'}).fill('85');
  await page.getByRole('spinbutton', {name: 'HiPS frame'}).press('Tab');
  await expect(page.getByTestId('hips-channel-label')).toContainText(`D${channels[85].detector} · ${channels[85].wavelength_um.toFixed(3)} µm`);
  await expect.poll(() => tiles.length, {timeout: 45000}).toBeGreaterThan(0);
  await expect(iframe.locator('a[href="https://aladin.cds.unistra.fr/"]')).toBeVisible();
  await page.getByRole('button', {name: 'Story', exact: true}).click();
  await expect(page.getByTestId('aladin-frame')).toHaveCount(0);
  await expect(page.getByRole('radio',{name:'Epoch',exact:true})).toHaveAttribute('data-state','on');
});

test('a real Lab pixel streams at least fifty measured spectrum points', async ({page}) => {
  test.setTimeout(120000);
  await page.goto('/explore?ra=150.609552&dec=2.116248&det=4&fov=0.05&ui=lab');
  const canvas = page.locator('canvas').first();
  await expect(canvas).toBeVisible({timeout: 60000});
  const box = await canvas.boundingBox();
  await canvas.click({position: {x: box!.width / 2, y: box!.height / 2}});
  await expect.poll(async () => Number(await page.getByTestId('spectrum-plot').getAttribute('data-points')), {timeout: 90000}).toBeGreaterThanOrEqual(50);
});
