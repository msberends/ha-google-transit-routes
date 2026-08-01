# Claude Code Instructions: `ha-google-transit-routes`

## Repository

`msberends/ha-google-transit-routes` on GitHub.

## Summary

Build a Home Assistant custom integration (HACS-compatible) that exposes the **full** Google Routes API response for transit queries, most importantly **scheduled arrival and departure times**, which the built-in `google_travel_time` integration discards entirely. The integration also includes a custom Lovelace dashboard card for wall-mounted displays.

The official HA integration (`google_travel_time`) only returns duration and distance for transit queries. It throws away `transitDetails` from the Google Routes API response, including stop names, scheduled arrival/departure timestamps, transit line names, headsigns, vehicle types, and stop counts. This integration exists to fill that gap.

---

## 1. Problem Statement

The built-in `google_travel_time` integration and its `get_transit_times` action return only:

```yaml
routes:
  - duration: 3349
    duration_text: "56 min"
    static_duration_text: "56 min"
    distance_meters: 41925
    distance_text: "41,9 km"
```

The Google Routes API actually returns rich transit data per step, including:

- `transitDetails.stopDetails.arrivalTime` (RFC 3339 timestamp)
- `transitDetails.stopDetails.departureTime` (RFC 3339 timestamp)
- `transitDetails.stopDetails.arrivalStop.name`
- `transitDetails.stopDetails.departureStop.name`
- `transitDetails.localizedValues.arrivalTime.time.text` (e.g. "01:24")
- `transitDetails.localizedValues.arrivalTime.timeZone` (e.g. "Europe/Amsterdam")
- `transitDetails.headsign`
- `transitDetails.transitLine.name`
- `transitDetails.transitLine.nameShort`
- `transitDetails.transitLine.color`
- `transitDetails.transitLine.vehicle.type` (BUS, HEAVY_RAIL, SUBWAY, TRAM, etc.)
- `transitDetails.transitLine.vehicle.name.text`
- `transitDetails.transitLine.agencies[].name`
- `transitDetails.stopCount`
- `transitDetails.tripShortText`

All of this is discarded by the official integration. This custom integration exposes it.

---

## 2. Integration Identity

- **Domain:** `google_transit_routes`
- **Name (user-facing):** "Google Transit Routes"
- **HACS category:** Integration (the Lovelace card is bundled in the same repo)
- **IoT class:** Cloud Polling
- **Minimum HA version:** 2024.1.0
- **Python dependencies:** `aiohttp` (already available in HA core, no extra pip packages needed)
- **No dependency on the `googlemaps` Python package.** Use raw HTTP requests to the Routes API via `aiohttp`. This keeps the integration lightweight and avoids pulling in a large SDK.

---

## 3. Google Routes API Details

### Endpoint

```
POST https://routes.googleapis.com/directions/v2:computeRoutes
```

### Required Headers

```
Content-Type: application/json
X-Goog-Api-Key: <API_KEY>
X-Goog-FieldMask: <comma-separated field paths>
```

### Field Mask

The field mask determines what data Google returns. Use this comprehensive mask:

```
routes.duration,routes.distanceMeters,routes.localizedValues,routes.legs.steps.travelMode,routes.legs.steps.transitDetails.stopDetails,routes.legs.steps.transitDetails.localizedValues,routes.legs.steps.transitDetails.headsign,routes.legs.steps.transitDetails.headway,routes.legs.steps.transitDetails.transitLine,routes.legs.steps.transitDetails.stopCount,routes.legs.steps.transitDetails.tripShortText,routes.legs.stepsOverview
```

### Request Body (Transit)

```json
{
  "origin": { "address": "UMCG Noord, Groningen" },
  "destination": { "address": "Station Meadowfield" },
  "travelMode": "TRANSIT",
  "languageCode": "nl",
  "units": "METRIC",
  "computeAlternativeRoutes": true,
  "departureTime": "2026-07-31T23:35:00+02:00",
  "transitPreferences": {
    "routingPreference": "FEWER_TRANSFERS",
    "allowedTravelModes": ["BUS", "TRAIN"]
  }
}
```

### Key Notes on Request Parameters

