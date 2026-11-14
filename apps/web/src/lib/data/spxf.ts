export type SpxfFrame = {
  flux: Float32Array;
  var?: Float32Array;
  flags: Uint16Array;
};
export type Spxf = { header: any; frames: SpxfFrame[] };

export async function fetchSpxf(
  url: string,
  gz: boolean,
  signal?: AbortSignal,
): Promise<Spxf> {
  const res = await fetch(url, { signal });
  if (!res.ok) throw new Error(`SPXF ${res.status} ${url}`);
  const stream = gz ? await decodedSpxfStream(res) : res.body!;
  return parseSpxf(await new Response(stream).arrayBuffer());
}

/** Browsers may already decode an HTTP Content-Encoding: gzip response. */
export async function decodedSpxfStream(
  response: Response,
): Promise<ReadableStream<Uint8Array<ArrayBuffer>>> {
  if (!response.body) throw new Error("Empty SPXF response");
  const reader = response.body.getReader();
  let first = new Uint8Array(0);
  while (first.length < 2) {
    const result = await reader.read();
    if (result.done) throw new Error("Truncated SPXF response");
    const joined = new Uint8Array(first.length + result.value.length);
    joined.set(first);
    joined.set(result.value, first.length);
    first = joined;
  }
  const stream = new ReadableStream<Uint8Array<ArrayBuffer>>({
    start(controller) {
      controller.enqueue(first);
    },
    async pull(controller) {
      const result = await reader.read();
      if (result.done) controller.close();
      else controller.enqueue(result.value);
    },
    cancel(reason) {
      return reader.cancel(reason);
    },
  });
  return first[0] === 0x1f && first[1] === 0x8b
    ? stream.pipeThrough(new DecompressionStream("gzip"))
    : stream;
}

export function parseSpxf(buf: ArrayBuffer): Spxf {
  const dv = new DataView(buf);
  if (String.fromCharCode(...new Uint8Array(buf, 0, 4)) !== "SPXF")
    throw new Error("bad magic");
  const flags = dv.getUint16(6, true),
    n = dv.getUint32(8, true);
  const header = JSON.parse(
    new TextDecoder().decode(new Uint8Array(buf, 16, n)),
  );
  const { nx, ny } = header.grid,
    px = nx * ny,
    pad8 = (b: number) => b + ((8 - (b % 8)) % 8);
  let off = 16 + n;
  const readF32 = () => {
    const bytes = new Uint8Array(buf, off, px * 4);
    off += pad8(px * 4);
    if (!(flags & 1)) return new Float32Array(bytes.slice().buffer);
    const out = new Uint8Array(px * 4);
    for (let i = 0; i < px; i++)
      for (let b = 0; b < 4; b++) out[i * 4 + b] = bytes[b * px + i];
    return new Float32Array(out.buffer);
  };
  const frames: SpxfFrame[] = header.frames.map(() => {
    const flux = readF32(),
      v = header.has_var ? readF32() : undefined;
    const fl = new Uint16Array(buf.slice(off, off + px * 2));
    off += pad8(px * 2);
    return { flux, var: v, flags: fl };
  });
  return { header, frames };
}
