"""Constants for the Google Transit Routes integration."""

DOMAIN = "google_transit_routes"
API_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
DEFAULT_LANGUAGE = "en"

TRANSIT_FIELD_MASK = ",".join(
    [
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
    ]
)

TRAVEL_FIELD_MASK = ",".join(
    [
        "routes.duration",
        "routes.staticDuration",
        "routes.distanceMeters",
        "routes.localizedValues",
    ]
)

# Config / options keys
CONF_API_KEY = "api_key"
CONF_ROUTES = "routes"  # legacy-only: pre-subentry options storage, read during migration
CONF_ROUTE_NAME = "name"
CONF_ORIGIN = "origin"
CONF_DESTINATION = "destination"
CONF_LANGUAGE = "language"
CONF_UPDATE_INTERVAL = "update_interval"

# Each saved route is a config subentry of this type.
SUBENTRY_TYPE_ROUTE = "route"

# Service / action input keys
ATTR_ORIGIN = "origin"
ATTR_DESTINATION = "destination"
ATTR_LANGUAGE = "language"
ATTR_DEPARTURE_TIME = "departure_time"
ATTR_ARRIVAL_TIME = "arrival_time"
ATTR_ALTERNATIVES = "alternatives"
ATTR_TRANSIT_MODE = "transit_mode"
ATTR_ROUTING_PREFERENCE = "routing_preference"
ATTR_MODE = "mode"
ATTR_AVOID = "avoid"
ATTR_TRAFFIC_MODEL = "traffic_model"

SERVICE_GET_TRANSIT_ROUTE = "get_transit_route"
SERVICE_GET_TRAVEL_TIME = "get_travel_time"

DEFAULT_ALTERNATIVES = True

ATTRIBUTION = "Powered by Google"

# Entity domains supported for location resolution
ENTITY_DOMAIN_ZONE = "zone"
ENTITY_DOMAIN_DEVICE_TRACKER = "device_tracker"
ENTITY_DOMAIN_PERSON = "person"
ENTITY_DOMAIN_SENSOR = "sensor"
