from google.adk.agents import Agent
from typing import Optional
import json

def convert_currency(amount: str, from_currency: str, to_currency: str) -> dict:
    """Converts an amount from one currency to another.

    Args:
        amount (str): The amount to convert.
        from_currency (str): The currency to convert from.
        to_currency (str): The currency to convert to.

    Returns:
        dict: A dictionary containing the status and the converted amount.
    """
    try:
        amount_float = float(amount)
    except ValueError:
        return {"status": "error", "result": "Invalid amount. Please provide a numeric value."}

    # Mock conversion logic (replace with actual API call)
    exchange_rates = {
        "USD_EUR": 0.92,
        "EUR_USD": 1.09,
        "USD_GBP": 0.79,
        "GBP_USD": 1.27,
        "EUR_GBP": 0.86,
        "GBP_EUR": 1.16,
    }

    currency_pair = f"{from_currency}_{to_currency}"
    reverse_currency_pair = f"{to_currency}_{from_currency}"

    if currency_pair in exchange_rates:
        rate = exchange_rates[currency_pair]
        converted_amount = amount_float * rate
        return {"status": "success", "result": f"{amount} {from_currency} is equal to {converted_amount:.2f} {to_currency}"}
    elif reverse_currency_pair in exchange_rates:
        rate = exchange_rates[reverse_currency_pair]
        converted_amount = amount_float / rate
        return {"status": "success", "result": f"{amount} {from_currency} is equal to {converted_amount:.2f} {to_currency}"}
    else:
        return {"status": "error", "result": "Currency pair not supported."}


def get_exchange_rate(currency_pair: str) -> dict:
    """Gets the current exchange rate between two currencies.

    Args:
        currency_pair (str): The currency pair (e.g., "USD_EUR").

    Returns:
        dict: A dictionary containing the status and the exchange rate.
    """
    # Mock exchange rate data (replace with actual API call)
    exchange_rates = {
        "USD_EUR": 0.92,
        "EUR_USD": 1.09,
        "USD_GBP": 0.79,
        "GBP_USD": 1.27,
        "EUR_GBP": 0.86,
        "GBP_EUR": 1.16,
    }

    if currency_pair in exchange_rates:
        rate = exchange_rates[currency_pair]
        return {"status": "success", "result": f"The exchange rate for {currency_pair} is {rate}"}
    else:
        return {"status": "error", "result": "Currency pair not supported."}


currency_agent = Agent(
    name="currency_agent",
    model="gemini-2.0-flash",
    description="A currency converter agent that converts between different currencies and provides exchange rates.",
    instruction="The agent should first ask the user for the initial currency, then the amount to convert, and finally the desired currency. Use the convert_currency tool to perform the conversion and respond to the user with the converted amount. If the user asks for the exchange rate, use the get_exchange_rate tool.",
    tools=[convert_currency, get_exchange_rate]
)