- `origin` and `destination` can be `{ "address": "..." }` or `{ "location": { "latLng": { "latitude": 53.22, "longitude": 6.57 } } }`.
- `departureTime` and `arrivalTime` are mutually exclusive. Both use RFC 3339 format. If neither is set, the API defaults to "now".
- `computeAlternativeRoutes` must be a JSON boolean (`true`/`false`), not a Python boolean (`True`/`False`).
- `transitPreferences.allowedTravelModes` accepts: `BUS`, `SUBWAY`, `TRAIN`, `LIGHT_RAIL`, `RAIL`.
- `transitPreferences.routingPreference` accepts: `LESS_WALKING`, `FEWER_TRANSFERS`.
- Transit routes do NOT support intermediate waypoints.
- Transit trips are available for up to 7 days in the past and 100 days in the future.

### Response Structure (Transit)

The response for a transit query looks like this (simplified):

```json
{
  "routes": [
    {
      "duration": "4091s",
      "distanceMeters": 42900,
      "localizedValues": {
        "distance": { "text": "42,9 km" },
        "duration": { "text": "1 uur 8 min." },
        "staticDuration": { "text": "1 uur 8 min." },
        "transitFare": {}
      },
      "legs": [
        {
          "steps": [
            { "travelMode": "WALK" },
            {
              "travelMode": "TRANSIT",
              "transitDetails": {
                "stopDetails": {
                  "arrivalStop": {
                    "name": "Groningen, Hereplein",
                    "location": { "latLng": { "latitude": 53.213, "longitude": 6.569 } }
                  },
                  "arrivalTime": "2026-07-31T22:31:00Z",
                  "departureStop": {
                    "name": "Groningen, UMCG Noord",
                    "location": { "latLng": { "latitude": 53.223, "longitude": 6.569 } }
                  },
                  "departureTime": "2026-07-31T22:26:00Z"
                },
                "localizedValues": {
                  "arrivalTime": {
                    "time": { "text": "00:31" },
                    "timeZone": "Europe/Amsterdam"
                  },
                  "departureTime": {
                    "time": { "text": "00:26" },
                    "timeZone": "Europe/Amsterdam"
                  }
                },
                "headsign": "Hoofdstation",
                "transitLine": {
                  "name": "Station Noord - HS - Korreweg - P+R Hoogkerk",
                  "vehicle": {
                    "name": { "text": "Bus" },
                    "type": "BUS",
                    "iconUri": "//maps.gstatic.com/mapfiles/transit/iw2/6/bus2.png"
                  },
                  "agencies": [
                    { "name": "Qbuzz", "uri": "https://www.qbuzz.nl/" }
                  ],
                  "color": "#007bff",
                  "nameShort": "4"
                },
                "stopCount": 5
              }
            },
            { "travelMode": "WALK" },
            {
              "travelMode": "TRANSIT",
              "transitDetails": {
                "stopDetails": {
                  "arrivalStop": { "name": "Meadowfield" },
                  "arrivalTime": "2026-07-31T23:24:00Z",
                  "departureStop": { "name": "Groningen" },
                  "departureTime": "2026-07-31T22:54:00Z"
                },
                "localizedValues": {
                  "arrivalTime": {
                    "time": { "text": "01:24" },
                    "timeZone": "Europe/Amsterdam"
                  },
                  "departureTime": {
                    "time": { "text": "00:54" },
                    "timeZone": "Europe/Amsterdam"
                  }
                },
                "headsign": "Leeuwarden",
                "transitLine": {
                  "name": "Groningen <-> Leeuwarden ST37400",
                  "vehicle": {
                    "name": { "text": "Trein" },
                    "type": "HEAVY_RAIL"
                  }
                },
                "stopCount": 11
              }
            },
            { "travelMode": "WALK" }
          ],
          "stepsOverview": {
            "multiModalSegments": [...]
          }
        }
      ]
    }
  ]
}
```

---

## 4. What to Build

### 4.1 Config Flow (UI-based setup)

Users set up the integration via Settings > Devices & Services > Add Integration.

**Step 1: API Key**
- Input: Google Routes API key
- Validate: make a test call to the Routes API (a simple driving route, e.g. "Amsterdam" to "Rotterdam") to verify the key works. If it fails, show an error.

**Step 2 (optional): Add a saved route**
- Users can optionally add named routes (e.g. "UMCG to Meadowfield") with origin, destination, and preferences.
- Each saved route creates a sensor entity.
- Users can also skip this and only use the action for on-demand queries.

**Options flow:**
- Allow adding/removing saved routes after initial setup.
- Allow changing the API key.

