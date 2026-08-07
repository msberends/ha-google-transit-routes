import { LitElement, html, css, nothing } from "lit";
import { customElement, property } from "lit/decorators.js";
import type { LegData } from "./types";
import { VEHICLE_ICONS } from "./icons";
import { formatDuration } from "./duration";
import { isTrainMode, stripNegligibleTrailingWalk } from "./legs";
import { agencyColor } from "./agency-colors";

/** Horizontal journey bar: one coloured segment per transit leg, striped for walks. */
@customElement("google-transit-journey-bar")
export class GoogleTransitJourneyBar extends LitElement {
  @property({ attribute: false }) public legs: LegData[] = [];
  @property({ attribute: false }) public expanded = false;
  @property({ attribute: false }) public language = "en";

  protected render() {
    if (!this.legs?.length) {
      return html``;
    }

    const legs = stripNegligibleTrailingWalk(this.legs);
    if (!legs.length) {
      return html``;
    }

    // A walk leg's own span (departure_time → arrival_time) can be longer
    // than its real walking duration when it's chained up to a connecting
    // transit leg that doesn't depart right away — the difference is time
    // spent waiting, not walking. Use the full span for proportions (so the
    // bar reflects real elapsed time) but split each walk block visually
    // into its walking and waiting parts, so a short walk with a long wait
    // doesn't just look like a long walk.
    const spans = legs.map((leg) => this._spanSeconds(leg));
    const totalDuration = spans.reduce((sum, s) => sum + s, 0) || 1;
    const widths = spans.map((s) => Math.max((s / totalDuration) * 100, 6));
    const gridTemplateColumns = widths
      .map((w) => `minmax(0, ${w}fr)`)
      .join(" ");

    return html`
      <div class="bar" style="grid-template-columns: ${gridTemplateColumns}">
        ${legs.map((leg, i) => {
          const isWalk = leg.mode === "WALK";
          const icon = VEHICLE_ICONS[leg.mode] ?? "mdi:map-marker-path";
          const color =
            leg.line_color ||
            agencyColor(leg.agency) ||
            "var(--secondary-text-color, #727272)";
          const walkSeconds = Math.min(leg.duration || 0, spans[i]);
          const waitSeconds = spans[i] - walkSeconds;
          return html`
            <div
              class="segment ${isWalk ? "walk" : "transit"}"
              style=${isWalk ? "" : `background: ${color};`}
              title=${leg.line_full_name || leg.mode}
            >
              ${isWalk
                ? html`
                    <div
                      class="walk-part"
                      style="flex-grow: ${Math.max(walkSeconds, 1)}"
                    >
                      <ha-icon icon="mdi:walk"></ha-icon>
                    </div>
                    ${waitSeconds > 0
                      ? html`<div
                          class="wait-part"
                          style="flex-grow: ${waitSeconds}"
                          title="Waiting"
                        >
                          <ha-icon icon="mdi:human"></ha-icon>
                        </div>`
                      : nothing}
                  `
                : html`<ha-icon icon=${icon}></ha-icon
                    ><span class="line-name">${leg.line_name}</span>`}
            </div>
          `;
        })}
      </div>
      <div class="times" style="grid-template-columns: ${gridTemplateColumns}">
        ${legs.map((leg, i) => {
          // A walk's own span can include waiting time for the connection
          // that follows it; the displayed duration should only ever be the
          // time actually spent walking.
          const displaySeconds =
            leg.mode === "WALK"
              ? Math.min(leg.duration || 0, spans[i])
              : spans[i];
          return html`<span>${this._legTimeLabel(leg, displaySeconds)}</span>`;
        })}
      </div>
      ${this.expanded
        ? html`<div class="leg-details">
            ${legs.map((leg) => {
              const label = this._legDetailLabel(leg);
              return label
                ? html`<div class="leg-detail-row">
                    <ha-icon
                      icon=${VEHICLE_ICONS[leg.mode] ?? "mdi:map-marker-path"}
                    ></ha-icon>
                    <span>${label}</span>
                  </div>`
                : nothing;
            })}
          </div>`
        : nothing}
    `;
  }

  /** "H:MM (duration)" — the end time is omitted since it's always the next block's start. */
  private _legTimeLabel(leg: LegData, spanSeconds: number): string {
    if (!leg.departure_time_local) {
      return "";
    }
    return spanSeconds > 0
      ? `${leg.departure_time_local} (${formatDuration(spanSeconds)})`
      : leg.departure_time_local;
  }

