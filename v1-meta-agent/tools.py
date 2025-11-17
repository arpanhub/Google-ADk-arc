import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any

# Import code writer agent
try:
    from .code_writer_agent.agent import root_agent as code_writer
except ImportError:
    code_writer = None

# State management for requirements collection
_requirements_state = {
    "active": False,
    "agent_spec": {},
    "env_data": {},
    "packages": [],
    "config": {}
}

def list_available_tools() -> dict:
    """
    Lists all available tools from the tool registry.
    Shows tool name, description, parameters, and dependencies.
    
    Returns:
        dict: Registry data with all tools and their metadata
    """
    tools_dir = Path(__file__).parent / "tools_library"
    registry_path = tools_dir / "tool_registry.json"
    
    print(f"🔍 Looking for registry at: {registry_path}")
    print(f"📁 Registry exists: {registry_path.exists()}")
    
    if not registry_path.exists():
        return {
            "status": "error",
            "error": f"Tool registry not found at: {registry_path}",
            "suggestion": "Ensure tool_registry.json exists in tools_library/"
        }
    
    try:
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        # Handle dictionary format (tool_name: tool_info)
        tools_list = []
        for tool_name, tool_info in registry.items():
            tools_list.append({
                "name": tool_name,
                **tool_info
            })
        
        print(f"\n📚 Available Tools ({len(tools_list)} total):")
        print("=" * 80)
        
        for tool in tools_list:
            print(f"\n🔧 {tool['name']}")
            print(f"   Description: {tool['description']}")
            print(f"   File: {tool['file']}")
            print(f"   Function: {tool['function']}")
            if tool.get('required_env'):
                print(f"   API Keys: {', '.join(tool['required_env'])}")
            if tool.get('dependencies'):
                print(f"   Dependencies: {', '.join(tool['dependencies'])}")
        
        print("\n" + "=" * 80)
        
        return {
            "status": "success",
            "total_tools": len(tools_list),
            "tools": tools_list,
            "registry_format": "dictionary"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to load tool registry: {str(e)}"
        }


