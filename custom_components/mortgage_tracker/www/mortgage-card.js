class MortgageCard extends HTMLElement {
  set hass(hass) {
    const entityId = this.config.entity;
    const stateObj = hass.states[entityId];
    if (!stateObj) return;

    const balance = parseFloat(stateObj.state);
    const attrs = stateObj.attributes;
    const chartData = attrs.chart_data || [];
    const transactions = attrs.transactions || [];

    // Prepare chart data
    const series = [{
      name: 'Balance',
      data: chartData.map(item => [new Date(item.date).getTime(), item.balance])
    }];

    const options = {
      chart: { type: 'line', height: 250 },
      series: series,
      xaxis: { type: 'datetime' },
      yaxis: { title: { text: 'Balance (£)' } },
      title: { text: 'Mortgage Balance Over Time', align: 'center' }
    };

    // Render card
    this.innerHTML = `
      <ha-card>
        <h1>Mortgage Tracker</h1>
        <p><b>Current Balance:</b> £${balance.toFixed(2)}</p>
        <p><b>Payments Remaining:</b> ${attrs.payments_remaining}</p>
        <p><b>Interest Rate:</b> ${attrs.interest_rate}%</p>

        <div id="mortgage-chart"></div>

        <h3>Regular Payment Settings</h3>
        <input type="number" id="regular-amount" placeholder="Amount (£)" value="${attrs.regular_payment || ''}">
        <input type="number" id="payment-day" min="1" max="28" placeholder="Day of Month" value="${attrs.payment_day || ''}">
        <button id="set-regular-btn">Set Regular Payment</button>

        <h3>Add Transaction</h3>
        <input type="number" id="new-amount" placeholder="Amount (£)">
        <input type="date" id="new-date">
        <button id="add-btn">Add Payment</button>

        <h3>Edit Transactions</h3>
        <ul>
          ${transactions.map((tx, index) => `
            <li>
              ${tx.date}: £${tx.amount.toFixed(2)}
              <input type="number" id="edit-${index}" placeholder="New Amount">
              <button data-index="${index}" class="edit-btn">Update</button>
            </li>
          `).join('')}
        </ul>
      </ha-card>
    `;

    // Initialize chart
    if (!this.chart) {
      this.chart = new ApexCharts(this.querySelector("#mortgage-chart"), options);
      this.chart.render();
    } else {
      this.chart.updateOptions(options);
    }

    // Add transaction
    this.querySelector("#add-btn").addEventListener("click", () => {
      const amount = parseFloat(this.querySelector("#new-amount").value);
      const date = this.querySelector("#new-date").value || new Date().toISOString().slice(0,10);
      if (amount) {
        hass.callService("mortgage_tracker", "add_payment", { amount, date });
      }
    });

    // Edit transaction
    this.querySelectorAll(".edit-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const index = parseInt(btn.dataset.index);
        const newAmount = parseFloat(this.querySelector(`#edit-${index}`).value);
        if (!isNaN(newAmount)) {
          hass.callService("mortgage_tracker", "edit_payment", { index, amount: newAmount });
        }
      });
    });

    // Set regular payment
    this.querySelector("#set-regular-btn").addEventListener("click", () => {
      const amount = parseFloat(this.querySelector("#regular-amount").value);
      const day = parseInt(this.querySelector("#payment-day").value);
      if (!isNaN(amount) && day >= 1 && day <= 28) {
        hass.callService("mortgage_tracker", "set_regular_payment", { amount, day });
      }
    });
  }

  setConfig(config) {
    if (!config.entity) throw new Error("You must define an entity");
    this.config = config;
  }

  getCardSize() {
    return 6;
  }
}

customElements.define('mortgage-card', MortgageCard);
