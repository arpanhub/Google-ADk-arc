from google.adk.agents import Agent
from typing import Optional, Dict, Any


def add_numbers(num1: str, num2: str) -> str:
    """This tool gives the addition of the 2 numbers
    
    Args:

        num1 (str): First number to add

        num2 (str): Second number to add

    
    Returns:
        str: Result of add_numbers
    """
    # TODO: Implement add_numbers
    return ""


def subtract_numbers(num1: str, num2: str) -> str:
    """This tool gives the subtraction of the 2 numbers
    
    Args:

        num1 (str): First number to subtract from

        num2 (str): Second number to subtract

    
    Returns:
        str: Result of subtract_numbers
    """
    # TODO: Implement subtract_numbers
    return ""



root_agent = Agent(
    name="calculator_agent",
    model="gemini-2.0-flash",
    description="Calculator agent for addition and subtraction",
    instruction="You are an agent that: Calculator agent for addition and subtraction",
    tools=[add_numbers, subtract_numbers],
)