def create_specialized_agent(
    agent_name: str,
    description: str,
    tool_names: str,
    workflow_description: str
) -> dict:
    """
    Create a new specialized agent using pre-built tools from the library.
    
    Args:
        agent_name: Name of the agent (e.g., "fathom_slack_agent")
        description: What this agent does
        tool_names: Comma-separated list of tool names from registry
        workflow_description: Step-by-step workflow this agent should execute
        
    Returns:
        dict: Agent creation result
    """
    global _requirements_state
    
    print(f"\n🚀 Creating agent: {agent_name}")
    
    # Get directories
    base_dir = Path(__file__).parent
    root_dir = base_dir.parent
    agent_dir = root_dir / agent_name
    
    tools_library_dir = base_dir / "tools_library"
    registry_path = tools_library_dir / "tool_registry.json"
    
    print(f"📁 Base directory: {base_dir}")
    print(f"📁 Tools library: {tools_library_dir}")
    print(f"📁 Agent directory: {agent_dir}")
    print(f"📁 Registry path: {registry_path}")
    print(f"📁 Registry exists: {registry_path.exists()}")
    
    if agent_dir.exists():
        return {
            "status": "error",
            "message": f"Agent '{agent_name}' already exists at {agent_dir}"
        }
    
    # Load tool registry
    if not registry_path.exists():
        return {
            "status": "error",
            "message": f"Tool registry not found at: {registry_path}",
            "debug_info": {
                "base_dir": str(base_dir),
                "tools_library_dir": str(tools_library_dir),
                "registry_path": str(registry_path),
                "registry_exists": registry_path.exists()
            }
        }
    
    try:
        with open(registry_path, 'r') as f:
            tool_registry = json.load(f)
        print(f"✅ Loaded registry with {len(tool_registry)} tools")
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to load tool registry: {str(e)}"
        }
    
    # Parse requested tools
    requested_tools = [t.strip() for t in tool_names.split(',')]
    print(f"📋 Requested tools: {requested_tools}")
    
    # Validate tools exist (registry is dict, not list)
    missing_tools = [t for t in requested_tools if t not in tool_registry]
    if missing_tools:
        available = list(tool_registry.keys())
        return {
            "status": "error",
            "message": f"Tools not found in registry: {', '.join(missing_tools)}",
            "available_tools": available
        }
    
    # Collect tool info and determine required resources
    tools_to_copy = {}
    all_env_vars = set()
    all_dependencies = set()
    
    for tool_name in requested_tools:
        tool_info = tool_registry[tool_name]
        tools_to_copy[tool_name] = tool_info
        all_env_vars.update(tool_info.get("required_env", []))
        all_dependencies.update(tool_info.get("dependencies", []))
    
    print(f"🔑 Required API keys: {list(all_env_vars)}")
    print(f"📦 Required packages: {list(all_dependencies)}")
    
    # ✅ NEW: Always include OPENAI_API_KEY from meta-agent
    meta_agent_env_path = base_dir / ".env"
    openai_key_from_meta = None
    
    if meta_agent_env_path.exists():
        print(f"🔍 Checking meta-agent .env for OpenAI key...")
        with open(meta_agent_env_path, 'r') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY='):
                    openai_key_from_meta = line.split('=', 1)[1].strip()
                    print(f"✅ Found OpenAI key in meta-agent .env")
                    break
    
    # Check if API keys are missing
    env_keys_needed = list(all_env_vars)
    collected_env_data = _requirements_state.get("env_data", {}) if _requirements_state["active"] else {}
    
    # ✅ NEW: Auto-add OpenAI key if found
    if openai_key_from_meta and "OPENAI_API_KEY" not in collected_env_data:
        collected_env_data["OPENAI_API_KEY"] = {
            "value": openai_key_from_meta,
            "description": "OpenAI API key (inherited from meta-agent)",
            "api_endpoint": "https://api.openai.com/v1"
        }
        print(f"✅ Auto-added OpenAI API key from meta-agent")
    
    missing_keys = [key for key in env_keys_needed if key not in collected_env_data]
    
    if missing_keys:
        return {
            "status": "missing_api_keys",
            "message": f"Please provide API keys before creating the agent",
            "required_api_keys": missing_keys,
            "instructions": [
                f"Call add_api_key_requirement() for each key:",
                *[f"  - {key}: (Get this from the service's settings/API section)" for key in missing_keys],
                "",
                "Example:",
                f'  add_api_key_requirement("{missing_keys[0]}", "actual_key_value", "Description", "https://api.example.com/endpoint")',
                "",
                "After collecting all keys, call create_specialized_agent() again."
            ]
        }
    
    try:
        # Create agent directory structure
        agent_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {agent_dir}")
        
        # Create __init__.py
        init_content = "from .agent import root_agent\n\n__all__ = ['root_agent']\n"
        (agent_dir / "__init__.py").write_text(init_content)
        print(f"✅ Created __init__.py")
        
        # Copy individual tool files and their subdirectories
        tool_files = set([tools_to_copy[t]["file"] for t in requested_tools])
        copied_dirs = set()
        helper_files_copied = set()
        
        print(f"\n📁 Copying {len(tool_files)} tool file(s)...")
        for tool_file in tool_files:
            src = tools_library_dir / tool_file
            dst = agent_dir / tool_file
            
            if not src.exists():
                raise FileNotFoundError(f"Tool file not found: {src}")
            
            # Create parent directory if needed (e.g., fathom_tools/, slack_tools/)
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            # Track which subdirectories we're using
            if '/' in tool_file or '\\' in tool_file:
                tool_dir = str(Path(tool_file).parent).replace('\\', '/')
                copied_dirs.add(tool_dir)
            
            shutil.copy(src, dst)
            print(f"  ✅ Copied {tool_file}")
        
        # Copy __init__.py and _helpers.py for each subdirectory used
        for tool_dir in copied_dirs:
            # Copy __init__.py
            init_src = tools_library_dir / tool_dir / "__init__.py"
            if init_src.exists():
                init_dst = agent_dir / tool_dir / "__init__.py"
                shutil.copy(init_src, init_dst)
                print(f"  ✅ Copied {tool_dir}/__init__.py")
            
            # Copy _helpers.py if it exists
            helpers_src = tools_library_dir / tool_dir / "_helpers.py"
            if helpers_src.exists():
                helpers_dst = agent_dir / tool_dir / "_helpers.py"
                shutil.copy(helpers_src, helpers_dst)
                helper_files_copied.add(f"{tool_dir}/_helpers.py")
                print(f"  ✅ Copied {tool_dir}/_helpers.py (shared utilities)")
        
        # ✅ NEW: Get model config from environment or default
        model_name = os.getenv("AGENT_MODEL", "openai/gpt-4o")
        
        # Generate agent.py with LiteLlm
        print(f"\n🤖 Generating agent.py with model: {model_name}...")
        agent_code = generate_agent_code(
            agent_name=agent_name,
            description=description,
            tools_to_copy=tools_to_copy,
            workflow_description=workflow_description,
            model_name=model_name  # ✅ Pass model name
        )
        (agent_dir / "agent.py").write_text(agent_code)
        print(f"✅ Created agent.py")
        
        # ✅ NEW: Ensure OPENAI_API_KEY is in env_keys_needed if using OpenAI model
        if "openai" in model_name.lower() and "OPENAI_API_KEY" not in env_keys_needed:
            env_keys_needed.append("OPENAI_API_KEY")
        
        # Generate .env file with ACTUAL API key values
        print(f"\n🔐 Generating .env file...")
        env_content = generate_env_file(env_keys_needed, collected_env_data)
        (agent_dir / ".env").write_text(env_content)
        print(f"✅ Created .env with {len(env_keys_needed)} API key(s)")
        
        # Generate requirements.txt if dependencies exist
        files_created = ["__init__.py", "agent.py", ".env"]
        
        if all_dependencies:
            req_content = "google-adk\n" + "\n".join(sorted(all_dependencies))
            (agent_dir / "requirements.txt").write_text(req_content)
            files_created.append("requirements.txt")
            print(f"✅ Created requirements.txt")
            
            # AUTO-INSTALL DEPENDENCIES
            print(f"\n📦 Installing {len(all_dependencies)} package(s)...")
            
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install"] + list(all_dependencies),
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    print(f"   ✅ All dependencies installed successfully!\n")
                    install_status = "success"
                else:
                    print(f"   ⚠️  Some packages failed to install")
                    install_status = "partial"
            except Exception as e:
                print(f"   ⚠️  Auto-install failed: {e}\n")
                install_status = "error"
        else:
            install_status = "not_needed"
        
        # Show which API keys were populated
        populated_keys = [key for key in env_keys_needed if key in collected_env_data]
        
        print(f"\n✨ Agent creation complete!")
        print(f"   📁 Location: {agent_dir}")
        print(f"   🤖 Model: {model_name}")
        print(f"   🔧 Tools: {len(requested_tools)}")
        print(f"   🔑 API Keys: {len(populated_keys)}")
        print(f"   📦 Dependencies: {len(all_dependencies)}")
        
        return {
            "status": "success",
            "agent_name": agent_name,
            "agent_directory": str(agent_dir),
            "model": model_name,
            "tools_included": requested_tools,
            "files_created": files_created,
            "api_keys_populated": populated_keys,
            "dependencies": list(all_dependencies),
            "install_status": install_status,
            "next_steps": [
                f"✅ Agent created with {len(populated_keys)} API key(s) configured!",
                f"🤖 Using model: {model_name}",
                f"1. Review: {agent_dir}",
                f"2. Run: adk web",
                f"3. Select: '{agent_name}'",
                f"4. Test the workflow!"
            ]
        }
        
    except Exception as e:
        # Cleanup on failure
        if agent_dir.exists():
            shutil.rmtree(agent_dir)
        
        import traceback
        return {
            "status": "error",
            "message": f"Failed to create agent: {str(e)}",
            "traceback": traceback.format_exc()
        }


