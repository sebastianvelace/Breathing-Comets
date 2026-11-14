/** Model inputs quoted on /method. Source: docs/BUILD.md 8.9 and 8.0b/8.0c; instrument values: SPHEREx Explanatory Supplement. */
export const comaModel = {
  g_co2_1au: 2.86e-3, g_co_1au: 2.46e-4, g_h2o_1au: 4.24e-4,
  tau_co2_quiet_s: 5e5, tau_co2_active_s: 3.1e5, tau_co_s: 1.3e6, tau_h2o_s: 8.3e4,
  speed_km_s_at_1au: 0.85, speed_low_km_s_at_1au: 0.5,
  monte_carlo_draws: 4000, calibration_pct: 5, g_pct: 5, tau_lognormal: 0.3, speed_lognormal: 0.2,
  aperture_px: 3, background_ring_px: [40, 55] as [number, number],
  windows_um: { co2_d5: [3.85, 4.42], co_d6: [4.6, 4.74], h2o_d4: [2.5, 2.86] } as Record<string, [number, number]>,
};
export const instrument = { pixel_arcsec: 6.15, exposure_s: 113.58, detectors: 6, fov_deg: [3.5, 11.3] as [number, number] };
export const diffLambda = { references: 8, window_bandwidths: 3, min_references: 3, mad_clip_sigma: 3, mad_scale: 1.4826 };
export const photometry = { radius_px: 4, floor_pct: 3, edge_margin_px: 20 };
export const maskedFlags = [
  "SUR_ERROR", "NONFUNC", "DICHROIC", "MISSING_DATA", "HOT", "COLD", "NONLINEAR", "PERSIST", "BLOOM", "SNOWBALL", "HALO", "SATELLITE_HALO",
];
