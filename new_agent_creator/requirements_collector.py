"""Interactive requirements collection for agent creation."""

from typing import Dict, Any, Optional
import json

class AgentRequirementsCollector:
    """Manages the collection of agent requirements from users."""
    
    REQUIRED_FIELDS = [
        "agent_name",
        "description",
        "instruction",
        "tools_description"
    ]
    
    OPTIONAL_FIELDS = {
        "model": "gemini-2.0-flash",
        "api_keys": {},
        "environment_vars": {},
        "external_dependencies": [],
        "config_settings": {}
    }
    
    def __init__(self):
        self.requirements = {}
        self.collection_status = {}
    
    def get_missing_fields(self) -> list:
        """Get list of required fields not yet provided."""
        return [
            field for field in self.REQUIRED_FIELDS 
            if field not in self.requirements or not self.requirements[field]
        ]
    
    def get_completion_status(self) -> dict:
        """Get current completion status."""
        missing = self.get_missing_fields()
        total = len(self.REQUIRED_FIELDS)
        completed = total - len(missing)
        
        return {
            "completed": completed,
            "total": total,
            "percentage": int((completed / total) * 100),
            "missing_fields": missing,
            "is_complete": len(missing) == 0
        }
    
    def add_requirement(self, field: str, value: Any) -> dict:
        """Add or update a requirement field."""
        self.requirements[field] = value
        self.collection_status[field] = "provided"
        
        status = self.get_completion_status()
        return {
            "status": "updated",
            "field": field,
            "completion": status
        }
    
    def add_api_key(self, service_name: str, key_value: str, description: str = "") -> dict:
        """Add API key configuration."""
        if "api_keys" not in self.requirements:
            self.requirements["api_keys"] = {}
        
        self.requirements["api_keys"][service_name] = {
            "key": key_value,
            "description": description
        }
        
        return {
            "status": "success",
            "message": f"API key for '{service_name}' added",
            "total_keys": len(self.requirements["api_keys"])
        }
    
    def add_env_var(self, var_name: str, var_value: str, description: str = "") -> dict:
        """Add environment variable."""
        if "environment_vars" not in self.requirements:
            self.requirements["environment_vars"] = {}
        
        self.requirements["environment_vars"][var_name] = {
            "value": var_value,
            "description": description
        }
        
        return {
            "status": "success",
            "message": f"Environment variable '{var_name}' added"
        }
    
    def add_dependency(self, package_name: str, version: str = "", purpose: str = "") -> dict:
        """Add external package dependency."""
        if "external_dependencies" not in self.requirements:
            self.requirements["external_dependencies"] = []
        
        self.requirements["external_dependencies"].append({
            "package": package_name,
            "version": version,
            "purpose": purpose
        })
        
        return {
            "status": "success",
            "message": f"Dependency '{package_name}' added",
            "total_dependencies": len(self.requirements["external_dependencies"])
        }
    
    def add_config(self, config_key: str, config_value: Any, description: str = "") -> dict:
        """Add configuration setting."""
        if "config_settings" not in self.requirements:
            self.requirements["config_settings"] = {}
        
        self.requirements["config_settings"][config_key] = {
            "value": config_value,
            "description": description
        }
        
        return {
            "status": "success",
            "message": f"Config '{config_key}' added"
        }
    
    def get_summary(self) -> dict:
        """Get complete summary of collected requirements."""
        status = self.get_completion_status()
        
        return {
            "completion_status": status,
            "requirements": self.requirements,
            "api_keys_count": len(self.requirements.get("api_keys", {})),
            "env_vars_count": len(self.requirements.get("environment_vars", {})),
            "dependencies_count": len(self.requirements.get("external_dependencies", [])),
            "ready_to_create": status["is_complete"]
        }
    
    def export_for_creation(self) -> dict:
        """Export requirements in format needed for agent creation."""
        if not self.get_completion_status()["is_complete"]:
            return {
                "status": "error",
                "message": "Cannot export - missing required fields",
                "missing": self.get_missing_fields()
            }
        
        # Merge tools description with API/config details
        tools_desc = self.requirements.get("tools_description", "")
        
        # Append API keys info to tools description
        if self.requirements.get("api_keys"):
            tools_desc += "\n\nAPI KEYS NEEDED:\n"
            for service, details in self.requirements["api_keys"].items():
                tools_desc += f"- {service}: {details.get('description', 'No description')}\n"
        
        # Append dependencies
        if self.requirements.get("external_dependencies"):
            tools_desc += "\n\nEXTERNAL PACKAGES:\n"
            for dep in self.requirements["external_dependencies"]:
                tools_desc += f"- {dep['package']} {dep.get('version', '')}: {dep.get('purpose', '')}\n"
        
        return {
            "status": "ready",
            "agent_spec": {
                "agent_name": self.requirements["agent_name"],
                "description": self.requirements["description"],
                "instruction": self.requirements["instruction"],
                "tools_description": tools_desc,
                "model": self.requirements.get("model", "gemini-2.0-flash")
            },
            "env_data": {
                "api_keys": self.requirements.get("api_keys", {}),
                "env_vars": self.requirements.get("environment_vars", {}),
                "config": self.requirements.get("config_settings", {})
            }
        }
    
    def reset(self) -> dict:
        """Reset all collected requirements."""
        self.requirements = {}
        self.collection_status = {}
        return {"status": "reset", "message": "All requirements cleared"}


# Global collector instance (session-based in production)
_collector = AgentRequirementsCollector()


def start_requirements_collection() -> dict:
    """Start fresh requirements collection session."""
    global _collector
    _collector = AgentRequirementsCollector()
    return {
        "status": "started",
        "message": "Requirements collection started. I'll guide you through the process.",
        "required_fields": _collector.REQUIRED_FIELDS
    }


def add_basic_requirement(field: str, value: str) -> dict:
    """Add a basic requirement field."""
    return _collector.add_requirement(field, value)


def add_api_key_requirement(service_name: str, key_placeholder: str, description: str = "") -> dict:
    """Add API key requirement."""
    return _collector.add_api_key(service_name, key_placeholder, description)


def add_env_variable(var_name: str, var_value: str, description: str = "") -> dict:
    """Add environment variable."""
    return _collector.add_env_var(var_name, var_value, description)


def add_package_dependency(package_name: str, version: str = "", purpose: str = "") -> dict:
    """Add external package dependency."""
    return _collector.add_dependency(package_name, version, purpose)


def add_configuration(config_key: str, config_value: str, description: str = "") -> dict:
    """Add configuration setting."""
    return _collector.add_config(config_key, config_value, description)


def get_requirements_status() -> dict:
    """Check current status of requirements collection."""
    return _collector.get_summary()


def finalize_requirements() -> dict:
    """Finalize and export requirements for agent creation."""
    return _collector.export_for_creation()