from datetime import datetime, timedelta
from homeassistant.helpers.entity import Entity
from .const import DOMAIN

class MortgageSensor(Entity):
    def __init__(self, hass, balance=200000, term_months=240, interest_rate=3.5,
                 regular_payment=1000, payment_day=1):
        self.hass = hass
        self.balance = balance
        self.term_months = term_months
        self.interest_rate = interest_rate
        self.regular_payment = regular_payment
        self.payment_day = payment_day
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
            "end_date": self._calculate_end_date().strftime("%Y-%m-%d") if self._calculate_end_date() else None,
            "last_update": self.last_update,
            "transactions": self.transactions,
            "chart_data": self._get_chart_data(),
        }

    def _calculate_payments_remaining(self):
        if self.regular_payment <= 0:
            return None
        return max(0, int(self.balance / self.regular_payment))

    def _calculate_end_date(self):
        remaining = self._calculate_payments_remaining()
        if remaining is None:
            return None
        today = datetime.today()
        months = remaining
        end_month = (today.month + months - 1) % 12 + 1
        end_year = today.year + ((today.month + months - 1) // 12)
        try:
            return datetime(end_year, end_month, self.payment_day)
        except:
            return datetime(end_year, end_month, 1)

    def _get_chart_data(self):
        chart = []
        bal = self.balance
        for tx in sorted(self.transactions, key=lambda x: x["date"]):
            bal -= tx["amount"]
            chart.append({"date": tx["date"], "balance": round(bal, 2)})
        return chart

    async def add_payment(self, amount, date=None):
        """Add a payment (past or future)."""
        if not date:
            date = datetime.today().strftime("%Y-%m-%d")
        self.transactions.append({"amount": amount, "date": date})
        self.balance -= amount
        self.last_update = datetime.now().isoformat()
        self.async_write_ha_state()

    async def edit_payment(self, index, new_amount):
        """Edit an existing payment."""
        if 0 <= index < len(self.transactions):
            old_amount = self.transactions[index]["amount"]
            self.transactions[index]["amount"] = new_amount
            self.balance += old_amount - new_amount
            self.last_update = datetime.now().isoformat()
            self.async_write_ha_state()

    async def set_interest_rate(self, rate):
        self.interest_rate = rate
        self.last_update = datetime.now().isoformat()
        self.async_write_ha_state()

    async def reset_mortgage(self, balance=None, term=None):
        self.balance = balance if balance else 200000
        self.term_months = term if term else 240
        self.transactions = []
        self.last_update = datetime.now().isoformat()
        self.async_write_ha_state()

    async def set_regular_payment(self, amount):
        self.regular_payment = amount
        self.last_update = datetime.now().isoformat()
        self.async_write_ha_state()

    async def set_payment_day(self, day):
        self.payment_day = day
        self.last_update = datetime.now().isoformat()
        self.async_write_ha_state()

    async def async_update(self):
        """Apply automatic monthly interest and regular payment."""
        today = datetime.today()
        last_update_day = self.last_update and datetime.fromisoformat(self.last_update).day

        # Only apply once per payment day
        if today.day == self.payment_day and today.day != last_update_day:
            monthly_interest = (self.interest_rate / 100) / 12 * self.balance
            self.balance += monthly_interest

            payment = min(self.regular_payment, self.balance)
            self.balance -= payment
            self.transactions.append({
                "amount": payment,
                "date": today.strftime("%Y-%m-%d")
            })
            self.last_update = datetime.now().isoformat()
            self.async_write_ha_state()
