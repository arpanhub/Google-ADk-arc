from google.adk.agents import Agent
from .code_generator import create_agent_from_spec
from .agent_fixer import analyze_and_fix_agent, view_agent_code, list_created_agents
from .requirements_collector import (
    start_requirements_collection,
    add_basic_requirement,
    add_api_key_requirement,
    add_env_variable,
    add_package_dependency,
    add_configuration,
    get_requirements_status,
    finalize_requirements
)

def create_new_agent(
    agent_name: str,
    description: str,
    instruction: str,
    tools_description: str,
    model: str = "gemini-2.0-flash"
) -> dict:
    """Create a new ADK agent from specifications."""
    spec = {
        "agent_name": agent_name,
        "description": description,
        "instruction": instruction,
        "tools_spec": tools_description,
        "model": model
    }
    
    return create_agent_from_spec(spec)


def fix_agent_error(
    agent_name: str,
    error_message: str,
    additional_notes: str = ""
) -> dict:
    """Fix a broken agent by analyzing the error and regenerating code."""
    return analyze_and_fix_agent(agent_name, error_message, additional_notes)


def show_agent_code(agent_name: str) -> dict:
    """Display the current code of an agent for review."""
    return view_agent_code(agent_name)


def list_agents() -> dict:
    """List all agents created by this agent creator."""
    return list_created_agents()


# New guided creation tools
def begin_agent_creation() -> dict:
    """Start guided agent creation process with requirements collection."""
    return start_requirements_collection()


def set_agent_basic_info(field_name: str, field_value: str) -> dict:
    """Set basic agent information (agent_name, description, instruction, tools_description).
    
    Args:
        field_name: One of: agent_name, description, instruction, tools_description
        field_value: The value for that field
    """
    return add_basic_requirement(field_name, field_value)


def add_api_key(service_name: str, key_placeholder: str, description: str = "") -> dict:
    """Add API key requirement for external services.
    
    Args:
        service_name: Name of service (e.g., SLACK_BOT_TOKEN, FATHOM_API_KEY)
        key_placeholder: Placeholder or actual key value
        description: What this API key is used for
    """
    return add_api_key_requirement(service_name, key_placeholder, description)


def add_environment_variable(var_name: str, var_value: str, description: str = "") -> dict:
    """Add environment variable configuration."""
    return add_env_variable(var_name, var_value, description)


def add_external_package(package_name: str, version: str = "", purpose: str = "") -> dict:
    """Add external Python package dependency.
    
    Args:
        package_name: PyPI package name (e.g., slack_sdk, requests)
        version: Optional version requirement (e.g., >=1.0.0)
        purpose: What this package is used for
    """
    return add_package_dependency(package_name, version, purpose)


def add_config_setting(config_key: str, config_value: str, description: str = "") -> dict:
    """Add configuration setting for the agent."""
    return add_configuration(config_key, config_value, description)


def check_requirements_status() -> dict:
    """Check current progress of requirements collection."""
    return get_requirements_status()


def create_agent_from_requirements() -> dict:
    """Finalize requirements and create the agent.
    
    Only works if all required fields are collected.
    """
    export = finalize_requirements()
    
    if export["status"] == "error":
        return export
    
    # Create agent using collected requirements
    result = create_agent_from_spec(export["agent_spec"])
    
    # TODO: Also write .env file with API keys and env vars
    if result["status"] == "success":
        result["environment_data"] = export["env_data"]
        result["message"] += "\n\nNOTE: Add API keys and environment variables to the agent's .env file."
    
    return result


root_agent = Agent(
    name="agent_creator_v2",
    model="gemini-2.0-flash",
    description="Creates ADK agents using guided requirements collection or quick creation.",
    instruction=r"""You are the Agent Creator. You help users build Google ADK agents.
 
WHEN USER WANTS TO CREATE AN AGENT:

Step 1: Start collection
ALWAYS call begin_agent_creation() first

Step 2: Collect basic info (ASK ONE AT A TIME)
- Call set_agent_basic_info("agent_name", value)
- Call set_agent_basic_info("description", value)
- Call set_agent_basic_info("instruction", value)
- Call set_agent_basic_info("tools_description", value)

Step 3: Collect extras (if needed)
Ask: "Does this need API keys?"
- If yes: call add_api_key(name, placeholder, description)
Ask: "What Python packages?"
- If any: call add_external_package(name, version, purpose)

Step 4: Check progress
Call check_requirements_status() to see what's missing

Step 5: Create
When status shows 100% complete, call create_agent_from_requirements()

FIXING AGENTS:
User says "fix [agent_name]" → call fix_agent_error(agent_name, error_msg)

VIEWING:
"show code" → call show_agent_code(agent_name)
"list agents" → call list_agents()

Also refer the docs at https://google.github.io/adk-docs/ , https://google.github.io/adk-docs/tutorials/ , https://google.github.io/adk-docs/get-started/quickstart/
IMPORTANT RULES:
- ALWAYS start with begin_agent_creation()
- Collect info ONE FIELD AT A TIME
- Use check_requirements_status() before creating
- Don't skip the guided workflow for complex agents""",
    tools=[
        begin_agent_creation,
        set_agent_basic_info,
        add_api_key,
        add_environment_variable,
        add_external_package,
        add_config_setting,
        check_requirements_status,
        create_agent_from_requirements,
        create_new_agent,
        fix_agent_error,
        show_agent_code,
        list_agents
    ]
)