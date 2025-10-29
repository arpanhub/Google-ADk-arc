from utils.validator import validate_agent_config

test_config = {
    "agent_name": "test_agent",
    "description": "Test",
    "instruction": "Test instruction",
    "tools": []
}

result = validate_agent_config(test_config)
print(f"Validator works: {result.agent_name}")
print(f"Model: {result.model}")
print(f"Tool names: {result.tool_names}")