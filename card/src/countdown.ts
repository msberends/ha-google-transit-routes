import { LitElement, html, css } from "lit";
import { customElement, property, state } from "lit/decorators.js";

/**
 * Live-ticking "arrives in X min" countdown. Purely client-side (setInterval),
 * so it never triggers a sensor poll or API call.
 */
@customElement("google-transit-countdown")
export class GoogleTransitCountdown extends LitElement {
  @property({ attribute: false }) public arrival?: string;
  @property({ attribute: false }) public language = "en";

  @state() private _now = Date.now();
  private _interval?: number;

  public connectedCallback(): void {
    super.connectedCallback();
    this._interval = window.setInterval(() => {
      this._now = Date.now();
    }, 1000);
  }

  public disconnectedCallback(): void {
    super.disconnectedCallback();
    if (this._interval !== undefined) {
      window.clearInterval(this._interval);
      this._interval = undefined;
    }
  }

  private _format(seconds: number): string {
    const nl = this.language === "nl";
    if (seconds <= 0) {
      return nl ? "vertrokken" : "departed";
    }
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const prefix = nl ? "over" : "in";
    const hourUnit = nl ? "u" : "h";
    const minuteUnit = nl ? "min" : "min";
    if (hours > 0) {
      return `${prefix} ${hours}${hourUnit} ${minutes}m`;
    }
    return `${prefix} ${minutes} ${minuteUnit}`;
  }

  protected render() {
    if (!this.arrival) {
      return html``;
    }
    const arrivalMs = new Date(this.arrival).getTime();
    if (Number.isNaN(arrivalMs)) {
      return html``;
    }
    const seconds = Math.round((arrivalMs - this._now) / 1000);
    return html`<span class="countdown ${seconds <= 0 ? "departed" : ""}"
      >${this._format(seconds)}</span
    >`;
  }

  static styles = css`
    .countdown {
      font-weight: 600;
    }
    .departed {
      opacity: 0.6;
    }
  `;
}

declare global {
  interface HTMLElementTagNameMap {
    "google-transit-countdown": GoogleTransitCountdown;
  }
}
