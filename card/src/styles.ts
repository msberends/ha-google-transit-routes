import { css } from "lit";

export const cardStyles = css`
  :host {
    display: block;
  }

  ha-card {
    padding: 16px;
  }

  .card-content {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .card-content.compact {
    gap: 8px;
  }

  .route-row {
    cursor: pointer;
    padding: 12px 16px;
    border-radius: 12px;
    background: var(--ha-card-background, var(--card-background-color, #fff));
    border: 1px solid var(--divider-color, #e0e0e0);
    transition: opacity 0.3s ease;
  }

  .compact .route-row {
    padding: 8px 12px;
  }

  .route-row.departed {
    opacity: 0.4;
  }

  .route-row.unavailable {
    opacity: 0.6;
    font-style: italic;
  }

  .route-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1.3em;
    font-weight: 600;
    color: var(--primary-text-color);
  }

  .compact .route-header {
    font-size: 1.05em;
  }

  .route-header ha-icon {
    color: var(--state-icon-color, var(--paper-item-icon-color, #44739e));
    --mdc-icon-size: 28px;
  }

  .route-name {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .arrival {
    font-size: 0.85em;
    color: var(--secondary-text-color);
    white-space: nowrap;
  }

  .route-sub {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 1.15em;
    margin-top: 2px;
  }

  .compact .route-sub {
    font-size: 0.95em;
  }

  .expand-arrow {
    color: var(--secondary-text-color);
    transition: transform 0.2s ease;
  }

  .expand-arrow.open {
    transform: rotate(180deg);
  }

  .alternatives {
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px dashed var(--divider-color, #e0e0e0);
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 0.9em;
    color: var(--secondary-text-color);
  }

  .alternative-row {
    display: flex;
    justify-content: space-between;
    gap: 8px;
  }

  .alt-legs {
    font-weight: 600;
    white-space: nowrap;
  }

  .attribution {
    text-align: right;
    font-size: 0.7em;
    color: var(--disabled-text-color, #999);
    padding: 4px 4px 0 0;
  }

  /* Explicit theme overrides for theme: "light" / "dark" (theme: "auto" just
     inherits the ambient Home Assistant theme variables, no override needed). */
  :host(.force-light) {
    --card-background-color: #ffffff;
    --primary-text-color: #212121;
    --secondary-text-color: #727272;
    --divider-color: #e0e0e0;
    --disabled-text-color: #9e9e9e;
  }

  :host(.force-dark) {
    --card-background-color: #1c1c1c;
    --primary-text-color: #e1e1e1;
    --secondary-text-color: #a3a3a3;
    --divider-color: #383838;
    --disabled-text-color: #6c6c6c;
  }
`;
