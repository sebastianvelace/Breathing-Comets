/** Scientific notation with a decimal point and Unicode exponent: 1.17 × 10²⁷. Never locale-aware. */
export function fmtSciUnicode(value: number | null | undefined, digits = 3): string {
  if (value === null || value === undefined || !Number.isFinite(value)) return "—";
  if (value === 0) return "0";
  const exponent = Math.floor(Math.log10(Math.abs(value)));
  if (exponent >= -2 && exponent <= 3) return value.toPrecision(digits);
  const mantissa = (value / 10 ** exponent).toFixed(Math.max(digits - 1, 0));
  const sup = String(exponent)
    .split("")
    .map((c) => "⁰¹²³⁴⁵⁶⁷⁸⁹"["0123456789".indexOf(c)] ?? "⁻")
    .join("");
  return `${mantissa} × 10${sup}`;
}
