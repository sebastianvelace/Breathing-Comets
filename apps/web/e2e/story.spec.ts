import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
test('landing opens real Barnard frames and Gaia moves by epoch',async({page})=>{
  await page.goto('/');await page.getByRole('link',{name:'Open the sky'}).click();
  const timeline=page.getByTestId('timeline');await expect(timeline).toHaveAttribute('data-frame-count','24');
  const cross=page.getByTestId('gaia-cross');const x0=Number(await cross.getAttribute('data-x')),y0=Number(await cross.getAttribute('data-y'));
  await page.getByRole('slider',{name:'Observation timeline'}).press('End');
  await expect.poll(async()=>Number(await cross.getAttribute('data-y'))).not.toBe(y0);
  expect(Math.hypot(Number(await cross.getAttribute('data-x'))-x0,Number(await cross.getAttribute('data-y'))-y0)).toBeGreaterThan(1);
});
test('WISE reference spectrum is deblended and independent of clicked pixels',async({page})=>{
  await page.goto('/explore?target=wise-0855');await expect(page.getByTestId('timeline')).toHaveAttribute('data-frame-count','24');
  await expect(page.getByTestId('spectrum-plot')).toHaveAttribute('data-points',/^[5-9]\d$/);
  const data=JSON.parse(readFileSync('static/data/targets/wise-0855.json','utf8'));
  const red=data.spectrum.filter((p:{lam:number})=>p.lam>=4.2&&p.lam<=4.7);
  // The supplied deblended spectrum is checked directly; the neighboring star is real.
  expect(red.every((p:{f:number,e:number})=>p.f/p.e>5)).toBe(true);
  expect(red.reduce((a:number,p:{f:number,e:number})=>a+p.f,0)/Math.sqrt(red.reduce((a:number,p:{e:number})=>a+p.e*p.e,0))).toBeGreaterThan(10);
  expect(data.spectrum.filter((p:{lam:number})=>p.lam<3).every((p:{f:number})=>Math.abs(p.f)<.1)).toBe(true);
  await expect(page.getByText('Precomputed, deblended target spectrum; not a measurement of the selected pixel.')).toBeVisible();
});
test('shared URL restores the same observation in a fresh context',async({page,browser})=>{
  await page.goto('/explore?target=barnard');await expect(page.getByTestId('timeline')).toHaveAttribute('data-frame-count','24');
  await page.getByRole('slider',{name:'Observation timeline'}).press('Home');for(let i=0;i<12;i++)await page.getByRole('slider',{name:'Observation timeline'}).press('ArrowRight');await page.getByText('Blink',{exact:true}).click();
  await expect.poll(()=>new URL(page.url()).searchParams.get('mode')).toBe('blink');
  const url=page.url(),metadata=await page.getByTestId('frame-metadata').innerText();const context=await browser.newContext();const second=await context.newPage();await second.goto(url);await expect(second.getByTestId('timeline')).toHaveAttribute('data-frame-count','24');await expect(second.getByTestId('frame-metadata')).toHaveText(metadata,{useInnerText:true});expect(new URL(second.url()).search).toBe(new URL(url).search);await context.close();
});
