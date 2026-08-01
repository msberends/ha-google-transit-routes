import { LitElement, html, css } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import type { EntityConfig, GoogleTransitRoutesCardConfig, HomeAssistant } from "./types";

const DEFAULTS: Partial<GoogleTransitRoutesCardConfig> = {
  show_alternatives: true,
  show_legs: true,
  show_countdown: true,
  refresh_interval: 0,
  theme: "auto",
  compact: false,
};

/** Visual config editor so the card can be set up without hand-writing YAML. */
@customElement("google-transit-routes-card-editor")
export class GoogleTransitRoutesCardEditor extends LitElement {
  @property({ attribute: false }) public hass?: HomeAssistant;

  @state() private _config?: GoogleTransitRoutesCardConfig;

  public setConfig(config: GoogleTransitRoutesCardConfig): void {
    this._config = { ...DEFAULTS, ...config };
  }

  private _fireChanged(config: GoogleTransitRoutesCardConfig): void {
    this._config = config;
    this.dispatchEvent(
      new CustomEvent("config-changed", {
        detail: { config },
        bubbles: true,
        composed: true,
      })
    );
  }

  private _valueChanged(ev: Event): void {
    if (!this._config) {
      return;
    }
    const target = ev.target as HTMLInputElement & { configValue?: string };
    const key = target.configValue;
    if (!key) {
      return;
    }
    let value: unknown =
      target.type === "checkbox" ? target.checked : target.value;
    if (key === "refresh_interval") {
      value = Number(value) || 0;
    }
    this._fireChanged({ ...this._config, [key]: value });
  }

  private _themeChanged(ev: Event): void {
    if (!this._config) {
      return;
    }
    const value = (ev.target as HTMLSelectElement).value as
      | "auto"
      | "light"
      | "dark";
    this._fireChanged({ ...this._config, theme: value });
  }

  private _entityChanged(
    index: number,
    key: keyof EntityConfig,
    value: string
  ): void {
    if (!this._config) {
      return;
    }
    const entities = [...this._config.entities];
    entities[index] = { ...entities[index], [key]: value };
    this._fireChanged({ ...this._config, entities });
  }

  private _addEntity(): void {
    if (!this._config) {
      return;
    }
    const entities = [...(this._config.entities || []), { entity: "" }];
    this._fireChanged({ ...this._config, entities });
  }

  private _removeEntity(index: number): void {
    if (!this._config) {
      return;
    }
    const entities = this._config.entities.filter((_, i) => i !== index);
    this._fireChanged({ ...this._config, entities });
  }

  protected render() {
    if (!this._config || !this.hass) {
      return html``;
    }

    return html`
      <div class="card-config">
        <ha-textfield
          label="Title"
          .value=${this._config.title || ""}
          .configValue=${"title"}
          @input=${this._valueChanged}
        ></ha-textfield>

        <h3>Routes</h3>
        ${this._config.entities.map(
          (entityConf, index) => html`
            <div class="entity-row">
              <ha-entity-picker
                .hass=${this.hass}
                .value=${entityConf.entity}
                .includeDomains=${["sensor"]}
                @value-changed=${(e: CustomEvent) =>
                  this._entityChanged(index, "entity", e.detail.value)}
              ></ha-entity-picker>
              <ha-textfield
                label="Name"
                .value=${entityConf.name || ""}
                @input=${(e: Event) =>
                  this._entityChanged(
                    index,
                    "name",
                    (e.target as HTMLInputElement).value
                  )}
              ></ha-textfield>
              <ha-icon-picker
                label="Icon (optional)"
                .hass=${this.hass}
                .value=${entityConf.icon || ""}
                @value-changed=${(e: CustomEvent) =>
                  this._entityChanged(index, "icon", e.detail.value)}
              ></ha-icon-picker>
              <ha-icon-button
                .path=${"M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z"}
                @click=${() => this._removeEntity(index)}
              ></ha-icon-button>
            </div>
          `
        )}
        <mwc-button @click=${this._addEntity}>+ Add route</mwc-button>

        <h3>Display options</h3>
        <div class="switch-row">
          <ha-formfield label="Show alternative routes">
            <ha-switch
              .checked=${this._config.show_alternatives ?? true}
              .configValue=${"show_alternatives"}
              @change=${this._valueChanged}
            ></ha-switch>
          </ha-formfield>
          <ha-formfield label="Show journey bar (legs)">
            <ha-switch
              .checked=${this._config.show_legs ?? true}
              .configValue=${"show_legs"}
              @change=${this._valueChanged}
            ></ha-switch>
          </ha-formfield>
          <ha-formfield label="Show live countdown">
            <ha-switch
              .checked=${this._config.show_countdown ?? true}
              .configValue=${"show_countdown"}
              @change=${this._valueChanged}
            ></ha-switch>
          </ha-formfield>
          <ha-formfield label="Compact mode">
            <ha-switch
              .checked=${this._config.compact ?? false}
              .configValue=${"compact"}
              @change=${this._valueChanged}
            ></ha-switch>
          </ha-formfield>
        </div>

        <ha-textfield
          label="Refresh interval in seconds (0 = off, no automatic API calls)"
          helper="Each refresh calls the Google Routes API for every route on this card. Leave at 0 unless you understand the quota cost — see the API quota section in the README."
          helper-persistent
          type="number"
          .value=${String(this._config.refresh_interval ?? 0)}
          .configValue=${"refresh_interval"}
          @input=${this._valueChanged}
        ></ha-textfield>

        <label class="theme-label">
          Theme
          <select .value=${this._config.theme || "auto"} @change=${this._themeChanged}>
            <option value="auto">Auto (follow Home Assistant theme)</option>
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </select>
        </label>
      </div>
    `;
  }

  static styles = css`
    .card-config {
      display: flex;
      flex-direction: column;
      gap: 12px;
      padding: 8px 0;
    }
    h3 {
      margin: 8px 0 0;
      font-size: 1em;
      color: var(--secondary-text-color);
    }
    .entity-row {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .entity-row ha-entity-picker {
      flex: 2;
    }
    .entity-row ha-textfield {
      flex: 1;
    }
    .switch-row {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .theme-label {
      display: flex;
      flex-direction: column;
      gap: 4px;
      font-size: 0.9em;
      color: var(--secondary-text-color);
    }
  `;
}

declare global {
  interface HTMLElementTagNameMap {
    "google-transit-routes-card-editor": GoogleTransitRoutesCardEditor;
  }
}
