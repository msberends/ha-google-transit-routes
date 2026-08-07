/** Approximate primary brand colors for Dutch train operators, used when
 * Google's Routes API doesn't send a `transitLine.color` — which it
 * consistently doesn't for train legs (unlike bus/tram, train "lines" don't
 * carry a GTFS route color). These aren't pulled from official brand
 * guidelines (none of these operators publish one), just their well-known
 * livery colors, so a leg still gets a recognisable colour instead of
 * falling back to plain gray. Keyed by lowercased `leg.agency` as Google
 * reports it. */
const AGENCY_COLORS: Record<string, string> = {
  ns: "#FFC917",
  arriva: "#00A9A0",
  keolis: "#0057A8",
  blauwnet: "#0057A8",
  rrreis: "#0057A8",
  qbuzz: "#78BE21",
  connexxion: "#E2001A",
  breng: "#E2001A",
  valleilijn: "#E2001A",
};

export function agencyColor(agency: string | null | undefined): string | undefined {
  if (!agency) {
    return undefined;
  }
  return AGENCY_COLORS[agency.trim().toLowerCase()];
}
