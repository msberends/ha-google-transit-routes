/** "1h22m33s" / "22m33s" / "33s" — no rounding, no leading zeroes; a zero
 * seconds component is dropped rather than shown as "0s" (e.g. "5m" not
 * "5m0s"), unless the whole duration is zero. */
export function formatDuration(totalSeconds: number): string {
  const seconds = Math.floor(totalSeconds % 60);
  const totalMinutes = Math.floor(totalSeconds / 60);
  const minutes = totalMinutes % 60;
  const hours = Math.floor(totalMinutes / 60);
  const secondsPart = seconds > 0 ? `${seconds}s` : "";
  if (hours > 0) {
    return `${hours}h${minutes}m${secondsPart}`;
  }
  if (minutes > 0) {
    return `${minutes}m${secondsPart}`;
  }
  return secondsPart || "0s";
}
