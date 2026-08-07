import { LitElement, html, css, PropertyValues, TemplateResult, nothing } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import "./countdown";
import "./journey-bar";
import { cardStyles } from "./styles";
import { VEHICLE_ICONS } from "./icons";
import { formatDuration } from "./duration";
import { stripNegligibleTrailingWalk } from "./legs";
import type {
  EntityConfig,
  GoogleTransitRoutesCardConfig,
  HomeAssistant,
  LegData,
  RouteData,
} from "./types";

/** Modes with a meaningful short line number/name (e.g. bus "4"), shown as a
 * coloured badge. Everything else (trains, ferries, walking) is icon-only. */
const NUMBERED_LINE_MODES = new Set(["BUS", "TRAM", "SUBWAY", "LIGHT_RAIL"]);

const CARD_VERSION = "0.1.0";

// eslint-disable-next-line no-console
console.info(
  `%c GOOGLE-TRANSIT-ROUTES-CARD %c v${CARD_VERSION} `,
  "color: white; background: #1a73e8; font-weight: 700;",
  "color: #1a73e8; background: white; font-weight: 700;"
);

/**
 * Wall-mounted dashboard card for the Google Transit Routes integration.
 * Reads sensor state/attributes only; it never calls the Google API directly.
 */
@customElement("google-transit-routes-card")
export class GoogleTransitRoutesCard extends LitElement {
  @property({ attribute: false }) public hass?: HomeAssistant;

  @state() private _config?: GoogleTransitRoutesCardConfig;
  @state() private _expanded: Set<string> = new Set();

  private _refreshTimer?: number;

  public static async getConfigElement(): Promise<HTMLElement> {
    await import("./editor");
    return document.createElement("google-transit-routes-card-editor");
  }

  public static getStubConfig(): GoogleTransitRoutesCardConfig {
    return {
      type: "custom:google-transit-routes-card",
      title: "Reistijden",
      entities: [],
      show_alternatives: true,
      show_legs: true,
      show_countdown: true,
      refresh_interval: 0,
      theme: "auto",
      compact: false,
    };
  }

  public setConfig(config: GoogleTransitRoutesCardConfig): void {
    if (!config.entities || !Array.isArray(config.entities)) {
      throw new Error("google-transit-routes-card: 'entities' is required");
    }
    this._config = {
      show_alternatives: true,
      show_legs: true,
      show_countdown: true,
      refresh_interval: 0,
      theme: "auto",
      compact: false,
      ...config,
    };
  }

  public getCardSize(): number {
    return 1 + (this._config?.entities?.length || 1) * 3;
  }

  public connectedCallback(): void {
    super.connectedCallback();
    this._scheduleRefresh();
  }

  public disconnectedCallback(): void {
    super.disconnectedCallback();
    this._clearRefresh();
  }

  protected updated(changed: PropertyValues): void {
    if (changed.has("_config")) {
      this._scheduleRefresh();
      this._applyThemeClass();
    }
  }

  private _applyThemeClass(): void {
    this.classList.remove("force-light", "force-dark");
    if (this._config?.theme === "light") {
      this.classList.add("force-light");
    } else if (this._config?.theme === "dark") {
      this.classList.add("force-dark");
    }
  }

  private _clearRefresh(): void {
    if (this._refreshTimer !== undefined) {
      window.clearInterval(this._refreshTimer);
      this._refreshTimer = undefined;
    }
  }

  private _scheduleRefresh(): void {
    this._clearRefresh();
    const interval = (this._config?.refresh_interval ?? 0) * 1000;
    if (!interval) {
      return;
    }
    this._refreshTimer = window.setInterval(() => this._refreshEntities(), interval);
  }

  private _refreshEntities(): void {
    if (!this.hass || !this._config) {
      return;
    }
    const entityIds = this._config.entities
      .map((e) => e.entity)
      .filter(Boolean);
    if (!entityIds.length) {
      return;
    }
    this.hass.callService("homeassistant", "update_entity", {
      entity_id: entityIds,
    });
  }

  private _toggleExpanded(entityId: string): void {
    const expanded = new Set(this._expanded);
    if (expanded.has(entityId)) {
      expanded.delete(entityId);
    } else {
      expanded.add(entityId);
    }
    this._expanded = expanded;
  }

  protected render(): TemplateResult {
    if (!this._config || !this.hass) {
      return html``;
    }

    const compact = this._config.compact;

    return html`
      <ha-card .header=${this._config.title}>
        <div class="card-content ${compact ? "compact" : ""}">
          ${this._config.entities.map((entityConf) =>
            this._renderRoute(entityConf)
          )}
        </div>
      </ha-card>
    `;
  }

