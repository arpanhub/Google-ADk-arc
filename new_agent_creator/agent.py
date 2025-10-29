from google.adk.agents import Agent
from .code_generator import create_agent_from_spec

def create_new_agent(
    agent_name: str,
    description: str,
    instruction: str,
    tools_description: str,
    model: str = "gemini-2.0-flash"
) -> dict:
    """Create a new ADK agent from specifications.
    
    Uses LLM to generate complete agent code based on requirements.
    
    Args:
        agent_name: Name for the agent (lowercase_with_underscores)
        description: Brief description of agent purpose
        instruction: Detailed instructions for agent behavior
        tools_description: Natural language description of tools needed
        model: ADK model to use (default: gemini-2.0-flash)
        
    Returns:
        dict: Creation status and file paths
    """
    spec = {
        "agent_name": agent_name,
        "description": description,
        "instruction": instruction,
        "tools_spec": tools_description,
        "model": model
    }
    
    return create_agent_from_spec(spec)


root_agent = Agent(
    name="agent_creator_v2",
    model="gemini-2.0-flash",
    description="Creates new ADK agents using LLM code generation. Reference Google ADK documentation at [https://google.github.io/adk-docs/ , https://google.github.io/adk-docs/get-started/quickstart/, https://google.github.io/adk-docs/tutorials/agent-team/] for patterns and best practices.",
    instruction=r"""You are the Agent Creator - you help users build new Google ADK agents.

Process:
1. Gather requirements from user:
   - What should the agent do?
   - What tools/functions does it need? 
   - What tools/functions does it need?
   
2. Call create_new_agent with:
   - agent_name: lowercase_with_underscores
   - description: Brief summary
   - instruction: Detailed behavior guide
   - tools_description: Describe each tool needed in natural language
   
3. After creation, tell user the agent was created successfully and they need to restart 'adk web' to see it in the dropdown.

Example:
User: "I need a calculator"
You: "I'll create a calculator agent. What operations? (add, subtract, etc.)"
User: "Addition and subtraction"
You: *Call create_new_agent with tools_description="Two tools: add_numbers(num1: str, num2: str) for addition, subtract_numbers(num1: str, num2: str) for subtraction. Both return str with result."*
You: "Agent created successfully! Restart 'adk web' to use calculator_agent."

Be conversational and helpful. Guide users through the agent creation process step by step.""",
    tools=[create_new_agent]
)