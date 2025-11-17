from google.adk.agents import Agent
from typing import Dict, Any
from typing import Optional, Dict, Any
import os
import requests


import os
import requests
from typing import Dict, Any

def get_weather_data(resource_id: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieves weather information for a given city using a weather API.

    Args:
        resource_id (str): The name of the city for which to retrieve weather data.
        options (dict): Additional options for the request (not used in this implementation).

    Returns:
        dict: A dictionary containing the success status and result data. 
              Example: {'success': True, 'data': {...}} or {'success': False, 'error': '...'}
    """
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        return {'success': False, 'error': 'API key is not set in environment variables.'}

    # Construct the API URL
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={resource_id}&aqi=no"

    try:
        # Make the API request
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the JSON response
        data = response.json()

        # Check if the response contains the expected data
        if 'current' not in data or 'location' not in data:
            return {'success': False, 'error': 'Unexpected response structure from the API.'}

        # Return the structured data
        return {'success': True, 'data': data}

    except requests.exceptions.RequestException as e:
        # Handle any request-related errors
        return {'success': False, 'error': f'Request failed: {str(e)}'}
    except ValueError as e:
        # Handle JSON decoding errors
        return {'success': False, 'error': f'Error parsing response: {str(e)}'}


root_agent = Agent(
    name="get_weather",
    model="gemini-2.0-flash",
    description="Create a simple weather agent that ask city name and tells the weather for that",
    instruction="""agent introduces and ask user for city input to tell the weather report for that city""",
    tools=[get_weather_data],
)
