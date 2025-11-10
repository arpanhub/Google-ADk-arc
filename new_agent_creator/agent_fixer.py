"""Agent debugging and auto-fix functionality."""

from google import genai
import os
from pathlib import Path
from typing import Dict, Any

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

FIXER_SYSTEM_INSTRUCTION = """You are an expert Python debugger for Google ADK agents.

Your task: Fix broken agent.py files based on error messages.

CRITICAL RULES:
1. Analyze the error carefully
2. Identify the exact issue (import errors, syntax errors, logic errors)
3. Generate COMPLETE, FIXED agent.py code
4. Maintain all existing functionality
5. Only fix the specific issue reported
6. Return ONLY Python code, no explanations

Common ADK Issues:
- Import errors: Use 'from google.adk.agents import Agent'
- Type hints: Use 'from typing import Optional, Dict, Any, List'
- Tool returns: Must return dict or specified type
- Relative imports: Not needed in agent.py (it's the root)
- Missing docstrings: Add them
- Undefined variables: Initialize properly

OUTPUT: Complete, working agent.py file content."""


def analyze_and_fix_agent(
    agent_name: str,
    error_message: str,
    user_description: str = ""
) -> Dict[str, Any]:
    """Analyze error and generate fixed agent code.
    
    Args:
        agent_name: Name of the broken agent
        error_message: The error message/traceback
        user_description: Optional user description of the issue
        
    Returns:
        dict: Status and fix details
    """
    base_dir = Path(__file__).parent.parent
    agent_dir = base_dir / agent_name
    agent_file = agent_dir / "agent.py"
    
    # Check if agent exists
    if not agent_file.exists():
        return {
            "status": "error",
            "message": f"Agent '{agent_name}' not found at {agent_dir}"
        }
    
    # Read current code
    try:
        current_code = agent_file.read_text(encoding='utf-8')
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to read agent file: {str(e)}"
        }
    
    # Create fix prompt
    fix_prompt = f"""Fix this broken Google ADK agent:

AGENT NAME: {agent_name}

ERROR MESSAGE:
{error_message}

CURRENT CODE:
```python
{current_code}
```

USER NOTES: {user_description if user_description else "None provided"}

INSTRUCTIONS:
1. Identify the root cause of the error
2. Fix ONLY the issue causing the error
3. Maintain all existing tool functionality
4. Ensure proper imports and type hints
5. Return the COMPLETE fixed agent.py code

Generate the fixed code now:"""

    try:
        # Call LLM to fix
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=fix_prompt,
            config={
                "system_instruction": FIXER_SYSTEM_INSTRUCTION,
                "temperature": 0.1,
                "max_output_tokens": 2048
            }
        )
        
        fixed_code = response.text.strip()
        
        # Clean markdown
        if "```python" in fixed_code:
            fixed_code = fixed_code.split("```python")[1].split("```")[0].strip()
        elif "```" in fixed_code:
            fixed_code = fixed_code.split("```")[1].split("```")[0].strip()
        
        # Backup original
        backup_file = agent_dir / "agent.py.backup"
        backup_file.write_text(current_code, encoding='utf-8')
        
        # Write fixed code
        agent_file.write_text(fixed_code, encoding='utf-8')
        
        return {
            "status": "success",
            "message": f"Agent '{agent_name}' has been fixed. Original backed up to agent.py.backup",
            "backup_path": str(backup_file),
            "fixed_path": str(agent_file),
            "action": "Please restart 'adk web' to test the fix"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to generate fix: {str(e)}"
        }


def view_agent_code(agent_name: str) -> Dict[str, Any]:
    """View current agent code for debugging.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        dict: Agent code or error
    """
    base_dir = Path(__file__).parent.parent
    agent_file = base_dir / agent_name / "agent.py"
    
    if not agent_file.exists():
        return {
            "status": "error",
            "message": f"Agent '{agent_name}' not found"
        }
    
    try:
        code = agent_file.read_text(encoding='utf-8')
        return {
            "status": "success",
            "agent_name": agent_name,
            "code": code,
            "file_path": str(agent_file)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to read file: {str(e)}"
        }


def list_created_agents() -> Dict[str, Any]:
    """List all agents created by this agent creator.
    
    Returns:
        dict: List of agent names and paths
    """
    base_dir = Path(__file__).parent.parent
    
    # Find directories with agent.py
    agents = []
    for item in base_dir.iterdir():
        if item.is_dir() and (item / "agent.py").exists():
            # Exclude special directories
            if item.name not in ["new_agent_creator", "agent_creator", ".venv", "__pycache__"]:
                agents.append({
                    "name": item.name,
                    "path": str(item),
                    "has_backup": (item / "agent.py.backup").exists()
                })
    
    return {
        "status": "success",
        "count": len(agents),
        "agents": agents
    }