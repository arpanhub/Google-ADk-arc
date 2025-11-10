import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

#state managment for requirements collection
_requirements_state = {
    "active": False,
    "agent_spec":{},
    "env_data":{},
    "package":{},
    "config":{}
}

def get_root_directory()->Path:
    """get the root dir where agent will born"""
    current_file_path = Path(__file__).resolve()
    root_directory = current_file_path.parent.parent
    return root_directory

def start_requirements_collection(agent_spec:Dict[str, Any], env_data:Dict[str, Any], package:Dict[str, Any], config:Dict[str, Any]) -> None:
    """Start the requirements collection process."""
    global _requirements_state
    _requirements_state ={
        "active": True,
        "agent_spec":{
            "agent_name":None,
            "description":None,
            "instruction":None,
            "tool_descriptions":None,
            "model":"gemini-2.0-flash"
        },
        "env_data":{},
        "package":{},
        "config":{}

    }

    return {
        "status":"success",
        "message":"Requirements collection started.Please provide: agent_name, description, instruction, tools_description"
    }

def add_basic_requirement(field_name: str, field_value: str) -> dict:
    """Set basic agent information."""
    global _requirements_state
    
    if not _requirements_state["active"]:
        return {"status": "error", "message": "Requirements collection not started. Call start_requirements_collection() first."}
    
    valid_fields = ["agent_name", "description", "instruction", "tools_description", "model"]
    
    if field_name not in valid_fields:
        return {"status": "error", "message": f"Invalid field. Must be one of: {', '.join(valid_fields)}"}
    
    _requirements_state["agent_spec"][field_name] = field_value
    
    return {
        "status": "success",
        "message": f"Set {field_name} = {field_value[:50]}..." if len(field_value) > 50 else f"Set {field_name} = {field_value}"
    }



def add_api_key_requirement(service_name: str, key_placeholder: str, description: str = "") -> dict:
    """Add API key requirement for external services."""
    global _requirements_state
    
    if not _requirements_state["active"]:
        return {"status": "error", "message": "Requirements collection not started."}
    
    _requirements_state["env_data"][service_name] = {
        "value": key_placeholder,
        "description": description
    }
    
    return {
        "status": "success",
        "message": f"Added API key requirement: {service_name}"
    }

def add_package_dependency(package_name: str, version: str = "", purpose: str = "") -> dict:
    """Add external Python package dependency."""
    global _requirements_state
    
    if not _requirements_state["active"]:
        return {"status": "error", "message": "Requirements collection not started."}
    
    package_spec = f"{package_name}{version}" if version else package_name
    
    _requirements_state["packages"].append({
        "package": package_spec,
        "purpose": purpose
    })
    
    return {
        "status": "success",
        "message": f"Added package: {package_spec}"
    }

def get_requirements_status() -> dict:
    """Check current progress of requirements collection."""
    global _requirements_state
    
    if not _requirements_state["active"]:
        return {"status": "error", "message": "No active requirements collection."}
    
    spec = _requirements_state["agent_spec"]
    required_fields = ["agent_name", "description", "instruction", "tools_description"]
    
    missing = [f for f in required_fields if not spec.get(f)]
    complete = [f for f in required_fields if spec.get(f)]
    
    progress = (len(complete) / len(required_fields)) * 100
    
    return {
        "status": "success",
        "progress": f"{progress:.0f}%",
        "completed_fields": complete,
        "missing_fields": missing,
        "api_keys": list(_requirements_state["env_data"].keys()),
        "packages": [p["package"] for p in _requirements_state["packages"]],
        "ready_to_create": len(missing) == 0
    }

def generate_init_file()->str:
    """Generate the __init__.py file content."""
    return """from .agent import root_agent
    __all__ = ["root_agent"]
    """

def parse_tools_from_description(tools_description: str) -> list:
    """Parse tool descriptions and generate tool function stubs."""
    tools = []
    # Split by common separators
    tool_lines = [line.strip() for line in tools_description.split(',') if line.strip()]
    
    for tool_desc in tool_lines:
        # Extract tool name (first word or before colon/dash)
        tool_name = tool_desc.split(':')[0].split('-')[0].strip()
        tool_name = tool_name.replace(' ', '_').lower()
        
        # Clean up non-alphanumeric except underscore
        tool_name = ''.join(c for c in tool_name if c.isalnum() or c == '_')
        
        if tool_name:
            tools.append({
                "name": tool_name,
                "description": tool_desc
            })
    
    return tools

