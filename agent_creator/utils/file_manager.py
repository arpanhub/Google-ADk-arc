import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any

BASE_DIR = Path(__file__).parent.parent.parent  # getting_started directory


def create_agent_directory(agent_name: str) -> Path:
    """Create agent directory in getting_started root.
    
    Args:
        agent_name: Name of the agent (will be directory name)
        
    Returns:
        Path to created directory
    """
    agent_dir = BASE_DIR / agent_name
    agent_dir.mkdir(exist_ok=True)
    return agent_dir


def write_agent_files(agent_name: str, config: Dict[str, Any]) -> Dict[str, str]:
    """Generate and write agent files from templates.
    
    Args:
        agent_name: Name of the agent
        config: Agent configuration dict
        
    Returns:
        Dict with file paths created
    """
    template_dir = Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(template_dir))
    
    agent_dir = create_agent_directory(agent_name)
    
    # Render agent.py
    agent_template = env.get_template("agent_template.py.j2")
    agent_content = agent_template.render(**config)
    agent_file = agent_dir / "agent.py"
    agent_file.write_text(agent_content, encoding='utf-8')
    
    # Render __init__.py
    init_template = env.get_template("init_template.py.j2")
    init_content = init_template.render()
    init_file = agent_dir / "__init__.py"
    init_file.write_text(init_content, encoding='utf-8')
    
    # Render .env
    env_template = env.get_template("env_template.py.j2")
    env_content = env_template.render(api_key=os.getenv("GOOGLE_API_KEY", ""))
    env_file = agent_dir / ".env"
    env_file.write_text(env_content, encoding='utf-8')
    
    return {
        "agent_py": str(agent_file),
        "init_py": str(init_file),
        "env": str(env_file)
    }