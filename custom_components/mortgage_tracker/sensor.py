"""Mortgage Tracker sensor."""
from datetime import datetime, timedelta
import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import CONF_NAME

_LOGGER = logging.getLogger(__name__)

from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the Mortgage Tracker sensor."""
    sensor = MortgageSensor(hass)
    hass.data[DOMAIN]["sensor"] = sensor
    async_add_devices([sensor])

class MortgageSensor(Entity):
    """Representation of the Mortgage Tracker sensor."""

    def __init__(self, hass):
        self.hass = hass
        self._state = None
        self.balance = 200_000  # default GBP
        self.term_months = 240  # default 20 years
        self.interest_rate = 3.5  # annual %
        self.regular_payment = 1000  # default monthly payment
        self.payment_day = 1
        self.transactions = []  # {"amount": X, "date": YYYY-MM-DD}
        self.last_update = None

    @property
    def name(self):
        return "Mortgage Tracker"

    @property
    def state(self):
        return round(self.balance, 2)

    @property
    def unit_of_measurement(self):
        return "£"

    @property
    def extra_state_attributes(self):
        return {
            "term_months": self.term_months,
            "interest_rate": self.interest_rate,
            "regular_payment": self.regular_payment,
            "payment_day": self.payment_day,
            "payments_remaining": self._calculate_payments_remaining(),
            "last_update": self.last_update,
            "transactions": self.transactions,
            "chart_data": self._get_chart_data(),
        }

    def _calculate_payments_remaining(self):
        if self.regular_payment == 0:
            return None
        return max(0, int(self.balance / self.regular_payment))

    def _get_chart_data(self):
        # Returns list of balances after each transaction for charting
        chart = []
        bal = self.balance
        for tx in sorted(self.transactions, key=lambda x: x["date"]):
            bal -= tx["amount"]
            chart.append({"date": tx["date"], "balance": round(bal, 2)})
        return chart

    async def add_payment(self, amount, date=None):
        """Add past or extra payment."""
        if not date:
            date = datetime.today().strftime("%Y-%m-%d")
        self.transactions.append({"amount": amount, "date": date})
        self.balance -= amount
        self.last_update = datetime.now().isoformat()
        self.async_write_ha_state()

    async def set_interest_rate(self, rate):
        """Set interest rate in percent."""
        self.interest_rate = rate
        self.last_update = datetime.now().isoformat()
        self.async_write_ha_state()

    async def reset_mortgage(self, balance, term):
        """Reset balance and term."""
        self.balance = balance
        self.term_months = term
        self.transactions = []
        self.last_update = datetime.now().isoformat()
        self.async_write_ha_state()

    async def set_regular_payment(self, amount):
        """Set monthly regular payment."""
        self.regular_payment = amount
        self.last_update = datetime.now().isoformat()
        self.async_write_ha_state()

    async def set_payment_day(self, day):
        """Set automatic update day of month."""
        self.payment_day = day
        self.last_update = datetime.now().isoformat()
        self.async_write_ha_state()

    async def async_update(self):
        """Monthly automatic update."""
        today = datetime.today()
        if today.day == self.payment_day:
            # Apply interest
            monthly_interest = (self.interest_rate / 100) / 12 * self.balance
            self.balance += monthly_interest
            # Apply regular payment
            payment = min(self.regular_payment, self.balance)
            self.balance -= payment
            self.transactions.append({
                "amount": payment,
                "date": today.strftime("%Y-%m-%d")
            })
            self.last_update = datetime.now().isoformat()
