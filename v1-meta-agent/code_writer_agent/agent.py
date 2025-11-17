from google.adk.agents import Agent
from openai import OpenAI
import os
import json
import ast
from typing import List, Dict, Any


def write_tool_implementation(
    tool_name: str,
    tool_description: str,
    input_parameters: str,
    expected_output: str,
    context: str = ""
) -> dict:
    """
    Use OpenAI to generate full implementation for a tool function.
    
    Args:
        tool_name (str): Function name (e.g., "create_slack_canvas")
        tool_description (str): What the tool should do
        input_parameters (str): JSON string of parameter specifications
        expected_output (str): Description of return value
        context (str): Additional context (API docs, dependencies, etc.)
    
    Returns:
        dict: Generated code and metadata
    """
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here":
            return {
                "status": "error",
                "message": "OpenAI API key not configured",
                "fallback_code": generate_fallback_skeleton(tool_name, tool_description, [])
            }
        
        # Parse parameters if JSON string
        try:
            params = json.loads(input_parameters) if input_parameters else []
        except:
            params = []
        
        params_str = ", ".join([f"{p.get('name', 'param')}: {p.get('type', 'str')}" for p in params])
        
        system_prompt = """You are an expert Python developer specializing in API integrations and tool implementations.
Generate complete, production-ready function implementations.

Requirements:
- Include all necessary imports at the top of the function
- Add proper error handling (try/except blocks)
- Use type hints for parameters and return types
- Include detailed docstrings with Args and Returns sections
- Use environment variables for API keys (os.getenv())
- Return structured data (dict or specific types)
- Add inline comments for complex logic
- Handle edge cases and validation

Do NOT include:
- TODO comments
- Placeholder logic
- Mock implementations
- Explanatory text outside the code

Return ONLY valid Python code, properly formatted."""

        user_prompt = f"""Generate a complete Python function implementation:

Function Name: {tool_name}
Description: {tool_description}
Parameters: {params_str}
Expected Output: {expected_output}

Additional Context:
{context if context else "No additional context provided"}

Generate the complete function with all imports, error handling, and proper documentation."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        generated_code = response.choices[0].message.content.strip()
        
        # Extract code from markdown if wrapped
        if "```python" in generated_code:
            code_blocks = generated_code.split("```python")
            if len(code_blocks) > 1:
                generated_code = code_blocks[1].split("```")[0].strip()
        elif "```" in generated_code:
            code_blocks = generated_code.split("```")
            if len(code_blocks) > 1:
                generated_code = code_blocks[1].strip()
        
        return {
            "status": "success",
            "code": generated_code,
            "model_used": "gpt-4o",
            "tokens_used": response.usage.total_tokens
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"OpenAI generation failed: {str(e)}",
            "fallback_code": generate_fallback_skeleton(tool_name, tool_description, params if 'params' in locals() else [])
        }


def validate_generated_code(code: str) -> dict:
    """
    Validate that generated code is syntactically correct.
    
    Args:
        code (str): Python code string to validate
    
    Returns:
        dict: Validation result with status and details
    """
    try:
        ast.parse(code)
        return {
            "valid": True,
            "message": "Code is syntactically valid",
            "error": None
        }
    except SyntaxError as e:
        return {
            "valid": False,
            "message": "Syntax error detected",
            "error": str(e),
            "line": e.lineno,
            "offset": e.offset
        }
    except Exception as e:
        return {
            "valid": False,
            "message": "Validation error",
            "error": str(e)
        }


def generate_fallback_skeleton(tool_name: str, description: str, params: list) -> str:
    """
    Generate skeleton code if OpenAI fails.
    
    Args:
        tool_name (str): Function name
        description (str): Function description
        params (list): List of parameter specifications
    
    Returns:
        str: Skeleton function code
    """
    if not params:
        params = [{"name": "input_data", "type": "str", "description": "Input parameter"}]
    
    params_str = ", ".join([f"{p.get('name', 'param')}: {p.get('type', 'str')}" for p in params])
    params_doc = "\n        ".join([
        f"{p.get('name', 'param')} ({p.get('type', 'str')}): {p.get('description', 'Parameter description')}"
        for p in params
    ])
    
    return f'''def {tool_name}({params_str}) -> dict:
    """
    {description}
    
    Args:
        {params_doc}
    
    Returns:
        dict: Result of {tool_name}
    """
    # TODO: Implementation needed - OpenAI code generation failed
    # Please implement the logic for this tool
    raise NotImplementedError("{tool_name} requires manual implementation")
'''


def infer_parameters_heuristic(tool_name: str, tool_description: str) -> list:
    """
    Fallback heuristic-based parameter inference.
    
    Args:
        tool_name (str): Function name
        tool_description (str): Function description
    
    Returns:
        list: List of parameter specifications
    """
    description_lower = tool_description.lower()
    
    # Webhook handlers
    if "webhook" in description_lower or "receive" in description_lower:
        return [
            {"name": "payload", "type": "dict", "description": "Webhook payload data"}
        ]
    
    # Slack operations
    if "slack" in description_lower:
        if "canvas" in description_lower:
            return [
                {"name": "channel_id", "type": "str", "description": "Slack channel ID"},
                {"name": "title", "type": "str", "description": "Canvas title"},
                {"name": "content", "type": "dict", "description": "Canvas content structure"}
            ]
        elif "message" in description_lower or "post" in description_lower:
            return [
                {"name": "channel_id", "type": "str", "description": "Slack channel ID"},
                {"name": "message", "type": "str", "description": "Message text"}
            ]
        elif "reminder" in description_lower:
            return [
                {"name": "user_id", "type": "str", "description": "User ID to remind"},
                {"name": "text", "type": "str", "description": "Reminder text"},
                {"name": "time", "type": "str", "description": "When to remind"}
            ]
    
    # Fathom operations
    if "fathom" in description_lower:
        return [
            {"name": "call_data", "type": "dict", "description": "Fathom call summary data"}
        ]
    
    # API fetch operations
    if any(word in description_lower for word in ["fetch", "get", "retrieve"]):
        return [
            {"name": "resource_id", "type": "str", "description": "ID of resource to fetch"},
            {"name": "options", "type": "dict", "description": "Optional query parameters"}
        ]
    
    # Create/Add operations
    if any(word in description_lower for word in ["create", "add", "insert"]):
        return [
            {"name": "data", "type": "dict", "description": "Data for new resource"}
        ]
    
    # Search operations
    if "search" in description_lower:
        return [
            {"name": "query", "type": "str", "description": "Search query"},
            {"name": "filters", "type": "dict", "description": "Optional filters"}
        ]
    
    # Generic fallback
    return [
        {"name": "input_data", "type": "str", "description": "Input data for the operation"}
    ]


# Create the Code Writer Agent
code_writer_agent = Agent(
    name="code_writer_agent",
    model="gemini-2.0-flash",
    description="Orchestrates OpenAI to write functional code implementations for tools",
    instruction="""You are a code generation orchestrator that uses OpenAI GPT-4o to write production-ready Python code.

When asked to implement a tool:
1. Analyze the tool name and description to understand requirements
2. Use infer_parameters_heuristic() to determine appropriate parameters
3. Call write_tool_implementation() with clear specifications including:
   - Tool name and description
   - Inferred parameters as JSON
   - Expected output format
   - Context about packages, APIs, and dependencies
4. Call validate_generated_code() to verify syntax correctness
5. If validation fails, analyze the error and suggest fixes
6. Return the final validated code

Be specific in your requests to OpenAI - provide:
- Exact function signatures with type hints
- Required libraries/packages from context
- Expected data structures for inputs and outputs
- API endpoints and authentication methods
- Error cases to handle properly

If OpenAI generation fails, use the fallback skeleton code provided in the response.""",
    tools=[
        write_tool_implementation,
        validate_generated_code,
        infer_parameters_heuristic
    ]
)