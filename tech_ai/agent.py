from google.adk.agents import Agent
from typing import Optional, Dict, Any


def web_search(input_data: str) -> str:
    """web_search
    
    Args:
        input_data (str): Input parameter for web_search
    
    Returns:
        str: Result of web_search
    """
    # TODO: Implement web_search
    return ""

def summariser(input_data: str) -> str:
    """summariser
    
    Args:
        input_data (str): Input parameter for summariser
    
    Returns:
        str: Result of summariser
    """
    # TODO: Implement summariser
    return ""


root_agent = Agent(
    name="tech_ai",
    model="gemini-2.0-flash",
    description="This agent fetches the latest AI-related news and provides summaries of tech events upon request.",
    instruction="The agent is triggered when the user asks 'What's on tech?' or poses a specific query regarding tech or AI. Upon activation, the agent fetches the latest relevant news articles, summarizes the information, and presents the summary to the user.",
    tools=[web_search, summariser],
)
