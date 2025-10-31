
class MortgageCard extends HTMLElement {
  set hass(hass) {
    const entityId = this.config.entity;
    const state = hass.states[entityId];
    this.innerHTML = `
      <ha-card>
        <h1>${this.config.title || "Mortgage"}</h1>
        <p>Balance: £${state.state}</p>
        <p>Remaining Payments: ${state.attributes.remaining_payments}</p>
        <p>Interest Rate: ${state.attributes.interest_rate}%</p>
        <p>End Date: ${state.attributes.end_date}</p>
      </ha-card>
    `;
  }

  setConfig(config) {
    this.config = config;
  }

  static getConfigElement() {
    return document.createElement("div");
  }
}

customElements.define("mortgage-card", MortgageCard);
