from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import entity_platform
from homeassistant.helpers import entity_component
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config):
    """Set up the Mortgage Tracker integration."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry):
    """Set up from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Forward setup to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    # -----------------------------------------------------------------
    # 1️⃣ Create the input_number helpers if missing
    # -----------------------------------------------------------------
    # These helpers let the user enter a payment and interest rate
    async def ensure_helper(domain, object_id, name, min_value, max_value, step, unit):
        if f"{domain}.{object_id}" not in hass.states.async_entity_ids():
            await hass.services.async_call(
                "input_number",
                "set_value",
                {"entity_id": f"{domain}.{object_id}", "value": 0},
                blocking=False,
            )

    # Make sure input_numbers exist (note: HA will automatically persist them)
    if "input_number.mortgage_payment_amount" not in hass.states.async_entity_ids():
        hass.async_create_task(
            hass.services.async_call(
                "input_number",
                "create",
                {
                    "object_id": "mortgage_payment_amount",
                    "name": "Payment Amount",
                    "min": 0,
                    "max": 10000,
                    "step": 100,
                    "unit_of_measurement": "£",
                },
            )
        )

    if "input_number.mortgage_interest_rate" not in hass.states.async_entity_ids():
        hass.async_create_task(
            hass.services.async_call(
                "input_number",
                "create",
                {
                    "object_id": "mortgage_interest_rate",
                    "name": "Interest Rate",
                    "min": 0,
                    "max": 10,
                    "step": 0.1,
                    "unit_of_measurement": "%",
                },
            )
        )

    # -----------------------------------------------------------------
    # 2️⃣ Register services
    # -----------------------------------------------------------------
    async def handle_add_payment(call: ServiceCall):
        """Handle adding an extra payment."""
        amount = call.data.get("amount")
        for entity in hass.data[DOMAIN].values():
            await entity.add_payment(amount)

    async def handle_set_interest(call: ServiceCall):
        """Handle updating the interest rate."""
        rate = call.data.get("rate")
        for entity in hass.data[DOMAIN].values():
            await entity.set_interest_rate(rate)

    hass.services.async_register(DOMAIN, "add_additional_payment", handle_add_payment)
    hass.services.async_register(DOMAIN, "set_interest_rate", handle_set_interest)

    return True