### 4.2 Action: `google_transit_routes.get_transit_route`

This is the primary feature. A callable action (formerly "service") that any automation or script can invoke with dynamic parameters.

**Input parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `origin` | string | Yes | Address, GPS coordinates ("lat,lng"), or HA entity ID (zone.xxx, device_tracker.xxx, person.xxx, sensor.xxx) |
| `destination` | string | Yes | Same format as origin |
| `language` | string | No | BCP-47 language code, default "en" |
| `departure_time` | string | No | RFC 3339 timestamp or ISO datetime string. Mutually exclusive with arrival_time. Default: now. |
| `arrival_time` | string | No | RFC 3339 timestamp. Mutually exclusive with departure_time. |
| `alternatives` | boolean | No | Whether to return alternative routes (up to 3). Default: **true**. |
| `transit_mode` | string | No | Preferred mode: "bus", "subway", "train", "light_rail", "rail". Can be a comma-separated list. |
| `routing_preference` | string | No | "less_walking" or "fewer_transfers". |

**Entity resolution:**
When `origin` or `destination` is an HA entity ID (starts with a known domain prefix like `zone.`, `device_tracker.`, `person.`, `sensor.`):
- For `zone.*`: use the zone's latitude/longitude attributes.
- For `device_tracker.*` and `person.*`: use the entity's latitude/longitude attributes.
- For `sensor.*`: use the entity's state as an address string, or latitude/longitude if available.

**Response data structure:**

The action must return a `response_variable` with this clean, flat structure. **Multiple routes are always returned when available** (up to 4: the default route plus up to 3 alternatives). Users access them as `routes[0]`, `routes[1]`, etc. The routes are sorted by departure time (earliest first).

```yaml
routes:
  - arrival_time: "2026-07-31T23:24:00Z"           # UTC timestamp of final arrival
    arrival_time_local: "01:24"                      # localised time string
    arrival_timezone: "Europe/Amsterdam"              # IANA timezone
    departure_time: "2026-07-31T22:26:00Z"           # UTC timestamp of first transit departure
    departure_time_local: "00:26"                     # localised time string
    departure_timezone: "Europe/Amsterdam"
    duration: 4091                                    # total route duration in seconds (from API)
    duration_text: "1 uur 8 min."                     # localised duration text (from API)
    duration_from_now: 3480                           # seconds from API call time to arrival_time
    duration_from_now_text: "58 min."                 # human-readable version, computed at response time
    distance_meters: 42900
    distance_text: "42,9 km"
    legs:
      - mode: "BUS"
        line_name: "4"                                # nameShort if available, otherwise name
        line_full_name: "Station Noord - HS - Korreweg - P+R Hoogkerk"
        headsign: "Hoofdstation"
        departure_stop: "Groningen, UMCG Noord"
        departure_time: "2026-07-31T22:26:00Z"
        departure_time_local: "00:26"
        arrival_stop: "Groningen, Hereplein"
        arrival_time: "2026-07-31T22:31:00Z"
        arrival_time_local: "00:31"
        stop_count: 5
        agency: "Qbuzz"
        line_color: "#007bff"
        vehicle_type: "BUS"
      - mode: "WALK"
        duration: 480
      - mode: "HEAVY_RAIL"
        line_name: "Stoptrein"
        line_full_name: "Groningen <-> Leeuwarden ST37400"
        headsign: "Leeuwarden"
        departure_stop: "Groningen"
        departure_time: "2026-07-31T22:54:00Z"
        departure_time_local: "00:54"
        arrival_stop: "Meadowfield"
        arrival_time: "2026-07-31T23:24:00Z"
        arrival_time_local: "01:24"
        stop_count: 11
        agency: "Arriva"
        line_color: "#..."
        vehicle_type: "HEAVY_RAIL"
      - mode: "WALK"
        duration: 240
  - arrival_time: "2026-08-01T00:27:00Z"            # second route option
    arrival_time_local: "02:27"
    # ... same structure as above ...
  - arrival_time: "2026-08-01T01:24:00Z"            # third route option
    arrival_time_local: "03:24"
    # ... same structure as above ...
```

