from homeassistant.core import HomeAssistant
from .sensor import MortgageSensor
from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass, entry, async_add_devices):
    data = entry.data
    sensor = MortgageSensor(
        hass,
        balance=data.get("balance", 200000),
        term_months=data.get("term_months", 240),
        interest_rate=data.get("interest_rate", 3.5),
        regular_payment=data.get("regular_payment", 1000),
        payment_day=data.get("payment_day", 1)
    )
    hass.data.setdefault(DOMAIN, {})["sensor"] = sensor
    async_add_devices([sensor])

    # Register services
    async def handle_add_payment(call):
        await sensor.add_payment(call.data.get("amount"), call.data.get("date"))

    async def handle_edit_payment(call):
        await sensor.edit_payment(call.data.get("index"), call.data.get("amount"))

    async def handle_set_interest_rate(call):
        await sensor.set_interest_rate(call.data.get("rate"))

    async def handle_reset_mortgage(call):
        await sensor.reset_mortgage(call.data.get("balance"), call.data.get("term"))

    async def handle_set_regular_payment(call):
        await sensor.set_regular_payment(call.data.get("amount"))

    async def handle_set_payment_day(call):
        await sensor.set_payment_day(call.data.get("day"))

    hass.services.async_register(DOMAIN, "add_payment", handle_add_payment)
    hass.services.async_register(DOMAIN, "edit_payment", handle_edit_payment)
    hass.services.async_register(DOMAIN, "set_interest_rate", handle_set_interest_rate)
    hass.services.async_register(DOMAIN, "reset_mortgage", handle_reset_mortgage)
    hass.services.async_register(DOMAIN, "set_regular_payment", handle_set_regular_payment)
    hass.services.async_register(DOMAIN, "set_payment_day", handle_set_payment_day)

    return True
