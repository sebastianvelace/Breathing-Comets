import { expose, transfer } from 'comlink';
import { parseSpxf, decodedSpxfStream } from '../data/spxf.js';
import type { Header, Frame } from '../data/types.js';

export type StackService = { load: typeof load };
async function load(url: string, headerReady: (header: Header) => void, frameReady: (frame: Frame, i: number) => void) {
  const response = await fetch(url);
  if (!response.ok || !response.body) throw new Error(`SPXF HTTP ${response.status}`);
  const reader = (await decodedSpxfStream(response)).getReader();
  let pending = new Uint8Array(0), prefix: Uint8Array | undefined, header: Header | undefined, frameSize = 0, i = 0;
  for (;;) {
    const result = await reader.read();
    if (result.done) break;
    const joined = new Uint8Array(pending.length + result.value.length); joined.set(pending); joined.set(result.value, pending.length); pending = joined;
    if (!header && pending.length >= 16) {
      const dv = new DataView(pending.buffer); const length = dv.getUint32(8, true);
      if (length > 4_000_000) throw new Error('Invalid SPXF header length');
      if (pending.length < 16 + length) continue;
      if (dv.getUint16(4, true) !== 1 || String.fromCharCode(...pending.slice(0, 4)) !== 'SPXF') throw new Error('Unsupported SPXF');
      prefix = pending.slice(0, 16); header = JSON.parse(new TextDecoder().decode(pending.slice(16, 16 + length))) as Header;
      const pixels = header.grid.nx * header.grid.ny, pad = (n: number) => Math.ceil(n / 8) * 8;
      frameSize = pad(pixels * 4) * (header.has_var ? 2 : 1) + pad(pixels * 2);
      pending = pending.slice(16 + length); await headerReady(header);
    }
    while (header && prefix && pending.length >= frameSize && i < header.frames.length) {
      // Reuse the exact reference parser for each streamed frame.
      const single = new TextEncoder().encode(JSON.stringify({ ...header, frames: [header.frames[i]] }));
      const n = Math.ceil(single.length / 8) * 8, packet = new Uint8Array(16 + n + frameSize); packet.set(prefix);
      new DataView(packet.buffer).setUint32(8, n, true); packet.fill(32, 16, 16 + n); packet.set(single, 16); packet.set(pending.subarray(0, frameSize), 16 + n);
      const frame = parseSpxf(packet.buffer).frames[0];
      await frameReady(transfer(frame, [frame.flux.buffer, frame.flags.buffer, ...(frame.var ? [frame.var.buffer] : [])]), i++);
      pending = pending.slice(frameSize);
    }
  }
  if (!header || i !== header.frames.length || pending.length) throw new Error('Truncated SPXF stack');
  return i;
}
expose({ load });
