from homeassistant.helpers.entity import Entity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the mortgage tracker sensor."""
    sensor = MortgageSensor(hass)
    async_add_entities([sensor])
    hass.data[DOMAIN]["sensor"] = sensor  # store for service access

class MortgageSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self.balance = 200000.0
        self.interest_rate = 3.5
        self.remaining_payments = 240
        self._attr_name = "Mortgage Tracker"

    @property
    def state(self):
        return round(self.balance, 2)

    @property
    def extra_state_attributes(self):
        return {
            "remaining_payments": self.remaining_payments,
            "end_date": "2045-10-31",
            "interest_rate": self.interest_rate,
        }

    async def add_payment(self, amount):
        """Reduce balance and recalculate remaining payments."""
        self.balance = max(0, self.balance - float(amount))
        self.remaining_payments = max(0, self.remaining_payments - 1)
        self.async_write_ha_state()

    async def set_interest_rate(self, rate):
        """Set new interest rate."""
        self.interest_rate = float(rate)
        self.async_write_ha_state()
