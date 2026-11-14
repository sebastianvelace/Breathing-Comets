import { error } from "@sveltejs/kit";
import type { EntryGenerator, PageLoad } from "./$types";

export const prerender = true;

// Only comets with a detail packet (stack plates + spectra) get a page.
const packets = import.meta.glob("../../../../static/data/comets/{3i-atlas,29p-schwassmann-wachmann}.json");

const slugOf = (path: string) => path.split("/").pop()!.replace(".json", "");

export const entries: EntryGenerator = () => Object.keys(packets).map((p) => ({ slug: slugOf(p) }));

export const load: PageLoad = async ({ params }) => {
  const key = Object.keys(packets).find((p) => slugOf(p) === params.slug);
  if (!key) error(404, "No detail page for this comet");
  const module = (await packets[key]()) as { default: import("#lib/data/cometDetail.js").CometDetail };
  return { detail: module.default };
};