  private _renderRoute(entityConf: EntityConfig): TemplateResult {
    const hass = this.hass!;
    const config = this._config!;
    const stateObj = entityConf.entity ? hass.states[entityConf.entity] : undefined;
    const language = hass.locale?.language || "en";
    const nl = language === "nl";

    if (!stateObj) {
      return html`
        <div class="route-row unavailable">
          <div class="route-header">
            <ha-icon icon=${entityConf.icon || "mdi:bus-clock"}></ha-icon>
            <span class="route-name">${entityConf.name || entityConf.entity}</span>
            <span class="arrival"
              >${nl ? "entiteit niet gevonden" : "entity not found"}</span
            >
          </div>
        </div>
      `;
    }

    const attrs = stateObj.attributes;
    const arrivalTime: string | undefined = attrs.arrival_time;
    const arrivalLocal: string | undefined = attrs.arrival_time_local;
    const legs = attrs.legs || [];
    const alternatives: RouteData[] = attrs.alternative_routes || [];
    const routeName = entityConf.name || attrs.friendly_name || entityConf.entity;
    const isExpanded = this._expanded.has(entityConf.entity);
    const departed = arrivalTime
      ? new Date(arrivalTime).getTime() < Date.now()
      : false;
    const hasAlternatives = config.show_alternatives && alternatives.length > 0;

    return html`
      <div
        class="route-row ${departed ? "departed" : ""}"
        @click=${hasAlternatives
          ? () => this._toggleExpanded(entityConf.entity)
          : undefined}
      >
        <div class="route-header">
          <ha-icon icon=${entityConf.icon || "mdi:bus-clock"}></ha-icon>
          <span class="route-name">${routeName}</span>
          <span class="arrival">
            ${arrivalLocal
              ? html`${nl ? "aankomst" : "arrival"} ${arrivalLocal}`
              : nl
                ? "geen route gevonden"
                : "no route found"}
          </span>
        </div>

        <div class="route-sub">
          ${config.show_countdown && arrivalTime
            ? html`<google-transit-countdown
                .arrival=${arrivalTime}
                .language=${language}
              ></google-transit-countdown>`
            : html`<span></span>`}
          ${hasAlternatives
            ? html`<ha-icon
                class="expand-arrow ${isExpanded ? "open" : ""}"
                icon="mdi:chevron-down"
              ></ha-icon>`
            : nothing}
        </div>

        ${config.show_legs && legs.length
          ? html`<google-transit-journey-bar
              .legs=${legs}
              .expanded=${isExpanded}
              .language=${language}
            ></google-transit-journey-bar>`
          : nothing}
        ${hasAlternatives && isExpanded
          ? html`
              <div class="alternatives">
                <strong class="alternatives-label"
                  >${nl ? "Alternatieven:" : "Alternatives:"}</strong
                >
                ${alternatives.slice(0, 3).map(
                  (alt) => html`
                    <div class="alternative-row">
                      <span>
                        ${alt.departure_time_local} → ${alt.arrival_time_local}
                        (${alt.duration_text})
                      </span>
                      <span class="alt-legs">
                        ${stripNegligibleTrailingWalk(alt.legs || []).map(
                          (leg, i) =>
                            html`${i > 0 ? ", " : ""}${this._renderAltLeg(
                              leg
                            )}`
                        )}
                      </span>
                    </div>
                  `
                )}
              </div>
            `
          : nothing}
      </div>
    `;
  }

  /** One leg in the compact alternatives list: a coloured line-number badge
   * for bus/tram/subway/light-rail, or a bare icon for everything else
   * (train, ferry, walk), each followed by its duration. */
  private _renderAltLeg(leg: LegData): TemplateResult {
    const duration = formatDuration(leg.duration || 0);
    if (NUMBERED_LINE_MODES.has(leg.mode) && leg.line_name) {
      const color = leg.line_color || "var(--secondary-text-color, #727272)";
      return html`<span class="alt-leg"
        ><span class="alt-line-badge" style="background: ${color}"
          >${leg.line_name}</span
        >
        (${duration})</span
      >`;
    }
    const isWalk = leg.mode === "WALK";
    const icon = VEHICLE_ICONS[leg.mode] ?? "mdi:map-marker-path";
    return html`<span class="alt-leg"
      ><ha-icon
        class=${isWalk ? "alt-walk-icon" : "alt-mode-icon"}
        icon=${icon}
      ></ha-icon>
      (${duration})</span
    >`;
  }

  static styles = cardStyles;
}

declare global {
  interface Window {
    customCards: Array<Record<string, unknown>>;
  }
  interface HTMLElementTagNameMap {
    "google-transit-routes-card": GoogleTransitRoutesCard;
  }
}

window.customCards = window.customCards || [];
window.customCards.push({
  type: "google-transit-routes-card",
  name: "Google Transit Routes Card",
  description:
    "Wall-mounted dashboard card showing saved Google Transit routes with live countdowns, journey bars and alternative departures.",
  preview: true,
});
