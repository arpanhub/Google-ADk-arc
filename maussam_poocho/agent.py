from google.adk.agents import Agent
import random

def get_weather(city: str) -> dict:
    '''Retrieves current weather information for a given city.

    Args:
        city (str): The name of the city.

    Returns:
        dict: A dictionary containing the weather information, including temperature, conditions, and humidity.
              Returns an error message if the city is invalid.
    '''
    # Mock weather data for demonstration purposes
    weather_data = {
        "New York": {"temperature": 25, "conditions": "Sunny", "humidity": 60},
        "London": {"temperature": 18, "conditions": "Cloudy", "humidity": 75},
        "Tokyo": {"temperature": 28, "conditions": "Rainy", "humidity": 80},
        "Sydney": {"temperature": 22, "conditions": "Partly Cloudy", "humidity": 65},
        "InvalidCity": None
    }

    if city in weather_data:
        if weather_data[city] is not None:
            temperature = weather_data[city]["temperature"]
            conditions = weather_data[city]["conditions"]
            humidity = weather_data[city]["humidity"]
            return {"status": "success", "result": f"The weather in {city} is {temperature}°C, {conditions}, with {humidity}% humidity."}
        else:
            return {"status": "error", "result": f"Could not retrieve weather data for {city}."}
    else:
        return {"status": "error", "result": "Invalid city name. Please provide a valid city."}


root_agent = Agent(
    name="maussam_poocho",
    model="gemini-2.0-flash",
    description="Provides current weather information for cities.",
    instruction="The agent should use the get_weather tool to retrieve weather information for a given city and then present the information to the user in a concise and readable format. The agent should ask for the city, call get_weather and respond to the user. The agent should handle invalid city names gracefully.",
    tools=[get_weather]
)