def generate_agent_code(
    agent_name: str,
    description: str,
    tools_to_copy: Dict[str, Any],
    workflow_description: str,
    model_name: str = "openai/gpt-4o"  
) -> str:
    """Generate agent.py code with LiteLlm and proper imports."""
    
    # Group tools by source file
    tools_by_file = {}
    for tool_name, tool_info in tools_to_copy.items():
        # Handle both old format (file.py) and new format (dir/file.py)
        file_path = tool_info["file"]
        # Remove .py extension and convert to import path
        import_path = file_path.replace(".py", "").replace("/", ".").replace("\\", ".")
        function_name = tool_info["function"]
        
        if import_path not in tools_by_file:
            tools_by_file[import_path] = []
        tools_by_file[import_path].append(function_name)
    
    # Generate imports
    import_lines = []
    for import_path, functions in tools_by_file.items():
        import_lines.append(f"from .{import_path} import {', '.join(functions)}")
    
    imports_str = "\n".join(import_lines)
    tools_list = ", ".join([tool_info["function"] for tool_info in tools_to_copy.values()])
    
    
    agent_code = f'''"""
{agent_name}

{description}

Generated by V1 Meta-Agent
"""

import os
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
{imports_str}

# Load model from environment or use default
model_name = os.getenv("AGENT_MODEL", "{model_name}")

root_agent = Agent(
    name="{agent_name}",
    model=LiteLlm(model=model_name),
    description="""{description}""",
    instruction="""
{workflow_description}

Always follow this workflow step-by-step and provide clear feedback after each action.
""",
    tools=[
        {tools_list}
    ]
)
'''
    
    return agent_code


