from datetime import datetime, timedelta
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN
import json

class MortgageTracker(SensorEntity):
    def __init__(self, config):
        self._attr_name = "Mortgage Tracker"
        self.principal = config["principal"]
        self.annual_interest_rate = config["annual_interest_rate"] / 100
        self.term_years = config["term_years"]
        self.monthly_payment = config["monthly_payment"]
        self.start_date = datetime.now()
        self.extra_payments = 0.0
        self.balance_history = []
        self.update_metrics()

    def project_balance(self):
        balances = []
        monthly_rate = self.annual_interest_rate / 12
        balance = self.principal
        for i in range(self.term_years * 12):
            interest = balance * monthly_rate
            balance += interest - self.monthly_payment
            balance = max(balance, 0)
            balances.append(round(balance, 2))
            if balance <= 0:
                break
        return balances

    def update_metrics(self):
        monthly_rate = self.annual_interest_rate / 12
        n = self.term_years * 12
        self.balance = self.principal
        payments = 0
        while self.balance > 0 and payments < n:
            interest = self.balance * monthly_rate
            self.balance += interest - self.monthly_payment - self.extra_payments
            if self.balance < 0:
                self.balance = 0
            payments += 1
        self.remaining_payments = payments
        self.end_date = self.start_date + timedelta(days=payments * 30)
        self.balance_history.append(self.balance)

    @property
    def native_value(self):
        return round(self.balance, 2)

    @property
    def extra_state_attributes(self):
        return {
            "currency": "GBP",
            "remaining_payments": self.remaining_payments,
            "estimated_end_date": self.end_date.strftime("%Y-%m-%d"),
            "annual_interest_rate": round(self.annual_interest_rate * 100, 2),
            "monthly_payment": self.monthly_payment,
            "balance_history": json.dumps(self.balance_history[-120:]),
            "projection": json.dumps(self.project_balance())
        }

    async def async_added_to_hass(self):
        self.hass.services.async_register(DOMAIN, "make_extra_payment", self.handle_extra_payment)
        self.hass.services.async_register(DOMAIN, "change_interest_rate", self.handle_interest_rate_change)
        self.hass.services.async_register(DOMAIN, "set_outstanding_balance", self.handle_set_balance)

    async def handle_extra_payment(self, call):
        amount = call.data.get("amount", 0)
        self.extra_payments += amount
        self.update_metrics()
        self.async_write_ha_state()

    async def handle_interest_rate_change(self, call):
        rate = call.data.get("new_rate", self.annual_interest_rate * 100)
        self.annual_interest_rate = rate / 100
        self.update_metrics()
        self.async_write_ha_state()

    async def handle_set_balance(self, call):
        new_balance = call.data.get("new_balance", self.balance)
        self.principal = new_balance
        self.update_metrics()
        self.async_write_ha_state()