  /** "Hereplein → Hoofdstation · 4 stops" — only meaningful for transit legs. */
  private _legDetailLabel(leg: LegData): string {
    if (leg.mode === "WALK" || !leg.departure_stop || !leg.arrival_stop) {
      return "";
    }
    const nl = this.language === "nl";
    const isTrain = isTrainMode(leg.mode);
    const stops = leg.stop_count
      ? ` · ${leg.stop_count} ${
          nl
            ? isTrain
              ? "station" + (leg.stop_count === 1 ? "" : "s")
              : leg.stop_count === 1
                ? "halte"
                : "haltes"
            : isTrain
              ? leg.stop_count === 1
                ? "station"
                : "stations"
              : leg.stop_count === 1
                ? "stop"
                : "stops"
        }`
      : "";
    return `${this._stripCityPrefix(leg.departure_stop)} → ${this._stripCityPrefix(
      leg.arrival_stop
    )}${stops}`;
  }

  /** Bus/tram stop names come back from the API as "City, Stop Name"; the
   * city prefix is redundant here (the route header already names the
   * cities) and just eats space. Train stations are typically a bare name
   * with no comma, so they pass through unchanged. */
  private _stripCityPrefix(stopName: string): string {
    const commaIndex = stopName.indexOf(",");
    return commaIndex === -1 ? stopName : stopName.slice(commaIndex + 1).trim();
  }

  /** Elapsed seconds for a leg: its actual departure→arrival span when known
   * (may include waiting for walk legs), falling back to its own duration. */
  private _spanSeconds(leg: LegData): number {
    if (leg.departure_time && leg.arrival_time) {
      const ms =
        new Date(leg.arrival_time).getTime() -
        new Date(leg.departure_time).getTime();
      if (!Number.isNaN(ms) && ms >= 0) {
        return Math.round(ms / 1000);
      }
    }
    return leg.duration || 0;
  }

  static styles = css`
    .bar {
      display: grid;
      grid-auto-flow: column;
      height: 26px;
      border-radius: 13px;
      overflow: hidden;
      margin: 6px 0 2px;
    }

    .segment {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 3px;
      color: #fff;
      font-size: 0.72em;
      overflow: hidden;
    }

    .segment.walk {
      /* .walk-part / .wait-part fill this — no background of its own. */
      gap: 0;
      overflow: hidden;
    }

    .walk-part {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
      min-width: 16px;
      background: repeating-linear-gradient(
        45deg,
        var(--disabled-text-color, #9e9e9e),
        var(--disabled-text-color, #9e9e9e) 4px,
        var(--secondary-background-color, #e0e0e0) 4px,
        var(--secondary-background-color, #e0e0e0) 8px
      );
    }

    /* Flat, unstriped fill: visually distinct from the walking stripe so a
       waiting stretch doesn't read as "more walking". */
    .wait-part {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
      min-width: 16px;
      background: var(--secondary-background-color, #e0e0e0);
    }

    .segment ha-icon {
      --mdc-icon-size: 15px;
      color: #fff;
    }

    .walk-part ha-icon,
    .wait-part ha-icon {
      --mdc-icon-size: 13px;
      color: #fff;
      background: var(--disabled-text-color, #9e9e9e);
      border-radius: 50%;
      padding: 2px;
    }

    .line-name {
      font-weight: 700;
    }

    .times {
      display: grid;
      grid-auto-flow: column;
      font-size: 0.72em;
      color: var(--secondary-text-color, #727272);
    }

    .times span {
      overflow: visible;
      white-space: nowrap;
      text-align: left;
    }

    .leg-details {
      display: flex;
      flex-direction: column;
      gap: 2px;
      font-size: 0.72em;
      font-style: italic;
      color: var(--secondary-text-color, #727272);
      margin-top: 4px;
    }

    .leg-detail-row {
      display: flex;
      align-items: flex-start;
      gap: 4px;
    }

    .leg-detail-row ha-icon {
      --mdc-icon-size: 13px;
      flex-shrink: 0;
      margin-top: 1px;
    }

    .leg-detail-row span {
      white-space: normal;
      overflow-wrap: break-word;
    }
  `;
}

declare global {
  interface HTMLElementTagNameMap {
    "google-transit-journey-bar": GoogleTransitJourneyBar;
  }
}