Key design decisions for the response:
- **Multiple routes are the default.** The `alternatives` parameter defaults to `true`. All returned routes appear in the `routes` list, sorted by departure time. Users pick the one they need: `routes[0]` for the earliest, `routes[1]` for the next, etc.
- Top-level `arrival_time` is the arrival time of the LAST transit leg (not the last walk), as this is what users care about (when does the train/bus arrive).
- Top-level `departure_time` is the departure time of the FIRST transit leg.
- **`duration_from_now`** is computed at response time as `arrival_time - now()` in seconds. This gives users a single number for "how long until I'm there," which accounts for waiting time before the first departure. The accompanying `duration_from_now_text` is a human-readable string (e.g. "58 min.", "1 uur 23 min."), using the same language as the API response.
- `legs` includes WALK segments with their duration, so users can see the full picture.
- `line_name` prefers `transitLine.nameShort` (e.g. "4") over `transitLine.name` (the full route description), because that is what you see on the bus/sign. Include both.
- All times appear both as UTC timestamps (for computation) and as localised strings (for display in notifications).

### 4.3 Sensor Entities (for saved routes)

For each saved route configured in the options flow, create a sensor entity.

- **Entity ID pattern:** `sensor.google_transit_<slugified_name>`
- **State:** The next arrival time as a localised time string (e.g. "01:24")
- **Device class:** `timestamp` (if using the UTC timestamp as state) or `None` (if using the localised string)
- **Attributes:**
  - `arrival_time` (UTC)
  - `arrival_time_local`
  - `departure_time` (UTC)
  - `departure_time_local`
  - `duration`
  - `duration_text`
  - `duration_from_now` (seconds from now to arrival, recomputed on each state read)
  - `duration_from_now_text`
  - `distance_text`
  - `origin`
  - `destination`
  - `legs` (list of dicts, same structure as in the action response)
  - `alternative_routes` (list of the other route options, same structure)
  - `route_count` (number of routes found, including the primary one)
  - `attribution` ("Powered by Google")
- **Update interval:** **None (no automatic polling).** Sensors only update when triggered via `homeassistant.update_entity` from an automation or script. This is a deliberate design choice to protect users from unexpected API costs. See section 9, constraint 4.
- **On-demand update:** support `homeassistant.update_entity`.

### 4.4 Also Support Non-Transit Modes

While transit is the primary use case, the Routes API supports all travel modes. The integration should also expose:

**Action: `google_transit_routes.get_travel_time`**

For driving, walking, bicycling. Input parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `origin` | string | Yes | Same as transit |
| `destination` | string | Yes | Same as transit |
| `mode` | string | Yes | "driving", "walking", "bicycling", "two_wheeler" |
| `language` | string | No | Default "en" |
| `departure_time` | string | No | RFC 3339 timestamp |
| `avoid` | string | No | Comma-separated: "tolls", "highways", "ferries", "indoor" |
| `traffic_model` | string | No | "best_guess", "pessimistic", "optimistic" |

Response: simplified (no transit legs), just duration, distance, and basic route info.

### 4.5 Lovelace Dashboard Card: `google-transit-routes-card`

A custom Lovelace card designed for wall-mounted tablets and dashboards. It shows saved transit routes at a glance with live countdowns, transit line details, and alternative route options.

#### Design Goals

- **Wall-mounted iPad optimised:** large, readable text. Touch-friendly. Works in kiosk mode.
- **Family-friendly:** multiple saved routes visible at once (e.g. "Papa naar UMCG", "Mama naar Leeuwarden", "Alice naar school").
- **Live countdown:** "arrives in 42 min" that ticks down in real time (client-side JavaScript timer, no polling needed for the countdown itself).
- **Transit leg visualisation:** show a horizontal "journey bar" per route with coloured segments for each transit leg (using `line_color` from the API), with vehicle type icons (bus, train, tram) and line numbers.
- **Alternative routes:** tap a route to expand and see the next 2-3 departure options.
- **Auto-refresh:** the card triggers `homeassistant.update_entity` on its sensors at a configurable interval (default 5 minutes).

#### Card Configuration (YAML)

```yaml
type: custom:google-transit-routes-card
title: "Reistijden"
entities:
  - entity: sensor.google_transit_umcg_to_meadowfield
    name: "Alice → Meadowfield"
    icon: mdi:train
  - entity: sensor.google_transit_meadowfield_to_umcg
    name: "Naar het UMCG"
    icon: mdi:hospital-building
  - entity: sensor.google_transit_home_to_school
    name: "Naar school"
    icon: mdi:school
show_alternatives: true          # show alternative routes on tap
show_legs: true                  # show journey bar with transit legs
show_countdown: true             # live ticking countdown
refresh_interval: 300            # seconds between sensor updates
theme: auto                      # "auto" (follows HA theme), "light", or "dark"
compact: false                   # compact mode for smaller screens
```

