import configuration from "../../../static/data/hips.json";
import table from "../../../static/data/channels.json";

export const hips = configuration;
export const channels = table.channels;

/** Aladin 3.8.2 indexes this cube linearly in frequency; labels come from channels. */
export function frequencyForFrame(frame: number): number {
  const speedOfLight = 299792458;
  const low = speedOfLight / hips.em_max_m,
    high = speedOfLight / hips.em_min_m;
  return (
    low +
    ((Math.max(0, Math.min(channels.length - 1, frame)) + 0.5) /
      channels.length) *
      (high - low)
  );
}

export function nearestChannel(wavelength?: number): number {
  if (wavelength === undefined) return 0;
  return channels.reduce(
    (best, channel, i) =>
      hips.blank_frames.includes(channel.frame)
        ? best
        : Math.abs(channel.wavelength_um - wavelength) <
            Math.abs(channels[best].wavelength_um - wavelength)
          ? i
          : best,
    0,
  );
}
