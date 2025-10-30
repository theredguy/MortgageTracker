from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

@config_entries.HANDLERS.register(DOMAIN)
class MortgageTrackerFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="Mortgage Tracker", data=user_input)

        schema = vol.Schema({
            vol.Required("principal"): float,
            vol.Required("annual_interest_rate"): float,
            vol.Required("term_years"): int,
            vol.Required("monthly_payment"): float
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