#### Visual Layout (per route row)

```
┌─────────────────────────────────────────────────────────┐
│  🚆  Alice → Meadowfield                   aankomst 01:24 │
│                                          over 42 min ▼  │
│  [Bus 4]━━━[walk]━━━[Trein Leeuwarden]━━━[walk]        │
│  00:26        00:31  00:54          01:24                │
├─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┤
│  Alternatief: 00:54 → 02:27 (1u 33m)   Bus 10 + Trein  │
│  Alternatief: 01:10 → 03:24 (2u 14m)   Bus 4 + Trein   │
└─────────────────────────────────────────────────────────┘
```

- The coloured segments in the journey bar use the `line_color` from the API response.
- Vehicle type icons: use MDI icons (`mdi:bus`, `mdi:train`, `mdi:tram`, `mdi:subway`, `mdi:ferry`, `mdi:walk`).
- The countdown ("over 42 min") uses `duration_from_now` from the sensor and ticks down client-side every second.
- The "▼" expands/collapses alternative routes.
- When a route has departed (countdown reaches 0), the row greys out and shows the next route automatically.

#### Technical Implementation

- **Language:** TypeScript, compiled to a single JS file.
- **Framework:** LitElement (the standard for HA custom cards).
- **Bundler:** Rollup (standard for HA card projects).
- **No external runtime dependencies.** Only LitElement and HA frontend types.
- The card reads sensor state and attributes. It does NOT call the Google API directly.
- Register via `window.customCards` for the HA card picker.
- Provide a visual editor (`getConfigElement()`) so users can configure without YAML.

#### File Structure for the Card

```
card/
  src/
    google-transit-routes-card.ts      # Main card component
    editor.ts                          # Visual config editor
    styles.ts                          # CSS styles
    journey-bar.ts                     # Journey bar component (coloured segments)
    countdown.ts                       # Live countdown component
    types.ts                           # TypeScript interfaces
  rollup.config.mjs
  package.json
  tsconfig.json
```

The compiled `google-transit-routes-card.js` goes into `custom_components/google_transit_routes/www/` so it is served by HA automatically when the integration is loaded. The integration's `__init__.py` registers the card resource via `async_register_static_path` or the `lovelace` resource registration pattern.

---

## 5. File Structure

```
custom_components/
  google_transit_routes/
    __init__.py              # Integration setup, register actions, register card resource
    config_flow.py           # UI config flow and options flow
    const.py                 # Constants (DOMAIN, defaults, API URL, field masks)
    coordinator.py           # DataUpdateCoordinator for sensor polling
    sensor.py                # Sensor platform
    api.py                   # Google Routes API client (aiohttp-based)
    helpers.py               # Entity resolution, response parsing, utility functions
    manifest.json
    services.yaml            # Action definitions
    strings.json             # UI strings (English)
    translations/
      en.json                # English translations
      nl.json                # Dutch translations
    icons.json               # MDI icons for the integration
    www/
      google-transit-routes-card.js   # Compiled Lovelace card (committed to repo)
```

Card source (not distributed to HA, only for development):

```
card/
  src/
    google-transit-routes-card.ts
    editor.ts
    styles.ts
    journey-bar.ts
    countdown.ts
    types.ts
  rollup.config.mjs
  package.json
  tsconfig.json
```

Root level of the repo:

```
README.md                    # Documentation
LICENSE                      # MIT
hacs.json                    # HACS metadata
custom_components/           # As above
card/                        # Card source (TypeScript)
```

---

## 6. Implementation Details

### 6.1 `const.py`

