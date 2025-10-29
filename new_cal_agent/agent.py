from google.adk.agents import Agent

def add_numbers(num1: str, num2: str) -> dict:
    '''Adds two numbers.

    Args:
        num1 (str): The first number.
        num2 (str): The second number.

    Returns:
        dict: A dictionary containing the status and the result of the addition.
    '''
    try:
        number1 = float(num1)
        number2 = float(num2)
        result = number1 + number2
        return {"status": "success", "result": str(result)}
    except ValueError:
        return {"status": "error", "result": "Invalid input: Please provide valid numbers."}

def subtract_numbers(num1: str, num2: str) -> dict:
    '''Subtracts the second number from the first number.

    Args:
        num1 (str): The first number.
        num2 (str): The second number.

    Returns:
        dict: A dictionary containing the status and the result of the subtraction.
    '''
    try:
        number1 = float(num1)
        number2 = float(num2)
        result = number1 - number2
        return {"status": "success", "result": str(result)}
    except ValueError:
        return {"status": "error", "result": "Invalid input: Please provide valid numbers."}

root_agent = Agent(
    name="new_cal_agent",
    model="gemini-2.0-flash",
    description="A calculator agent for addition and subtraction.",
    instruction="1. First, ask the user for the first number.\n2. Then, ask the user for the second number.\n3. Once you have both numbers, perform addition using the `add_numbers` tool.\n4. Then, perform subtraction using the `subtract_numbers` tool.\n5. Present both results to the user, clearly labeled.\n6. If the input is invalid at any point, return \"Invalid input\".",
    tools=[add_numbers, subtract_numbers]
)