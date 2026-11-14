import { parseView } from "./view.js";
export const view = $state(parseView(new URLSearchParams()));
