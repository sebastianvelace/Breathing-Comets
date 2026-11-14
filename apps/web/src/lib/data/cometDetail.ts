export type DetailFrame = {
  src: string; width: number; height: number; obs_id: string; mjd: number; date: string;
  lam_um: number; bw_um: number; in_co2_band: boolean;
};
export type DetailEpoch = {
  id: string; stack: string; det: number;
  grid: { nx: number; pixel_arcsec: number; north_up: boolean };
  stretch: { lo: number; hi: number; map: string };
  n_frames_stack: number; frames: DetailFrame[];
};
export type DetailPoint = { lam: number; bw: number | null; f: number; e: number; mjd?: number; obs_id?: string };
export type CometDetail = {
  slug: string; name: string; track: string; generated: string; generator: string; credit: string;
  co2_band_um: [number, number]; co_window_um: [number, number];
  epochs: DetailEpoch[];
  spectrum: { by_epoch: Record<string, { d5: DetailPoint[]; d6: DetailPoint[] | null; source: string[] }>; filter: string; units: string };
  census: {
    r_au: number; delta_au: number;
    co2: { q16: number; q50: number; q84: number; q50_alt_tau_g: number; q50_alt_velocity: number; snr_det: number; flux_rel_err: number; n_core: number; chi2_red: number; t_rot_k: number; status: string };
    co: { class: string; q50: number | null; ratio_co_co2: number | null; ratio_16: number | null; ratio_84: number | null; snr_med: number | null; chi2_red: number | null } | null;
    h2o: { class: string } | null;
    aperture: { q_2px: number; q_3px: number; q_5px: number; q_8px: number; dlnq_dlnrho: number; q8_over_q2: number } | null;
  };
  validation: { id: string; species: string; epoch: string; measured: number; published_lo: number; published_hi: number; source: string; chi2_red: number }[];
};
