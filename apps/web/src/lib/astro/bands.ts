import definitions from "../../../static/data/bands.json";

export const bands: {
  label: string;
  center_um: number;
  lo_um: number;
  hi_um: number;
  color: string;
}[] = definitions.bands;