```python
DOMAIN = "google_transit_routes"
API_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
DEFAULT_LANGUAGE = "en"

TRANSIT_FIELD_MASK = ",".join([
    "routes.duration",
    "routes.distanceMeters",
    "routes.localizedValues",
    "routes.legs.steps.travelMode",
    "routes.legs.steps.staticDuration",
    "routes.legs.steps.transitDetails.stopDetails",
    "routes.legs.steps.transitDetails.localizedValues",
    "routes.legs.steps.transitDetails.headsign",
    "routes.legs.steps.transitDetails.headway",
    "routes.legs.steps.transitDetails.transitLine",
    "routes.legs.steps.transitDetails.stopCount",
    "routes.legs.steps.transitDetails.tripShortText",
    "routes.legs.stepsOverview",
])

TRAVEL_FIELD_MASK = ",".join([
    "routes.duration",
    "routes.staticDuration",
    "routes.distanceMeters",
    "routes.localizedValues",
])

CONF_API_KEY = "api_key"
CONF_ROUTES = "routes"
CONF_ROUTE_NAME = "name"
CONF_ORIGIN = "origin"
CONF_DESTINATION = "destination"
CONF_LANGUAGE = "language"
CONF_UPDATE_INTERVAL = "update_interval"
```

### 6.2 `api.py`

- Async class `GoogleRoutesApiClient` that wraps `aiohttp.ClientSession`.
- Constructor takes `api_key` and `session`.
- Method `async def get_transit_route(self, origin, destination, language, departure_time, arrival_time, alternatives, transit_mode, routing_preference) -> dict` that:
  1. Builds the request body.
  2. Builds headers including field mask.
  3. POSTs to the API.
  4. Raises appropriate exceptions on HTTP errors (400, 403, 429, 5xx).
  5. Returns the parsed JSON response.
- Method `async def get_travel_time(self, origin, destination, mode, language, departure_time, avoid, traffic_model) -> dict` for non-transit modes.
- Method `async def validate_api_key(self) -> bool` that makes a minimal test request.

**Error handling:**
- 400: `InvalidRequest` (bad parameters)
- 403: `InvalidApiKey`
- 429: `RateLimited`
- 5xx: `ApiUnavailable`
- Define custom exception classes in `api.py` or a separate `exceptions.py`.

### 6.3 `helpers.py`

- `resolve_entity_location(hass, entity_id) -> dict`: Given an HA entity ID, return `{"address": "..."}` or `{"location": {"latLng": {"latitude": ..., "longitude": ...}}}` suitable for the API request body.
- `resolve_location(hass, location_str) -> dict`: Determine if input is an entity ID, lat/lng pair, or address string, and return the appropriate API format.
- `parse_transit_response(api_response: dict) -> list[dict]`: Transform the raw API response into the clean response structure documented in section 4.2. This is the core parsing logic.
- `parse_travel_response(api_response: dict) -> list[dict]`: Simpler parser for non-transit responses.

### 6.4 `__init__.py`

- `async_setup_entry`: register the actions and set up the coordinator.
- Register actions:
  - `google_transit_routes.get_transit_route`
  - `google_transit_routes.get_travel_time`
- Action handlers call the API client, parse the response, and return structured data.

### 6.5 `config_flow.py`

- Step 1: API key input, validate with test call.
- Options flow: manage saved routes (add/remove), change language, change update interval.

### 6.6 `sensor.py`

- `GoogleTransitSensor` extends `CoordinatorEntity` and `SensorEntity`.
- Uses `DataUpdateCoordinator` from `coordinator.py`.
- State is the ISO timestamp of the next arrival.
- All transit details in attributes.

### 6.7 `services.yaml`

Define both actions with their input fields, types, and descriptions. Example:

```yaml
get_transit_route:
  name: Get transit route
  description: >
    Get public transit route with full timetable data including
    scheduled arrival and departure times, transit lines, and stops.
  fields:
    origin:
      name: Origin
      description: Starting point. Address, "lat,lng" coordinates, or entity ID (zone.xxx, person.xxx, device_tracker.xxx).
      required: true
      example: "UMCG Noord, Groningen"
      selector:
        text:
    destination:
      name: Destination
      description: End point. Same formats as origin.
      required: true
      example: "Station Meadowfield"
      selector:
        text:
    language:
      name: Language
      description: BCP-47 language code for localised text in the response.
      required: false
      default: "en"
      example: "nl"
      selector:
        text:
    departure_time:
      name: Departure time
      description: Desired departure time in ISO 8601 / RFC 3339 format. Cannot be combined with arrival_time.
      required: false
      example: "2026-08-01T08:00:00+02:00"
      selector:
        text:
    arrival_time:
      name: Arrival time
      description: Desired arrival time in ISO 8601 / RFC 3339 format. Cannot be combined with departure_time.
      required: false
      example: "2026-08-01T09:00:00+02:00"
      selector:
        text:
    alternatives:
      name: Alternative routes
      description: Whether to return up to 3 alternative routes.
      required: false
      default: true
      selector:
        boolean:
    transit_mode:
      name: Preferred transit mode
      description: Preferred transit vehicle type(s).
      required: false
      selector:
        select:
          multiple: true
          options:
            - label: Bus
              value: bus
            - label: Subway
              value: subway
            - label: Train
              value: train
            - label: Light rail
              value: light_rail
            - label: Rail
              value: rail
    routing_preference:
      name: Routing preference
      description: Preference for the transit route.
      required: false
      selector:
        select:
          options:
            - label: Less walking
              value: less_walking
            - label: Fewer transfers
              value: fewer_transfers
```