def generate_agent_code(spec: dict) -> str:
    """Generate the agent.py file content."""
    tools = parse_tools_from_description(spec["tools_description"])
    
    # Generate tool functions
    tool_functions = []
    tool_names = []
    
    for tool in tools:
        func_name = tool["name"]
        tool_names.append(func_name)
        
        tool_func = f'''def {func_name}(input_data: str) -> str:
    """{tool["description"]}
    
    Args:
        input_data (str): Input parameter for {func_name}
    
    Returns:
        str: Result of {func_name}
    """
    # TODO: Implement {func_name}
    return ""
'''
        tool_functions.append(tool_func)
    
    # Generate full agent file
    agent_code = f'''from google.adk.agents import Agent
from typing import Optional, Dict, Any


{chr(10).join(tool_functions)}

root_agent = Agent(
    name="{spec["agent_name"]}",
    model="{spec.get("model", "gemini-2.0-flash")}",
    description="{spec["description"]}",
    instruction="{spec["instruction"]}",
    tools=[{", ".join(tool_names)}],
)
'''
    
    return agent_code


def generate_env_file(env_data: dict) -> str:
    """Generate .env file content."""
    lines = ["GOOGLE_API_KEY=your_google_api_key_here"]
    
    for key, data in env_data.items():
        comment = f"# {data['description']}" if data.get('description') else ""
        if comment:
            lines.append(comment)
        lines.append(f"{key}={data['value']}")
    
    return '\n'.join(lines)


def generate_requirements_file(packages: list) -> str:
    """Generate requirements.txt content."""
    lines = ["google-adk"]
    
    for pkg in packages:
        comment = f"# {pkg['purpose']}" if pkg.get('purpose') else ""
        if comment:
            lines.append(comment)
        lines.append(pkg['package'])
    
    return '\n'.join(lines)

def create_agent_from_requirements() -> dict:
    """Finalize requirements and create the agent."""
    global _requirements_state
    
    if not _requirements_state["active"]:
        return {"status": "error", "message": "No active requirements collection."}
    
    spec = _requirements_state["agent_spec"]
    required_fields = ["agent_name", "description", "instruction", "tools_description"]
    missing = [f for f in required_fields if not spec.get(f)]
    
    if missing:
        return {
            "status": "error",
            "message": f"Missing required fields: {', '.join(missing)}"
        }
    
    # Create agent directory
    root_dir = get_root_directory()
    agent_dir = root_dir / spec["agent_name"]
    
    if agent_dir.exists():
        return {
            "status": "error",
            "message": f"Agent directory already exists: {agent_dir}"
        }
    
    try:
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate and write __init__.py
        init_content = generate_init_file()
        init_file = agent_dir / "__init__.py"
        init_file.write_text(init_content)

        # Generate and write agent.py
        agent_code = generate_agent_code(spec)
        agent_file = agent_dir / "agent.py"
        agent_file.write_text(agent_code)
        
        # Generate and write .env
        env_content = generate_env_file(_requirements_state["env_data"])
        env_file = agent_dir / ".env"
        env_file.write_text(env_content)
        
        # Generate and write requirements.txt if packages exist
        if _requirements_state["packages"]:
            req_content = generate_requirements_file(_requirements_state["packages"])
            req_file = agent_dir / "requirements.txt"
            req_file.write_text(req_content)
        
        # Reset state
        _requirements_state["active"] = False
        
        return {
            "status": "success",
            "message": f"Agent '{spec['agent_name']}' created successfully at {agent_dir}",
            "agent_directory": str(agent_dir),
            "files_created": ["__init__.py", "agent.py", ".env"] + (["requirements.txt"] if _requirements_state["packages"] else []),
            "next_steps": [
                "1. Update API keys in .env file",
                "2. Implement TODO sections in agent.py",
                f"3. Run 'adk web' and select '{spec['agent_name']}' from dropdown"
            ]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create agent: {str(e)}"
        }


def list_created_agents() -> dict:
    """List all agents in the getting_started directory."""
    root_dir = get_root_directory()
    
    agents = []
    for item in root_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.') and not item.name.startswith('__'):
            agent_file = item / "agent.py"
            if agent_file.exists():
                agents.append({
                    "name": item.name,
                    "path": str(item)
                })
    
    return {
        "status": "success",
        "agents": agents,
        "total": len(agents)
    }


def view_agent_code(agent_name: str) -> dict:
    """Display the current code of an agent for review."""
    root_dir = get_root_directory()
    agent_dir = root_dir / agent_name
    
    if not agent_dir.exists():
        return {"status": "error", "message": f"Agent '{agent_name}' not found"}
    
    agent_file = agent_dir / "agent.py"
    if not agent_file.exists():
        return {"status": "error", "message": f"agent.py not found in {agent_name}"}
    
    code = agent_file.read_text()
    
    return {
        "status": "success",
        "agent_name": agent_name,
        "code": code
    }

