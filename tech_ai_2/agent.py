from bs4 import BeautifulSoup
from google.adk.agents import Agent
from requests.exceptions import HTTPError, RequestException
from requests.exceptions import RequestException
from transformers import pipeline, Pipeline
from typing import Dict
from typing import Dict, Any
from typing import Optional, Dict, Any
import os
import requests


import os
import requests
from typing import Dict, Any
from bs4 import BeautifulSoup

def fetch_tech_news(resource_id: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scrapes and retrieves the latest tech news articles from top tech websites.

    Args:
        resource_id (str): The identifier for the tech news resource or website.
        options (dict): Additional options for the scraping process, such as headers or query parameters.

    Returns:
        dict: A dictionary containing the success status and result data, including summaries of the latest articles.
    """
    try:
        # Validate resource_id
        if not resource_id:
            raise ValueError("Resource ID cannot be empty.")

        # Define base URLs for known tech websites
        tech_websites = {
            'techcrunch': 'https://techcrunch.com',
            'wired': 'https://www.wired.com',
            'theverge': 'https://www.theverge.com'
        }

        # Check if the resource_id is valid
        if resource_id not in tech_websites:
            raise ValueError("Unsupported resource ID. Please use a valid tech website identifier.")

        # Construct the URL
        url = tech_websites[resource_id]

        # Fetch the webpage content
        response = requests.get(url, headers=options.get('headers', {}))
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the webpage content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract article summaries
        articles = []
        if resource_id == 'techcrunch':
            for article in soup.find_all('div', class_='post-block'):
                title = article.find('h2', class_='post-block__title').get_text(strip=True)
                summary = article.find('div', class_='post-block__content').get_text(strip=True)
                articles.append({'title': title, 'summary': summary})
        elif resource_id == 'wired':
            for article in soup.find_all('li', class_='archive-item-component'):
                title = article.find('h2', class_='archive-item-component__title').get_text(strip=True)
                summary = article.find('p', class_='archive-item-component__desc').get_text(strip=True)
                articles.append({'title': title, 'summary': summary})
        elif resource_id == 'theverge':
            for article in soup.find_all('div', class_='c-entry-box--compact'):
                title = article.find('h2', class_='c-entry-box--compact__title').get_text(strip=True)
                summary = article.find('p', class_='p-dek').get_text(strip=True) if article.find('p', class_='p-dek') else ''
                articles.append({'title': title, 'summary': summary})

        # Return the structured data
        return {'success': True, 'data': articles}

    except requests.exceptions.RequestException as e:
        # Handle network-related errors
        return {'success': False, 'error': f"Network error occurred: {str(e)}"}
    except Exception as e:
        # Handle other exceptions
        return {'success': False, 'error': str(e)}
import os
import requests
from typing import Dict, Any
from transformers import pipeline, Pipeline
from requests.exceptions import HTTPError, RequestException

def summarize_news(resource_id: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Summarizes the content of the fetched news articles from a specified resource.

    Args:
        resource_id (str): The identifier for the news resource.
        options (dict): Additional options for fetching and summarizing the news.

    Returns:
        dict: A dictionary containing the success status and the summarized result data.
    """
    # Initialize the response dictionary
    response = {
        "success": False,
        "data": None,
        "error": None
    }
    
    try:
        # Fetch the API key from environment variables
        api_key = os.getenv('NEWS_API_KEY')
        if not api_key:
            raise ValueError("API key is missing. Please set the NEWS_API_KEY environment variable.")

        # Construct the API URL using the resource_id and options
        api_url = f"https://newsapi.org/v2/top-headlines?sources={resource_id}&apiKey={api_key}"
        
        # Add additional options to the request if provided
        if options.get('language'):
            api_url += f"&language={options['language']}"
        
        # Make the request to the news API
        response_data = requests.get(api_url)
        response_data.raise_for_status()  # Raise an error for bad responses

        # Parse the JSON response
        articles = response_data.json().get('articles', [])
        if not articles:
            raise ValueError("No articles found for the given resource.")

        # Initialize the summarization pipeline
        summarizer: Pipeline = pipeline("summarization")

        # Summarize each article
        summaries = []
        for article in articles:
            content = article.get('content', '')
            if content:
                # Summarize the content
                summary = summarizer(content, max_length=130, min_length=30, do_sample=False)
                summaries.append({
                    "title": article.get('title', 'No Title'),
                    "summary": summary[0]['summary_text']
                })

        # Update the response dictionary with success status and data
        response["success"] = True
        response["data"] = summaries

    except HTTPError as http_err:
        response["error"] = f"HTTP error occurred: {http_err}"
    except RequestException as req_err:
        response["error"] = f"Request error occurred: {req_err}"
    except ValueError as val_err:
        response["error"] = str(val_err)
    except Exception as err:
        response["error"] = f"An unexpected error occurred: {err}"

    return response
import os
import requests
from typing import Dict, Any
from requests.exceptions import RequestException

def respond_to_user(input_data: str) -> Dict[str, Any]:
    """
    Responds to the user with the summarized news from top latest tech websites.

    Args:
        input_data (str): The input data or query from the user.

    Returns:
        Dict[str, Any]: A dictionary containing the success status and the result data.
    """
    try:
        # Validate input data
        if not input_data.strip():
            return {"success": False, "error": "Input data cannot be empty."}

        # Retrieve API key from environment variables
        api_key = os.getenv('NEWS_API_KEY')
        if not api_key:
            return {"success": False, "error": "API key is not set in environment variables."}

        # Define the API endpoint and parameters
        api_url = "https://newsapi.org/v2/top-headlines"
        params = {
            'category': 'technology',
            'language': 'en',
            'apiKey': api_key
        }

        # Make the API request
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # Raise an error for HTTP errors

        # Parse the JSON response
        news_data = response.json()

        # Check if the API returned articles
        if not news_data.get('articles'):
            return {"success": False, "error": "No articles found."}

        # Summarize the articles
        summaries = []
        for article in news_data['articles']:
            title = article.get('title', 'No Title')
            description = article.get('description', 'No Description')
            summaries.append(f"{title}: {description}")

        # Compile the summarized response
        result = {
            "success": True,
            "summaries": summaries
        }
        return result

    except RequestException as e:
        # Handle network-related errors
        return {"success": False, "error": f"Network error occurred: {str(e)}"}
    except Exception as e:
        # Handle any other unforeseen errors
        return {"success": False, "error": f"An error occurred: {str(e)}"}
import os
import requests
from typing import Dict

def introduce_self(input_data: str) -> Dict[str, str]:
    """
    Introduces the agent to the user by summarizing the top latest tech websites' blogs.

    Args:
        input_data (str): The input data provided by the user.

    Returns:
        Dict[str, str]: A dictionary containing the success status and the result data.
    """
    try:
        # Validate input data
        if not input_data or not isinstance(input_data, str):
            raise ValueError("Input data must be a non-empty string.")

        # Simulating the agent's introduction
        introduction = (
            "Hello! I am your tech blog summarizer. I can provide you with summaries "
            "of the latest articles from top tech websites. Just let me know which "
            "topics you're interested in!"
        )

        # Return the introduction as the result
        return {
            "success": "true",
            "result": introduction
        }

    except ValueError as ve:
        # Handle input validation errors
        return {
            "success": "false",
            "error": str(ve)
        }
    except Exception as e:
        # Handle any other unexpected errors
        return {
            "success": "false",
            "error": "An unexpected error occurred: " + str(e)
        }


root_agent = Agent(
    name="tech_ai_2",
    model="gemini-2.0-flash",
    description="This agent summarises the top latest tech webistes blogs and give me summarise it for me",
    instruction="""This agent tells user about the agent tech_ai that it can summarize latest news in past 24 hours for the user , on the user request""",
    tools=[fetch_tech_news, summarize_news, respond_to_user, introduce_self],
)
