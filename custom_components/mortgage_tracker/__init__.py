"""Mortgage Tracker integration."""
from homeassistant.core import HomeAssistant
from .sensor import MortgageSensor
from .const import DOMAIN

DOMAIN = "mortgage_tracker"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Mortgage Tracker component."""
    hass.data.setdefault(DOMAIN, {})

    # Register services
    async def handle_add_payment(call):
        sensor: MortgageSensor = hass.data[DOMAIN]["sensor"]
        await sensor.add_payment(call.data.get("amount"), call.data.get("date"))

    async def handle_set_interest_rate(call):
        sensor: MortgageSensor = hass.data[DOMAIN]["sensor"]
        await sensor.set_interest_rate(call.data.get("rate"))

    async def handle_reset_mortgage(call):
        sensor: MortgageSensor = hass.data[DOMAIN]["sensor"]
        await sensor.reset_mortgage(call.data.get("balance"), call.data.get("term"))

    async def handle_set_regular_payment(call):
        sensor: MortgageSensor = hass.data[DOMAIN]["sensor"]
        await sensor.set_regular_payment(call.data.get("amount"))

    async def handle_set_payment_day(call):
        sensor: MortgageSensor = hass.data[DOMAIN]["sensor"]
        await sensor.set_payment_day(call.data.get("day"))

    hass.services.async_register(DOMAIN, "add_payment", handle_add_payment)
    hass.services.async_register(DOMAIN, "set_interest_rate", handle_set_interest_rate)
    hass.services.async_register(DOMAIN, "reset_mortgage", handle_reset_mortgage)
    hass.services.async_register(DOMAIN, "set_regular_payment", handle_set_regular_payment)
    hass.services.async_register(DOMAIN, "set_payment_day", handle_set_payment_day)

    return True

async def async_setup_entry(hass, entry, async_add_devices):
    """Set up sensor entry."""
    from .sensor import async_setup_entry as sensor_setup
    await sensor_setup(hass, entry, async_add_devices)
