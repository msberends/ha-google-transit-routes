import { LitElement, html, css, nothing } from "lit";
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

    // A walk leg's own span (departure_time → arrival_time) can be longer
    // than its real walking duration when it's chained up to a connecting
    // transit leg that doesn't depart right away — the difference is time
    // spent waiting, not walking. Use the full span for proportions (so the
    // bar reflects real elapsed time) but split each walk block visually
    // into its walking and waiting parts, so a short walk with a long wait
    // doesn't just look like a long walk.
    const spans = this.legs.map((leg) => this._spanSeconds(leg));
    const totalDuration = spans.reduce((sum, s) => sum + s, 0) || 1;
    const widths = spans.map((s) => Math.max((s / totalDuration) * 100, 6));

    return html`
      <div class="bar">
        ${this.legs.map((leg, i) => {
          const isWalk = leg.mode === "WALK";
          const icon = VEHICLE_ICONS[leg.mode] ?? "mdi:map-marker-path";
          const color = leg.line_color || "var(--secondary-text-color, #727272)";
          const walkSeconds = Math.min(leg.duration || 0, spans[i]);
          const waitSeconds = spans[i] - walkSeconds;
          return html`
            <div
              class="segment ${isWalk ? "walk" : "transit"}"
              style="flex-grow: ${widths[i]}; ${isWalk
                ? ""
                : `background: ${color};`}"
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
                        ></div>`
                      : nothing}
                  `
                : html`<ha-icon icon=${icon}></ha-icon
                    ><span class="line-name">${leg.line_name}</span>`}
            </div>
          `;
        })}
      </div>
      <div class="times">
        ${this.legs.map(
          (leg, i) =>
            html`<span style="flex-grow: ${widths[i]}"
              >${this._legTimeLabel(leg, spans[i])}</span
            >`
        )}
      </div>
    `;
  }

  /** "H:MM (N min)" — the end time is omitted since it's always the next block's start. */
  private _legTimeLabel(leg: LegData, spanSeconds: number): string {
    if (!leg.departure_time_local) {
      return "";
    }
    const minutes = Math.round(spanSeconds / 60);
    return minutes > 0
      ? `${leg.departure_time_local} (${minutes} min)`
      : leg.departure_time_local;
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
      height: 100%;
      min-width: 4px;
      background: var(--secondary-background-color, #e0e0e0);
    }

    .segment ha-icon {
      --mdc-icon-size: 15px;
      color: #fff;
    }

    .walk-part ha-icon {
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
      display: flex;
      font-size: 0.72em;
      color: var(--secondary-text-color, #727272);
    }

    .times span {
      overflow: visible;
      white-space: nowrap;
    }
  `;
}

declare global {
  interface HTMLElementTagNameMap {
    "google-transit-journey-bar": GoogleTransitJourneyBar;
  }
}
