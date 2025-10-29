from typing import Dict, Any, List, Optional
from .utils.validator import validate_agent_config, ToolDefinition, ToolParam
from .utils.file_manager import write_agent_files


def parse_agent_requirements(user_description: str) -> dict:
    """Parse natural language agent description into structured config.
    
    This is a placeholder that returns a basic structure.
    In production, this would use LLM to parse user intent.
    
    Args:
        user_description: Natural language description of desired agent
        
    Returns:
        dict: Preliminary agent configuration
    """
    # Placeholder logic - will be enhanced with LLM
    return {
        "status": "parsed",
        "suggestion": {
            "agent_name": "new_agent",
            "description": user_description[:100],
            "instruction": f"You are an agent that: {user_description}",
            "tools": []
        },
        "message": "Basic configuration created. Please refine with add_tool or finalize."
    }


def add_tool_to_config(
    config: dict,
    tool_name: str,
    tool_description: str,
    parameters: Optional[List[Dict[str, str]]] = None,
    return_type: str = "dict"
) -> dict:
    """Add a tool definition to agent configuration.
    
    Args:
        config: Current agent configuration
        tool_name: Name of the tool function
        tool_description: What the tool does
        parameters: List of dicts with 'name', 'type', 'description'
        return_type: Return type of the tool
        
    Returns:
        dict: Updated configuration with status
    """
    if parameters is None:
        parameters = []
    
    # Convert params to ToolParam objects
    params_list = [
        ToolParam(
            name=p.get("name", "arg"),
            type=p.get("type", "str"),
            description=p.get("description", "")
        )
        for p in parameters
    ]
    
    # Build parameter string for function signature
    param_str = ", ".join([f"{p.name}: {p.type}" for p in params_list])
    
    tool_def = ToolDefinition(
        name=tool_name,
        parameters=param_str,
        return_type=return_type,
        description=tool_description,
        params_list=params_list,
        return_description=f"Result of {tool_name}",
        default_return='{"status": "success"}' if return_type == "dict" else '""'
    )
    
    if "tools" not in config:
        config["tools"] = []
    
    config["tools"].append(tool_def.dict())
    
    return {
        "status": "success",
        "message": f"Tool '{tool_name}' added to configuration",
        "config": config
    }


def create_agent_files(agent_config: dict) -> dict:
    """Validate and create agent files from configuration.
    
    Args:
        agent_config: Complete agent configuration
        
    Returns:
        dict: Status and file paths created
    """
    try:
        # Validate configuration
        validated_config = validate_agent_config(agent_config)
        
        # Convert to dict for template rendering
        render_config = {
            "agent_name": validated_config.agent_name,
            "model": validated_config.model,
            "description": validated_config.description,
            "instruction": validated_config.instruction,
            "tools": [t.dict() for t in validated_config.tools],
            "tool_names": validated_config.tool_names
        }
        
        # Write files
        file_paths = write_agent_files(validated_config.agent_name, render_config)
        
        return {
            "status": "success",
            "message": f"Agent '{validated_config.agent_name}' created successfully",
            "files": file_paths,
            "agent_name": validated_config.agent_name
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create agent: {str(e)}"
        }


def validate_config(agent_config: dict) -> dict:
    """Validate agent configuration without creating files.
    
    Args:
        agent_config: Agent configuration to validate
        
    Returns:
        dict: Validation result
    """
    try:
        validated = validate_agent_config(agent_config)
        return {
            "status": "valid",
            "message": "Configuration is valid",
            "config": validated.dict()
        }
    except Exception as e:
        return {
            "status": "invalid",
            "message": str(e)
        }