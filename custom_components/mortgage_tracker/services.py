from homeassistant.core import ServiceCall

# In-memory storage for demonstration
MORTGAGE_DATA = {
    "balance": 200000,
    "interest_rate": 3.5,
    "payments": [],
    "regular_payment": 1000,
    "payment_day": 1,
}

async def handle_add_payment(call: ServiceCall):
    """Add a payment."""
    amount = call.data.get("amount")
    date = call.data.get("date")
    if amount is not None and date:
        MORTGAGE_DATA["payments"].append({"amount": amount, "date": date})

async def handle_edit_payment(call: ServiceCall):
    """Edit an existing payment."""
    index = call.data.get("index")
    amount = call.data.get("amount")
    if index is not None and 0 <= index < len(MORTGAGE_DATA["payments"]):
        if amount is not None:
            MORTGAGE_DATA["payments"][index]["amount"] = amount

async def handle_set_interest_rate(call: ServiceCall):
    rate = call.data.get("rate")
    if rate is not None:
        MORTGAGE_DATA["interest_rate"] = rate

async def handle_reset_mortgage(call: ServiceCall):
    balance = call.data.get("balance", 200000)
    MORTGAGE_DATA["balance"] = balance
    MORTGAGE_DATA["payments"] = []

async def handle_set_regular_payment(call: ServiceCall):
    amount = call.data.get("amount")
    if amount is not None:
        MORTGAGE_DATA["regular_payment"] = amount

async def handle_set_payment_day(call: ServiceCall):
    day = call.data.get("day")
    if day is not None:
        MORTGAGE_DATA["payment_day"] = day
