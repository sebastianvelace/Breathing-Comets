import catalog from '../../../static/data/neo/index.json';
export type NeoObject = (typeof catalog.objects)[number];
export type ValidationDiameter = {key: string; neowise_km: number; spherex_km: number; ratio: number};
export const neo = catalog;
export const neoObjects = catalog.objects.filter(o => ['A', 'B', 'provisional'].includes(o.tier));
