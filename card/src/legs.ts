import type { LegData } from "./types";

/** Train-like modes, as distinct from bus/tram/subway — used to label stop
 * counts as "station(s)" rather than "stop(s)"/"halte(s)". */
const TRAIN_MODES = new Set(["HEAVY_RAIL", "RAIL", "COMMUTER_TRAIN"]);

export function isTrainMode(mode: string): boolean {
  return TRAIN_MODES.has(mode);
}

/** A sub-minute walk at the very end of a route (e.g. "arrive at the front
 * door") isn't worth a segment of its own — drop it from what's displayed.
 * Only the trailing leg is ever dropped; a short leading or transfer walk is
 * still real time the traveller has to account for. */
export function stripNegligibleTrailingWalk(legs: LegData[]): LegData[] {
  if (!legs.length) {
    return legs;
  }
  const last = legs[legs.length - 1];
  if (last.mode === "WALK" && (last.duration || 0) < 60) {
    return legs.slice(0, -1);
  }
  return legs;
}
