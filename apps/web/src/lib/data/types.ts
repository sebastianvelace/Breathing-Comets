export type Grid = {
  nx: number;
  ny: number;
  crval: [number, number];
  crpix: [number, number];
  cdelt_deg: [number, number];
  north_up: boolean;
};
export type FrameMeta = {
  obs_id: string;
  mjd: number;
  date: string;
  lam_um: number;
  bw_um: number;
  visit: number;
  collection: string;
  diff_sigma?: number;
  diff_available?: boolean;
};
export type Header = {
  grid: Grid;
  det: number;
  kind: string;
  has_var: boolean;
  frames: FrameMeta[];
  visits: unknown[];
  stretch_hint: { lo: number; hi: number } | number[];
  [key: string]: unknown;
};
export type Frame = {
  flux: Float32Array;
  var?: Float32Array;
  flags: Uint16Array;
};
export type Stack = { header: Header; frames: Frame[] };
export type GaiaStar = {
  source_id: string;
  ra: number;
  dec: number;
  pmra: number | null;
  pmdec: number | null;
  parallax: number | null;
  ref_epoch: number;
};
export type Note = { key: string; label: string; value: string; ref: string };
export type Manifest = {
  slug: string;
  name: string;
  ra: number;
  dec: number;
  fov_deg: number;
  default_det: number;
  default_mode: string;
  stacks: Record<string, string>;
  diff: Record<string, string>;
  gaia: string;
  gaia_target_id?: string;
  field_notes: Note[];
  caveat: string;
  pm?: {
    ra0: number;
    dec0: number;
    pmra_masyr: number;
    pmdec_masyr: number;
    ref_epoch_jyear: number;
  };
};
export type SpectrumPoint = {
  lam: number;
  f: number;
  e: number;
  sat?: boolean;
  mjd?: number;
};
