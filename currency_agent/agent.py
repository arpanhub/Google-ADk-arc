from google.adk.agents import Agent
from typing import Optional

def convert_currency(from_currency: str, to_currency: str, amount: float) -> dict:
    """Converts an amount from one currency to another.

    Args:
        from_currency (str): The currency to convert from (e.g., USD).
        to_currency (str): The currency to convert to (e.g., EUR).
        amount (float): The amount to convert.

    Returns:
        dict: A dictionary containing the status and the converted amount.
              Example: {"status": "success", "result": 92.65}
    """
    try:
        # Mock exchange rates (replace with actual API calls in production)
        exchange_rates = {
            "USD": {"EUR": 0.92, "GBP": 0.80, "JPY": 150.00},
            "EUR": {"USD": 1.09, "GBP": 0.87, "JPY": 163.00},
            "GBP": {"USD": 1.25, "EUR": 1.15, "JPY": 188.00},
            "JPY": {"USD": 0.0067, "EUR": 0.0061, "GBP": 0.0053}
        }

        if from_currency not in exchange_rates or to_currency not in exchange_rates[from_currency]:
            return {"status": "error", "result": "Invalid currency pair."}

        exchange_rate = exchange_rates[from_currency][to_currency]
        converted_amount = amount * exchange_rate
        return {"status": "success", "result": round(converted_amount, 2)}

    except Exception as e:
        return {"status": "error", "result": str(e)}


def get_exchange_rate(from_currency: str, to_currency: str) -> dict:
    """Retrieves the exchange rate between two currencies.

    Args:
        from_currency (str): The currency to convert from (e.g., USD).
        to_currency (str): The currency to convert to (e.g., EUR).

    Returns:
        dict: A dictionary containing the status and the exchange rate.
              Example: {"status": "success", "result": 0.92}
    """
    try:
        # Mock exchange rates (replace with actual API calls in production)
        exchange_rates = {
            "USD": {"EUR": 0.92, "GBP": 0.80, "JPY": 150.00},
            "EUR": {"USD": 1.09, "GBP": 0.87, "JPY": 163.00},
            "GBP": {"USD": 1.25, "EUR": 1.15, "JPY": 188.00},
            "JPY": {"USD": 0.0067, "EUR": 0.0061, "GBP": 0.0053}
        }

        if from_currency not in exchange_rates or to_currency not in exchange_rates[from_currency]:
            return {"status": "error", "result": "Invalid currency pair."}

        exchange_rate = exchange_rates[from_currency][to_currency]
        return {"status": "success", "result": exchange_rate}

    except Exception as e:
        return {"status": "error", "result": str(e)}


root_agent = Agent(
    name="currency_agent",
    model="gemini-2.0-flash",
    description="A currency converter agent that converts between different currencies and provides exchange rates.",
    instruction="The agent should first ask the user for the initial currency, then the amount to convert, and finally the desired currency. Use the convert_currency tool to perform the conversion and respond to the user with the converted amount. If the user asks for the exchange rate, use the get_exchange_rate tool.",
    tools=[convert_currency, get_exchange_rate]
)