### 6.8 `manifest.json`

```json
{
  "domain": "google_transit_routes",
  "name": "Google Transit Routes",
  "codeowners": ["@msberends"],
  "config_flow": true,
  "dependencies": [],
  "documentation": "https://github.com/msberends/ha-google-transit-routes",
  "iot_class": "cloud_polling",
  "issue_tracker": "https://github.com/msberends/ha-google-transit-routes/issues",
  "requirements": [],
  "version": "0.1.0"
}
```

### 6.9 `hacs.json`

```json
{
  "name": "Google Transit Routes",
  "render_readme": true
}
```

---

## 7. Usage Examples (for README.md)

### Action call in an automation

```yaml
actions:
  - action: google_transit_routes.get_transit_route
    data:
      origin: "zone.umcg_noord"
      destination: "zone.station_meadowfield"
      language: "nl"
    response_variable: transit

  - action: ntfy.publish
    data:
      title: "🚆 Alice vertrokken"
      message: >-
        Alice is vertrokken vanuit het UMCG.
        Verwachte aankomsttijd: {{ transit.routes[0].arrival_time_local }} uur (over {{ transit.routes[0].duration_from_now_text }}).
        Via: {% for leg in transit.routes[0].legs if leg.mode != 'WALK' %}{{ leg.line_name }} ({{ leg.headsign }}){% if not loop.last %}, {% endif %}{% endfor %}.
        {% if transit.routes | length > 1 %}
        Alternatief: {{ transit.routes[1].departure_time_local }} → {{ transit.routes[1].arrival_time_local }} uur.
        {% endif %}
    target:
      entity_id: notify.bob
```

### Sensor on a dashboard (standard entities card)

```yaml
type: entities
entities:
  - entity: sensor.google_transit_umcg_to_meadowfield
    name: "Volgende trein naar Meadowfield"
```

### Custom card on a dashboard (wall-mounted iPad)

```yaml
type: custom:google-transit-routes-card
title: "Reistijden"
entities:
  - entity: sensor.google_transit_umcg_to_meadowfield
    name: "Alice → Meadowfield"
  - entity: sensor.google_transit_meadowfield_to_umcg
    name: "Naar het UMCG"
show_alternatives: true
show_legs: true
show_countdown: true
```

### Template usage with the action response

```jinja2
{# First (earliest) route #}
{% set route = transit.routes[0] %}
Aankomst: {{ route.arrival_time_local }} uur (over {{ route.duration_from_now_text }})

{# List all transit legs #}
{% for leg in route.legs if leg.mode != 'WALK' %}
  {{ leg.line_name }} richting {{ leg.headsign }}: {{ leg.departure_time_local }} → {{ leg.arrival_time_local }}
{% endfor %}

{# Show all available routes #}
{% for route in transit.routes %}
  Optie {{ loop.index }}: vertrek {{ route.departure_time_local }}, aankomst {{ route.arrival_time_local }} ({{ route.duration_from_now_text }})
{% endfor %}
```

---

## 8. Testing

### Manual Testing

Use Developer Tools > Actions in Home Assistant to call `google_transit_routes.get_transit_route` with test parameters and inspect the response.

### Automated Tests

Write tests in a `tests/` directory at the repo root:

- `tests/test_api.py`: mock the HTTP responses and test the API client.
- `tests/test_helpers.py`: test entity resolution and response parsing with fixture data.
- `tests/test_config_flow.py`: test the config flow steps.

Use `pytest` and `pytest-homeassistant-custom-component` for HA-specific test infrastructure.

Include fixture JSON files in `tests/fixtures/` with real (anonymised) API responses for transit routes.

---

