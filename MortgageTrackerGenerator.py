import zipfile

zip_filename = "mortgage_tracker_hacs.zip"

files = {
    "custom_components/mortgage_tracker/__init__.py": """
from homeassistant.core import HomeAssistant
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry):
    hass.data.setdefault(DOMAIN, {})
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True
""",
    "custom_components/mortgage_tracker/manifest.json": """
{
  "domain": "mortgage_tracker",
  "name": "Mortgage Tracker",
  "version": "1.4.0",
  "documentation": "https://github.com/yourusername/mortgage-tracker",
  "requirements": [],
  "dependencies": [],
  "codeowners": ["@yourusername"],
  "config_flow": true
}
""",
    "custom_components/mortgage_tracker/const.py": 'DOMAIN = "mortgage_tracker"',
    "custom_components/mortgage_tracker/sensor.py": """
from homeassistant.helpers.entity import Entity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([MortgageSensor(hass)])

class MortgageSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._state = None
        self._attr_extra_state_attributes = {
            "remaining_payments": 0,
            "end_date": None,
            "balance": 0,
            "interest_rate": 0
        }
        self.balance = 200000
        self.interest_rate = 3.5
        self.monthly_payment = 1000
        self.remaining_payments = 240

    @property
    def name(self):
        return "Mortgage Tracker"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attr_extra_state_attributes

    async def async_update(self):
        self._state = round(self.balance, 2)
        self._attr_extra_state_attributes.update({
            "remaining_payments": self.remaining_payments,
            "end_date": "2045-10-31",
            "interest_rate": self.interest_rate
        })

    async def add_payment(self, amount):
        self.balance -= amount
        self.remaining_payments = max(0, self.remaining_payments - 1)
        await self.async_update()

    async def set_interest_rate(self, rate):
        self.interest_rate = rate
        await self.async_update()
""",
    "custom_components/mortgage_tracker/config_flow.py": """
from homeassistant import config_entries
from .const import DOMAIN

class MortgageConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        return self.async_create_entry(title="Mortgage Tracker", data={})
""",
    "custom_components/mortgage_tracker/services.yaml": """
add_additional_payment:
  description: "Add an extra payment to the mortgage"
  fields:
    amount:
      description: "Payment amount in GBP"
      example: 500

set_interest_rate:
  description: "Change the mortgage interest rate"
  fields:
    rate:
      description: "New interest rate in %"
      example: 3.5
""",
    "www/mortgage-card.js": """
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
""",
    "hacs.json": """
{
  "name": "Mortgage Tracker",
  "content_in_root": false,
  "domains": ["integration", "lovelace"],
  "homeassistant": "2023.1.0",
  "hacs": "1.0.0",
  "zip_release": false
}
""",
    "README.md": "# Mortgage Tracker HACS Integration\n\nIntegration to track mortgage payments with a custom Lovelace card."
}

with zipfile.ZipFile(zip_filename, "w") as zipf:
    for path, content in files.items():
        zipf.writestr(path, content)

print(f"Created {zip_filename}")
