import { LitElement, html, css } from "lit";
import { customElement, property } from "lit/decorators.js";
import type { LegData } from "./types";

const VEHICLE_ICONS: Record<string, string> = {
  BUS: "mdi:bus",
  TRAM: "mdi:tram",
  SUBWAY: "mdi:subway",
  HEAVY_RAIL: "mdi:train",
  RAIL: "mdi:train",
  COMMUTER_TRAIN: "mdi:train",
  LIGHT_RAIL: "mdi:tram",
  FERRY: "mdi:ferry",
  WALK: "mdi:walk",
};

/** Horizontal journey bar: one coloured segment per transit leg, striped for walks. */
@customElement("google-transit-journey-bar")
export class GoogleTransitJourneyBar extends LitElement {
  @property({ attribute: false }) public legs: LegData[] = [];

  protected render() {
    if (!this.legs?.length) {
      return html``;
    }

    const totalDuration =
      this.legs.reduce((sum, leg) => sum + (leg.duration || 0), 0) || 1;
    const transitLegs = this.legs.filter((leg) => leg.mode !== "WALK");

    return html`
      <div class="bar">
        ${this.legs.map((leg) => {
          const isWalk = leg.mode === "WALK";
          const width = ((leg.duration || 0) / totalDuration) * 100;
          const icon = VEHICLE_ICONS[leg.mode] ?? "mdi:map-marker-path";
          const color = leg.line_color || "var(--secondary-text-color, #727272)";
          return html`
            <div
              class="segment ${isWalk ? "walk" : "transit"}"
              style="flex-grow: ${Math.max(width, 6)}; ${isWalk
                ? ""
                : `background: ${color};`}"
              title=${leg.line_full_name || leg.mode}
            >
              ${isWalk
                ? html`<ha-icon icon="mdi:walk"></ha-icon>`
                : html`<ha-icon icon=${icon}></ha-icon
                    ><span class="line-name">${leg.line_name}</span>`}
            </div>
          `;
        })}
      </div>
      <div class="times">
        ${transitLegs.map(
          (leg) =>
            html`<span
              >${leg.departure_time_local} → ${leg.arrival_time_local}</span
            >`
        )}
      </div>
    `;
  }

  static styles = css`
    .bar {
      display: flex;
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
      min-width: 6px;
    }

    .segment.walk {
      background: repeating-linear-gradient(
        45deg,
        var(--disabled-text-color, #9e9e9e),
        var(--disabled-text-color, #9e9e9e) 4px,
        transparent 4px,
        transparent 8px
      );
    }

    .segment ha-icon {
      --mdc-icon-size: 15px;
      color: #fff;
    }

    .segment.walk ha-icon {
      color: var(--card-background-color, #fff);
    }

    .line-name {
      font-weight: 700;
    }

    .times {
      display: flex;
      justify-content: space-between;
      font-size: 0.72em;
      color: var(--secondary-text-color, #727272);
    }
  `;
}

declare global {
  interface HTMLElementTagNameMap {
    "google-transit-journey-bar": GoogleTransitJourneyBar;
  }
}
