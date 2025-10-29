"""Template knowledge base for ADK agent patterns."""

AGENT_TEMPLATE_KNOWLEDGE = """
# Google ADK Agent Creation Patterns

## Basic Agent Structure
```python
from google.adk.agents import Agent

def tool_function(param: str) -> dict:
    '''Tool description.
    
    Args:
        param (str): Parameter description
        
    Returns:
        dict: Result with status
    '''
    return {"status": "success", "result": "value"}

root_agent = Agent(
    name="agent_name",
    model="gemini-2.0-flash",
    description="Agent description",
    instruction="Agent instructions",
    tools=[tool_function]
)
```

## Common Patterns

### 1. Single Tool Agent
- One function, simple logic
- Returns dict with status/result
- Model: gemini-2.0-flash

### 2. Multi-Tool Agent
- Multiple related functions
- Each tool serves specific purpose
- Tools list: [func1, func2, func3]

### 3. Tool Parameter Types
- str, int, float, bool, dict, list
- Optional[type] for optional params
- Use type hints always

### 4. Return Types
- dict: {"status": "success", "data": value}
- str: Simple text responses
- list: Multiple items
- bool: True/False

## File Structure Requirements

### agent.py
- Import from google.adk.agents
- Define all tool functions first
- Create root_agent last
- Use typing for all parameters

### __init__.py
```python
from .agent import root_agent
__all__ = ["root_agent"]
```

### .env
```
GOOGLE_GENAI_USE_VERTEXAI=0
GOOGLE_API_KEY=your_key
```

## Best Practices
- Agent names: lowercase_with_underscores
- Tool names: verb_noun format (get_weather, calculate_sum)
- Always include docstrings
- Return dict for complex data
- Use typing.Optional for optional params
"""

AGENT_PY_TEMPLATE = '''from google.adk.agents import Agent
from typing import Optional, Dict, Any, List

{tools_code}

root_agent = Agent(
    name="{agent_name}",
    model="{model}",
    description="{description}",
    instruction="""{instruction}""",
    tools=[{tool_names}]
)
'''

INIT_PY_TEMPLATE = '''from .agent import root_agent

__all__ = ["root_agent"]
'''

ENV_TEMPLATE = '''GOOGLE_GENAI_USE_VERTEXAI=0
GOOGLE_API_KEY={api_key}
'''