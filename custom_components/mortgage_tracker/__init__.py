import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery

from . import services
from .sensor import MortgageSensor

_LOGGER = logging.getLogger(__name__)
DOMAIN = "mortgage_tracker"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up Mortgage Tracker integration."""

    # Auto-create input_number helpers if missing
    helpers = [
        {"name": "Mortgage Payment Amount", "entity_id": "input_number.mortgage_payment_amount", "min": 0, "max": 100000, "step": 1, "unit_of_measurement": "£"},
        {"name": "Mortgage Interest Rate", "entity_id": "input_number.mortgage_interest_rate", "min": 0, "max": 20, "step": 0.1, "unit_of_measurement": "%"},
        {"name": "Regular Monthly Payment", "entity_id": "input_number.mortgage_regular_payment", "min": 0, "max": 100000, "step": 1, "unit_of_measurement": "£"}
    ]

    for h in helpers:
        if h["entity_id"] not in hass.states:
            await hass.services.async_call(
                "input_number",
                "create",
                {
                    "name": h["name"],
                    "min": h["min"],
                    "max": h["max"],
                    "step": h["step"],
                    "unit_of_measurement": h["unit_of_measurement"],
                    "mode": "box",
                }
            )

       # Register services
    hass.services.async_register(DOMAIN, "add_payment", lambda call: hass.async_create_task(
        mortgage_sensor.add_payment(
            amount=call.data.get("amount"),
            date=call.data.get("date")
        )
    ))

    hass.services.async_register(DOMAIN, "edit_payment", lambda call: hass.async_create_task(
        mortgage_sensor.edit_payment(
            index=call.data.get("index"),
            new_amount=call.data.get("new_amount")
        )
    ))

    hass.services.async_register(DOMAIN, "set_interest_rate", lambda call: hass.async_create_task(
        mortgage_sensor.set_interest_rate(
            rate=call.data.get("rate")
        )
    ))

    hass.services.async_register(DOMAIN, "reset_mortgage", lambda call: hass.async_create_task(
        mortgage_sensor.reset_mortgage(
            balance=call.data.get("balance"),
            term=call.data.get("term")
        )
    ))

    hass.services.async_register(DOMAIN, "set_regular_payment", lambda call: hass.async_create_task(
        mortgage_sensor.set_regular_payment(
            amount=call.data.get("amount")
        )
    ))

    hass.services.async_register(DOMAIN, "set_payment_day", lambda call: hass.async_create_task(
        mortgage_sensor.set_payment_day(
            day=call.data.get("day")
        )
    ))
    _LOGGER.info("Mortgage Tracker integration setup complete with all services.")

    # Load sensor
    await discovery.async_load_platform(hass, "sensor", DOMAIN, {}, config)

    return True
