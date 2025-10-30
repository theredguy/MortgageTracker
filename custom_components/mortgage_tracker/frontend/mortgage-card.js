class MortgageCard extends HTMLElement {
  set hass(hass) {
    const entity = this.config.entity;
    const state = hass.states[entity];
    if (!state) return;

    const balance = state.state;
    const attrs = state.attributes;

    const balances = JSON.parse(attrs.balance_history || "[]");
    const projection = JSON.parse(attrs.projection || "[]");

    this.innerHTML = `
      <ha-card header="${this.config.title || 'Mortgage Tracker'}">
        <div class="card-content">
          <p><b>Balance:</b> £${balance}</p>
          <p><b>Remaining Payments:</b> ${attrs.remaining_payments}</p>
          <p><b>End Date:</b> ${attrs.estimated_end_date}</p>
          <p><b>Interest Rate:</b> ${attrs.annual_interest_rate}%</p>
          <canvas id="mortgageChart" height="120"></canvas>
        </div>
      </ha-card>
    `;

    // Draw chart
    if (window.Chart && balances.length) {
      const ctx = this.querySelector("#mortgageChart").getContext("2d");
      if (this.chart) this.chart.destroy();
      this.chart = new Chart(ctx, {
        type: "line",
        data: {
          labels: Array.from({ length: balances.length }, (_, i) => i + 1),
          datasets: [
            {
              label: "Actual Balance",
              data: balances,
              borderColor: "#4e79a7",
              fill: false,
            },
            {
              label: "Projected Balance",
              data: projection,
              borderColor: "#f28e2b",
              borderDash: [5, 5],
              fill: false,
            }
          ]
        },
        options: {
          scales: {
            y: { title: { display: true, text: "£ Balance" } },
            x: { title: { display: true, text: "Payments" } }
          },
          plugins: { legend: { position: "bottom" } },
          responsive: true,
          maintainAspectRatio: false
        }
      });
    }
  }

  setConfig(config) {
    if (!config.entity) throw new Error('Entity is required');
    this.config = config;
  }

  getCardSize() {
    return 3;
  }

  connectedCallback() {
    if (!window.Chart) {
      const script = document.createElement('script');
      script.src = "https://cdn.jsdelivr.net/npm/chart.js";
      document.head.appendChild(script);
    }
  }
}
customElements.define('mortgage-card', MortgageCard);
