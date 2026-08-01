export interface HassEntity {
  entity_id: string;
  state: string;
  attributes: Record<string, any>;
}

export interface HomeAssistant {
  states: { [entity_id: string]: HassEntity };
  callService: (
    domain: string,
    service: string,
    data?: Record<string, unknown>
  ) => Promise<void>;
  locale?: { language: string };
  themes?: { darkMode?: boolean };
}

export interface LegData {
  mode: string;
  duration?: number;
  line_name?: string;
  line_full_name?: string;
  headsign?: string;
  departure_stop?: string;
  departure_time?: string;
  departure_time_local?: string;
  arrival_stop?: string;
  arrival_time?: string;
  arrival_time_local?: string;
  stop_count?: number;
  agency?: string;
  line_color?: string | null;
  vehicle_type?: string;
}

export interface RouteData {
  arrival_time: string;
  arrival_time_local: string;
  departure_time: string;
  departure_time_local: string;
  duration: number;
  duration_text: string;
  duration_from_now?: number;
  duration_from_now_text?: string;
  distance_text: string;
  legs: LegData[];
}

export interface EntityConfig {
  entity: string;
  name?: string;
  icon?: string;
}

export interface GoogleTransitRoutesCardConfig {
  type: string;
  title?: string;
  entities: EntityConfig[];
  show_alternatives?: boolean;
  show_legs?: boolean;
  show_countdown?: boolean;
  refresh_interval?: number;
  theme?: "auto" | "light" | "dark";
  compact?: boolean;
}
