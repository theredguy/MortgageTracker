class MortgageCard extends HTMLElement {
  set hass(hass) {
    const config = this._config;
    if (!config) return;

    const stateObj = hass.states[config.entity];
    if (!stateObj) return;

    this.innerHTML = `
      <ha-card>
        <h1>${config.title || "Mortgage Tracker"}</h1>
        <div>Balance: £${stateObj.state}</div>
        <div>Remaining Payments: ${stateObj.attributes.remaining_payments}</div>
        <div>Interest Rate: ${stateObj.attributes.interest_rate}%</div>
        <div>Regular Payment: £${stateObj.attributes.regular_payment}</div>
        <div id="chart" style="height:200px;"></div>
      </ha-card>
    `;

    const data = stateObj.attributes.transactions.map(t => parseFloat(t.amount));
    if (window.ApexCharts) {
      new ApexCharts(this.querySelector("#chart"), {
        chart: { type: "line" },
        series: [{ name: "Payments", data: data }],
        xaxis: { categories: stateObj.attributes.transactions.map(t => t.date) }
      }).render();
    }
  }

  setConfig(config) {
    this._config = config;
  }

  getCardSize() {
    return 3;
  }
}

customElements.define("mortgage-card", MortgageCard);
