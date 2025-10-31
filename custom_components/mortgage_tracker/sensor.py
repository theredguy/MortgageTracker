
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