def generate_env_file(env_vars: list, env_values: dict = None) -> str:
    """Generate .env file with actual API key values."""
    
    lines = ["# Generated by V1 Meta-Agent", ""]
    
    # ✅ NEW: Always add OPENAI_API_KEY first if present
    if "OPENAI_API_KEY" in env_values:
        openai_info = env_values["OPENAI_API_KEY"]
        actual_value = openai_info.get('value', 'your_key_here') if isinstance(openai_info, dict) else openai_info
        lines.append("# OpenAI API Key (for LLM model)")
        if isinstance(openai_info, dict) and openai_info.get('description'):
            lines.append(f"# {openai_info['description']}")
        lines.append(f"OPENAI_API_KEY={actual_value}")
        lines.append("")
    
    for var in env_vars:
        # Skip OPENAI_API_KEY as we already added it
        if var == "OPENAI_API_KEY":
            continue
            
        # Use actual value if available
        if env_values and var in env_values:
            env_info = env_values[var]
            actual_value = env_info.get('value', 'your_key_here') if isinstance(env_info, dict) else env_info
            lines.append(f"# {var}")
            if isinstance(env_info, dict) and env_info.get('description'):
                lines.append(f"# {env_info['description']}")
            if isinstance(env_info, dict) and env_info.get('api_endpoint'):
                lines.append(f"# API: {env_info['api_endpoint']}")
            lines.append(f"{var}={actual_value}")
        else:
            lines.append(f"# {var}")
            lines.append(f"{var}=your_key_here")
        
        lines.append("")
    
    return "\n".join(lines)


def get_root_directory() -> Path:
    """Get the root directory of the current ADK project."""
    return Path(__file__).parent.parent


def start_requirements_collection() -> dict:
    """Start collecting requirements for a new agent."""
    global _requirements_state
    
    _requirements_state = {
        "active": True,
        "agent_spec": {},
        "env_data": {},
        "packages": [],
        "config": {}
    }
    
    return {
        "status": "started",
        "message": "Requirements collection started. Use add_* functions to collect data."
    }


def add_basic_requirement(field_name: str, field_value: str) -> dict:
    """Add a basic requirement field."""
    global _requirements_state
    
    if not _requirements_state["active"]:
        return {"status": "error", "message": "Call start_requirements_collection() first"}
    
    _requirements_state["agent_spec"][field_name] = field_value
    
    return {
        "status": "success",
        "field": field_name,
        "value": field_value
    }


def add_api_key_requirement(
    service_name: str, 
    key_value: str,
    description: str,
    api_endpoint: str
) -> dict:
    """Add an API key requirement with actual value."""
    global _requirements_state
    
    if not _requirements_state["active"]:
        return {"status": "error", "message": "Call start_requirements_collection() first"}
    
    _requirements_state["env_data"][service_name] = {
        "value": key_value,
        "description": description,
        "api_endpoint": api_endpoint
    }
    
    return {
        "status": "success",
        "service": service_name,
        "key_added": True,
        "message": f"API key for {service_name} has been securely stored"
    }


def add_package_dependency(package_name: str, version: str, description: str) -> dict:
    """Add a package dependency."""
    global _requirements_state
    
    if not _requirements_state["active"]:
        return {"status": "error", "message": "Call start_requirements_collection() first"}
    
    _requirements_state["packages"].append({
        "name": package_name,
        "version": version,
        "description": description
    })
    
    return {
        "status": "success",
        "package": package_name,
        "version": version
    }


def get_requirements_status() -> dict:
    """Get current requirements collection status."""
    global _requirements_state
    
    return {
        "active": _requirements_state["active"],
        "agent_spec": _requirements_state["agent_spec"],
        "env_keys_count": len(_requirements_state["env_data"]),
        "packages_count": len(_requirements_state["packages"])
    }


def list_created_agents() -> dict:
    """List all agents that have been created."""
    root_dir = get_root_directory()
    agents = []
    
    for item in root_dir.iterdir():
        if item.is_dir() and (item / "agent.py").exists():
            agents.append({
                "name": item.name,
                "path": str(item),
                "has_env": (item / ".env").exists(),
                "has_requirements": (item / "requirements.txt").exists()
            })
    
    return {
        "status": "success",
        "total_agents": len(agents),
        "agents": agents
    }


def view_agent_code(agent_name: str) -> dict:
    """View the code of a created agent."""
    root_dir = get_root_directory()
    agent_dir = root_dir / agent_name
    agent_file = agent_dir / "agent.py"
    
    if not agent_file.exists():
        return {
            "status": "error",
            "message": f"Agent '{agent_name}' not found"
        }
    
    return {
        "status": "success",
        "agent_name": agent_name,
        "code": agent_file.read_text()
    }