## 9. Important Constraints

1. **No `googlemaps` Python package.** Use `aiohttp` directly. The HA runtime already has it.
2. **No synchronous I/O.** All API calls must be async.
3. **API key in `secrets.yaml` or via config flow.** Never hardcode. The config flow stores it encrypted in `.storage`.
4. **NO AUTOMATIC POLLING. This is critical.** Transit queries hit the Compute Routes Pro SKU, which has a free cap of only **5,000 requests/month** (after the March 2025 pricing change). Beyond that, it costs $10 per 1,000 requests. Automatic polling on even a single sensor at 15-minute intervals would consume ~2,880 requests/month. Two sensors would exceed the free cap. Therefore:
   - The `DataUpdateCoordinator` must have **no automatic polling interval**. Set `update_interval=None`.
   - Sensors update **only** when explicitly triggered via `homeassistant.update_entity` from an automation or script.
   - The config flow and README must make this crystal clear: API calls only happen when deliberately triggered.
   - Include example automations showing the recommended pattern (time-based triggers on working days, zone-based triggers).
   - Consider adding an optional monthly API call counter (stored in `hass.data`) with a configurable warning threshold that fires a persistent notification when the user approaches their free cap.
5. **Boolean serialisation.** When building JSON payloads, ensure Python booleans are serialised correctly (`true`/`false`, not `True`/`False`). Use `json.dumps()` for the request body, which handles this automatically. The earlier `rest_command` approach had this bug because Jinja renders booleans as Python.
6. **Attribution.** Google requires attribution. Include "Powered by Google" in sensor attributes, in the Lovelace card footer, and document this requirement.
7. **Error messages.** Surface API error messages to the user via HA's notification system or persistent notifications, especially for auth errors and quota exceeded.

---

## 10. README.md Content

The README should include:

1. **Header** with badges (HACS, GitHub release, license).
2. **Why this exists**: one paragraph explaining the gap in the official integration, with a comparison table showing what the official integration returns vs what this one returns.
3. **Screenshot** of the Lovelace card on a dashboard (placeholder until real screenshots exist).
4. **Features**: bullet list including actions, sensors, multiple routes, duration_from_now, dashboard card.
5. **Installation** via HACS (add custom repo) and manual.
6. **Configuration** via UI config flow.
7. **Usage: Actions**: action examples for automations with multiple routes.
8. **Usage: Sensors**: sensor examples for dashboards.
9. **Usage: Dashboard Card**: card configuration YAML, visual editor instructions, screenshot.
10. **API key setup**: link to Google Cloud Console, explain that only the Routes API needs to be enabled.
11. **API quota**: note the 5,000 free requests/month for Compute Routes Pro, and the cost beyond that.
12. **Response reference**: full documentation of the response structure including all routes[n] fields.
13. **Comparison with the official integration**: table.
14. **Contributing** and **License** (MIT).

---

## 11. Code Style and Quality

- Follow HA core coding standards: type hints on all functions, docstrings, `ruff` for linting.
- Use `homeassistant.helpers.aiohttp_client.async_get_clientsession` for the HTTP session.
- Use `voluptuous` schemas for action input validation.
- Use `DataUpdateCoordinator` for sensor updates.
- All strings that appear in the UI go through `strings.json` / `translations/`.
- Log at appropriate levels: `_LOGGER.debug` for API requests/responses, `_LOGGER.error` for failures.

---

## 12. Priorities

Build in this order:

**Phase 1: Core integration (get it working)**

1. `const.py`, `manifest.json`, `hacs.json`
2. `api.py` (the API client, this is the core)
3. `helpers.py` (response parsing, entity resolution, `duration_from_now` computation)
4. `__init__.py` with action registration
5. `services.yaml`
6. `config_flow.py` (API key validation)
7. `strings.json` and translations

**Phase 2: Sensors**

8. `coordinator.py` and `sensor.py` (with `alternative_routes` in attributes)

**Phase 3: Dashboard card**

9. Card TypeScript source in `card/src/`
10. Rollup build config
11. Compiled JS in `custom_components/google_transit_routes/www/`
12. Card resource registration in `__init__.py`

**Phase 4: Polish**

13. `README.md`
14. Tests

The action (`get_transit_route`) is the highest priority. Get the action working and returning clean multi-route data first. Sensors build on the same API client and parser. The card builds on the sensors. Each phase should be independently functional.
