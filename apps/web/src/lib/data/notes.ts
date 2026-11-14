import * as messages from '#lib/paraglide/messages.js';
export function noteText(slug: string, key: string, source: string): string {
  const values: Record<string, string> = {};
  [...source.matchAll(/\d+(?:\.\d+)?/g)].forEach((match, i) => values[`v${i}`] = match[0]);
  const translate = (messages as unknown as Record<string, (values: Record<string, string>) => string>)[`note_${slug.replaceAll('-', '_')}_${key}`];
  return translate ? translate(values) : source;
}
