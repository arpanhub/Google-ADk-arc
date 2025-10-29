"""LLM-based code generator for ADK agents."""

from google import genai
import os
from typing import Dict, Any
from .agent_templates import AGENT_TEMPLATE_KNOWLEDGE  # Add dot

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

SYSTEM_INSTRUCTION = f"""You are an expert Python code generator for Google ADK agents.

Your task: Generate COMPLETE, WORKING agent.py files based on user requirements.

{AGENT_TEMPLATE_KNOWLEDGE}

CRITICAL RULES:
1. Generate ONLY valid Python code - no explanations, no markdown
2. Include ALL imports at top
3. Implement ALL tool functions with actual logic (not just pass)
4. Use proper type hints
5. Include detailed docstrings
6. Agent name must be lowercase_with_underscores
7. Return ONLY the agent.py content, nothing else

OUTPUT FORMAT:
Start directly with: from google.adk.agents import Agent
End with: tools=[...] followed by closing parenthesis

Do NOT include:
- Markdown code fences (```)
- Explanatory text
- Comments like "# This creates..."
- Multiple file outputs

Generate complete, production-ready code."""


def generate_agent_code(
    agent_name: str,
    description: str,
    instruction: str,
    tools_spec: str,
    model: str = "gemini-2.0-flash"
) -> str:
    """Generate agent.py code using LLM."""
    
    user_prompt = f"""Generate agent.py for:

AGENT NAME: {agent_name}
DESCRIPTION: {description}
INSTRUCTION: {instruction}

TOOLS NEEDED:
{tools_spec}

MODEL: {model}

Requirements:
- Implement ALL tool functions with realistic mock logic
- Use proper error handling
- Return dicts with 'status' and 'result' keys
- Include type hints and docstrings
- Generate ONLY Python code, no markdown or explanations"""

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=user_prompt,
        config={
            "system_instruction": SYSTEM_INSTRUCTION,
            "temperature": 0.1,
            "max_output_tokens": 2048
        }
    )
    
    generated_code = response.text.strip()
    
    # Clean markdown
    if "```python" in generated_code:
        generated_code = generated_code.split("```python")[1].split("```")[0].strip()
    elif "```" in generated_code:
        generated_code = generated_code.split("```")[1].split("```")[0].strip()
    
    return generated_code


def create_agent_from_spec(spec: Dict[str, Any]) -> Dict[str, str]:
    """Generate and write all agent files."""
    from pathlib import Path
    from .agent_templates import INIT_PY_TEMPLATE, ENV_TEMPLATE  # Add dot
    
    agent_name = spec["agent_name"]
    base_dir = Path(__file__).parent.parent
    agent_dir = base_dir / agent_name
    
    agent_dir.mkdir(exist_ok=True)
    
    try:
        agent_code = generate_agent_code(
            agent_name=agent_name,
            description=spec["description"],
            instruction=spec["instruction"],
            tools_spec=spec["tools_spec"],
            model=spec.get("model", "gemini-2.0-flash")
        )
        
        agent_file = agent_dir / "agent.py"
        agent_file.write_text(agent_code, encoding='utf-8')
        
        init_file = agent_dir / "__init__.py"
        init_file.write_text(INIT_PY_TEMPLATE, encoding='utf-8')
        
        env_file = agent_dir / ".env"
        env_content = ENV_TEMPLATE.format(api_key=os.getenv("GOOGLE_API_KEY", ""))
        env_file.write_text(env_content, encoding='utf-8')
        
        return {
            "status": "success",
            "message": f"Agent '{agent_name}' created successfully",
            "files": {
                "agent_py": str(agent_file),
                "init_py": str(init_file),
                "env": str(env_file)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to generate agent: {str(e)}"
        }