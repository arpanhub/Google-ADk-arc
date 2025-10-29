from typing import Dict, Any, List
from pydantic import BaseModel, Field, validator
import re


class ToolParam(BaseModel):
    name: str
    type: str
    description: str


class ToolDefinition(BaseModel):
    name: str
    parameters: str
    return_type: str = "dict"
    description: str
    params_list: List[ToolParam] = []
    return_description: str = "Operation result"
    default_return: str = "{}"
    
    @validator('name')
    def validate_name(cls, v):
        if not re.match(r'^[a-z_][a-z0-9_]*$', v):
            raise ValueError('Tool name must be valid Python identifier')
        return v


class AgentConfig(BaseModel):
    agent_name: str = Field(..., min_length=1)
    model: str = "gemini-2.0-flash"
    description: str
    instruction: str
    tools: List[ToolDefinition] = []
    
    @validator('agent_name')
    def validate_agent_name(cls, v):
        if not re.match(r'^[a-z_][a-z0-9_]*$', v):
            raise ValueError('Agent name must be valid directory name')
        return v
    
    @property
    def tool_names(self) -> str:
        return ", ".join([t.name for t in self.tools])


def validate_agent_config(config: Dict[str, Any]) -> AgentConfig:
    """Validate agent configuration.
    
    Args:
        config: Raw configuration dict
        
    Returns:
        Validated AgentConfig object
        
    Raises:
        ValidationError if config is invalid
    """
    return AgentConfig(**config)