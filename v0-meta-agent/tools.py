import os
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Import code writer agent
try:
    from .code_writer_agent.agent import (
        write_tool_implementation,
        validate_generated_code,
        infer_parameters_heuristic
    )
    CODE_WRITER_AVAILABLE = True
except ImportError:
    CODE_WRITER_AVAILABLE = False
    print("⚠️  Code Writer Agent not available - will use skeleton templates")


# State management for requirements collection
_requirements_state = {
    "active": False,
    "agent_spec": {},
    "env_data": {},
    "packages": [],
    "config": {}
}


def get_root_directory() -> Path:
    """Get the root directory where agents should be created."""
    current_file = Path(__file__).resolve()
    # Navigate up to getting_started directory
    root = current_file.parent.parent
    return root


def start_requirements_collection() -> dict:
    """Start guided agent creation process with requirements collection."""
    global _requirements_state
    _requirements_state = {
        "active": True,
        "agent_spec": {
            "agent_name": None,
            "description": None,
            "instruction": None,
            "tools_description": None,
            "model": "gemini-2.0-flash"
        },
        "env_data": {},
        "packages": [],
        "config": {}
    }
    
    return {
        "status": "success",
        "message": "Requirements collection started. Please provide: agent_name, description, instruction, tools_description"
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


def add_api_key_requirement(
    service_name: str, 
    key_value: str,
    description: str,
    api_endpoint: str
) -> dict:
    """
    Add API key requirement for external services with actual key value and endpoint.
    
    Args:
        service_name: Name of the API key environment variable (e.g., "WEATHER_API_KEY")
        key_value: Actual API key value provided by user
        description: Description of what this API key is for
        api_endpoint: The API endpoint URL (with {{placeholders}} for dynamic values)
    
    Returns:
        dict: Status of the operation
    """
    global _requirements_state
    
    if not _requirements_state["active"]:
        return {"status": "error", "message": "Requirements collection not started."}
    
    _requirements_state["env_data"][service_name] = {
        "value": key_value,  # Store actual value, not placeholder
        "description": description if description else "",
        "api_endpoint": api_endpoint if api_endpoint else ""  # Store endpoint info
    }
    
    return {
        "status": "success",
        "message": f"Added API key: {service_name} with endpoint information",
        "endpoint_captured": bool(api_endpoint)
    }

def add_package_dependency(generate_tool_with_openaipackage_name: str, version: str, purpose: str) -> dict:
    """
    Add external Python package dependency.
    
    Args:
        package_name: Name of the package (e.g., "requests")
        version: Version specification (e.g., ">=2.31.0" or empty string for latest)
        purpose: Why this package is needed
    
    Returns:
        dict: Status of the operation
    """
    global _requirements_state
    
    if not _requirements_state["active"]:
        return {"status": "error", "message": "Requirements collection not started."}
    
    # Handle empty version string
    version_str = version if version and version.strip() else ""
    package_spec = f"{package_name}{version_str}" if version_str else package_name
    
    _requirements_state["packages"].append({
        "package": package_spec,
        "purpose": purpose if purpose else ""
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


def parse_tools_from_description(tools_description: str) -> list:
    """Parse tool descriptions and generate tool function stubs."""
    tools = []
    
    # Split by common separators
    tool_lines = [line.strip() for line in tools_description.split(',') if line.strip()]
    
    for tool_desc in tool_lines:
        # Extract tool name (first word or before colon/dash)
        if ':' in tool_desc:
            parts = tool_desc.split(':', 1)
            tool_name = parts[0].strip()
            description = parts[1].strip() if len(parts) > 1 else tool_desc
        elif '-' in tool_desc:
            parts = tool_desc.split('-', 1)
            tool_name = parts[0].strip()
            description = parts[1].strip() if len(parts) > 1 else tool_desc
        else:
            tool_name = tool_desc.strip()
            description = tool_desc
        
        tool_name = tool_name.replace(' ', '_').lower()
        
        # Clean up non-alphanumeric except underscore
        tool_name = ''.join(c for c in tool_name if c.isalnum() or c == '_')
        
        # Ensure doesn't start with number
        if tool_name and tool_name[0].isdigit():
            tool_name = 'tool_' + tool_name
        
        if tool_name:
            tools.append({
                "name": tool_name,
                "description": description
            })
    
    return tools


def generate_init_file() -> str:
    """Generate the __init__.py file content."""
    return """from .agent import root_agent

__all__ = ["root_agent"]
"""


def generate_fallback_skeleton_simple(tool_name: str, description: str) -> str:
    """Simple fallback skeleton."""
    return f'''def {tool_name}(input_data: str) -> dict:
    """
    {description}
    
    Args:
        input_data (str): Input parameter
    
    Returns:
        dict: Result of {tool_name}
    """
    # TODO: Implement {tool_name}
    return {{"status": "not_implemented", "message": "TODO: Implementation needed"}}
'''

def generate_tool_with_openai(
    tool_name: str,
    tool_description: str,
    agent_context: dict
) -> dict:
    """
    Generate a complete tool implementation using OpenAI Code Writer.
    
    Args:
        tool_name: Name of the tool function
        tool_description: What the tool should do
        agent_context: Context about the agent being built
    
    Returns:
        dict: Generated code and metadata
    """
    if not CODE_WRITER_AVAILABLE:
        return {
            "status": "error",
            "message": "Code Writer not available",
            "code": generate_fallback_skeleton_simple(tool_name, tool_description)
        }
    
    # Infer parameters
    params = infer_parameters_heuristic(tool_name, tool_description)
    
    # Build enhanced context string with API endpoints
    context_parts = []
    
    if agent_context.get("packages"):
        pkgs = [p.get('package', '') for p in agent_context['packages']]
        context_parts.append(f"Required packages: {', '.join(pkgs)}")
    
    if agent_context.get("api_keys"):
        context_parts.append(f"Available API keys (from env): {', '.join(agent_context['api_keys'])}")
    
    # ✨ NEW: Add API endpoint information
    if agent_context.get("env_data"):
        context_parts.append("\nAPI Endpoint Information:")
        for key_name, key_info in agent_context["env_data"].items():
            if key_info.get("api_endpoint"):
                context_parts.append(f"- {key_name}: {key_info['api_endpoint']}")
                context_parts.append(f"  Description: {key_info.get('description', 'N/A')}")
    
    if agent_context.get("description"):
        context_parts.append(f"\nAgent purpose: {agent_context['description']}")
    
    context_str = "\n".join(context_parts)
    
    # Generate code with enhanced context
    result = write_tool_implementation(
        tool_name=tool_name,
        tool_description=tool_description,
        input_parameters=json.dumps(params),
        expected_output="dict with success status and result data",
        context=context_str
    )
    
    if result["status"] == "success":
        # Validate generated code
        validation = validate_generated_code(result["code"])
        if validation["valid"]:
            return {
                "status": "success",
                "code": result["code"],
                "source": "openai",
                "tokens": result.get("tokens_used", 0)
            }
        else:
            print(f"⚠️  Generated code invalid: {validation['error']}")
            return {
                "status": "fallback",
                "code": result.get("fallback_code", generate_fallback_skeleton_simple(tool_name, tool_description)),
                "source": "fallback",
                "error": validation["error"]
            }
    else:
        return {
            "status": "fallback",
            "code": result.get("fallback_code", generate_fallback_skeleton_simple(tool_name, tool_description)),
            "source": "fallback",
            "error": result.get("message", "Unknown error")
        }

def generate_agent_code_with_openai(spec: dict) -> str:
    """
    Enhanced agent code generation using OpenAI for tool implementations.
    """
    tools = parse_tools_from_description(spec["tools_description"])
    
    tool_functions = []
    tool_names = []
    imports = set(["from google.adk.agents import Agent", "from typing import Optional, Dict, Any"])
    
    # ✨ ENHANCED: Include env_data with API endpoints
    agent_context = {
        "agent_name": spec.get("agent_name"),
        "description": spec.get("description"),
        "packages": _requirements_state.get("packages", []),
        "api_keys": list(_requirements_state.get("env_data", {}).keys()),
        "env_data": _requirements_state.get("env_data", {})  # ✨ NEW: Pass full env data including endpoints
    }
    
    print(f"\n🤖 Generating {len(tools)} tools using OpenAI Code Writer...\n")
    
    for i, tool in enumerate(tools, 1):
        func_name = tool["name"]
        tool_names.append(func_name)
        
        print(f"  [{i}/{len(tools)}] ⏳ Generating: {func_name}...")
        
        # Call OpenAI to generate implementation
        result = generate_tool_with_openai(
            tool_name=func_name,
            tool_description=tool["description"],
            agent_context=agent_context
        )
        
        if result["status"] == "success":
            code = result["code"]
            tool_functions.append(code)
            
            # Extract imports from generated code
            for line in code.split('\n'):
                line_stripped = line.strip()
                if line_stripped.startswith('import ') or line_stripped.startswith('from '):
                    imports.add(line_stripped)
            
            print(f"  [{i}/{len(tools)}] ✅ Generated: {func_name} (OpenAI, {result.get('tokens', 0)} tokens)")
        else:
            # Fallback to skeleton
            code = result["code"]
            tool_functions.append(code)
            print(f"  [{i}/{len(tools)}] ⚠️  Fallback skeleton: {func_name}")
    
    print("\n✨ Code generation complete!\n")
    
    # Generate full agent file
    imports_section = '\n'.join(sorted(imports))
    
    agent_code = f'''{imports_section}


{chr(10).join(tool_functions)}


root_agent = Agent(
    name="{spec["agent_name"]}",
    model="{spec.get("model", "gemini-2.0-flash")}",
    description="{spec["description"]}",
    instruction="""{spec["instruction"]}""",
    tools=[{", ".join(tool_names)}],
)
'''
    
    return agent_code

def generate_env_file(env_data: dict) -> str:
    """
    Generate .env file content with actual API key values.
    
    Args:
        env_data: Dictionary of environment variables with values and descriptions
    
    Returns:
        str: Complete .env file content with real values
    """
    lines = ["# Google ADK API Key", "GOOGLE_API_KEY=your_google_api_key_here", ""]
    
    for key, data in env_data.items():
        # Add description as comment
        if data.get('description'):
            lines.append(f"# {data['description']}")
        
        # Add API endpoint as comment if available
        if data.get('api_endpoint'):
            lines.append(f"# API Endpoint: {data['api_endpoint']}")
        
        # Add actual key value (not placeholder!)
        lines.append(f"{key}={data['value']}")
        lines.append("")  # Empty line for readability
    
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
    """Finalize requirements and create the agent with OpenAI-generated code and auto-installed dependencies."""
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
        
        # Generate agent.py with OpenAI
        agent_code = generate_agent_code_with_openai(spec)
        agent_file = agent_dir / "agent.py"
        agent_file.write_text(agent_code)
        
        # Generate and write .env with ACTUAL API key values
        env_content = generate_env_file(_requirements_state["env_data"])
        env_file = agent_dir / ".env"
        env_file.write_text(env_content)
        
        # Generate and write requirements.txt if packages exist
        install_status = "not_needed"
        install_message = "No additional dependencies required"
        install_location = "N/A"
        
        if _requirements_state["packages"]:
            req_content = generate_requirements_file(_requirements_state["packages"])
            req_file = agent_dir / "requirements.txt"
            req_file.write_text(req_content)
            
            # AUTO-INSTALL DEPENDENCIES
            package_count = len(_requirements_state["packages"])
            print(f"\n📦 Installing {package_count} package(s) to current Python environment...")
            print(f"   Python: {sys.executable}")
            print(f"   Running: pip install -r {req_file}\n")
            
            try:
                # Run pip install in the same Python environment
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    print("   ✅ All dependencies installed successfully!\n")
                    
                    # Show where packages were installed
                    site_packages = Path(sys.executable).parent.parent / "Lib" / "site-packages"
                    if site_packages.exists():
                        install_location = str(site_packages)
                        print(f"   📍 Packages installed to: {install_location}\n")
                    
                    install_status = "success"
                    install_message = f"Successfully installed {package_count} package(s)"
                else:
                    print(f"   ⚠️  Warning: Some dependencies failed to install")
                    print(f"   Error output:\n{result.stderr}\n")
                    install_status = "partial"
                    install_message = "Some dependencies failed - please install manually"
                    
            except subprocess.TimeoutExpired:
                print("   ⚠️  Installation timeout - please install manually\n")
                install_status = "timeout"
                install_message = "Installation timed out after 5 minutes"
                
            except Exception as e:
                print(f"   ⚠️  Could not auto-install dependencies: {e}\n")
                print(f"   Please run manually: pip install -r {req_file}\n")
                install_status = "error"
                install_message = f"Auto-install failed: {str(e)}"
        
        # Reset state
        _requirements_state["active"] = False
        
        # Build next steps based on install status
        next_steps = [
            "1. ✅ API keys are already set in .env file (no manual update needed!)",
            "2. Review generated implementations in agent.py",
        ]
        
        # Add install step only if auto-install failed
        if install_status in ["partial", "timeout", "error"]:
            next_steps.append(f"3. Install dependencies manually: pip install -r requirements.txt")
            next_steps.append(f"4. Run 'adk web' and select '{spec['agent_name']}'")
        else:
            next_steps.append(f"3. Run 'adk web' and select '{spec['agent_name']}'")
        
        # Build files created list
        files_created = ["__init__.py", "agent.py", ".env"]
        if _requirements_state["packages"]:
            files_created.append("requirements.txt")
        
        return {
            "status": "success",
            "message": f"✅ Agent '{spec['agent_name']}' created successfully with OpenAI-generated code!",
            "agent_directory": str(agent_dir),
            "files_created": files_created,
            "dependency_install_status": install_status,
            "dependency_install_message": install_message,
            "dependency_install_location": install_location,
            "packages_installed": len(_requirements_state.get("packages", [])),
            "env_file_ready": bool(_requirements_state.get("env_data")),
            "next_steps": next_steps
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