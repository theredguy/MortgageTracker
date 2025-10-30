"""Mortgage Tracker HACS integration (YAML-based)."""

from homeassistant.core import HomeAssistant
from datetime import date
from .services import setup_services, compute_amortization_schedule

DOMAIN = "mortgage_tracker"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the mortgage tracker integration."""

    conf = config.get(DOMAIN, {})
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["config"] = conf

    # Initialize extra payments and outstanding balance storage
    hass.data[DOMAIN].setdefault("extra_payments", [])
    hass.data[DOMAIN].setdefault("outstanding_balance", conf.get("principal", 300000))

    # Compute initial amortization schedule
    def _compute_schedule():
        return compute_amortization_schedule(
            principal=float(conf.get("principal", 300000)),
            annual_interest_rate=float(conf.get("annual_interest_rate", 3.25)),
            term_years=int(conf.get("term_years", 30)),
            start_date=conf.get("start_date", date.today().isoformat()),
            extra_payments=hass.data[DOMAIN]["extra_payments"],
            outstanding=hass.data[DOMAIN]["outstanding_balance"]
        )

    hass.data[DOMAIN]["schedule"] = _compute_schedule()

    # Register services to manipulate mortgage
    setup_services(hass)

    # Load sensors via discovery (YAML-friendly)
    hass.async_create_task(
        hass.helpers.discovery.async_load_platform("sensor", DOMAIN, {}, config)
    )

    return True
