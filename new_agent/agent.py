from google.adk.agents import Agent
from typing import Optional, Dict, Any


def get_weather(country_name: str) -> dict:
    """Gets the current weather for a given country.
    
    Args:

        country_name (str): Country to get weather information for.

    
    Returns:
        dict: Result of get_weather
    """
    # TODO: Implement get_weather
    return {"status": "success"}



root_agent = Agent(
    name="new_agent",
    model="gemini-2.0-flash",
    description="agent that tells the current weather for a specific country",
    instruction="You are an agent that: agent that tells the current weather for a specific country",
    tools=[get_weather],
)