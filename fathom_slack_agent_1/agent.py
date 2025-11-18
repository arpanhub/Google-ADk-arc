from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, HTTPException, Request
from google.adk.agents import Agent
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import Dict
from typing import Optional, Dict, Any
import os
import uvicorn


import os
from typing import Dict
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from fastapi import FastAPI, HTTPException, Request
import uvicorn

app = FastAPI()

def receive_fathom_data(payload: dict) -> dict:
    """
    Receives the Fathom payload and posts a message to Slack.

    Args:
        payload (dict): The Fathom data payload to be processed.

    Returns:
        dict: A dictionary containing the success status and result data.
    """
    slack_token = os.getenv("Slack")
    if not slack_token:
        raise EnvironmentError("Slack API token is not set in environment variables.")

    client = WebClient(token=slack_token)
    channel_id = "#general"  # Example channel ID, should be replaced with actual channel

    try:
        # Validate payload structure
        if not isinstance(payload, dict) or 'event' not in payload:
            raise ValueError("Invalid payload structure. 'event' key is required.")

        # Construct the message to be sent to Slack
        message = f"Received Fathom event: {payload['event']}"

        # Send message to Slack
        response = client.chat_postMessage(channel=channel_id, text=message)

        # Check if the message was sent successfully
        if response['ok']:
            return {"success": True, "result": "Message sent to Slack successfully."}
        else:
            return {"success": False, "result": "Failed to send message to Slack."}

    except SlackApiError as e:
        # Handle Slack API errors
        return {"success": False, "result": f"Slack API error: {e.response['error']}"}
    except ValueError as ve:
        # Handle payload validation errors
        return {"success": False, "result": f"Payload error: {str(ve)}"}
    except Exception as e:
        # Handle any other exceptions
        return {"success": False, "result": f"An unexpected error occurred: {str(e)}"}

@app.post("/fathom")
async def fathom_webhook(request: Request):
    """
    Endpoint to receive Fathom webhook data.

    Args:
        request (Request): The incoming request object containing the Fathom payload.

    Returns:
        dict: A dictionary containing the success status and result data.
    """
    try:
        payload = await request.json()
        result = receive_fathom_data(payload)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['result'])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import Dict
from fastapi import FastAPI, HTTPException
import uvicorn

app = FastAPI()

def post_to_slack(payload: dict) -> Dict[str, str]:
    """
    Posts the received data to a specified Slack channel.

    Args:
        payload (dict): The data to be posted to Slack. Must contain 'channel' and 'text' keys.

    Returns:
        dict: A dictionary containing the success status and result data.
    """
    # Retrieve the Slack API token from environment variables
    slack_token = os.getenv('Slack')
    if not slack_token:
        raise ValueError("Slack API token is not set in environment variables.")

    # Initialize the Slack client
    client = WebClient(token=slack_token)

    try:
        # Validate payload structure
        if 'channel' not in payload or 'text' not in payload:
            raise ValueError("Payload must contain 'channel' and 'text' keys.")

        # Attempt to post the message to the specified Slack channel
        response = client.chat_postMessage(
            channel=payload['channel'],
            text=payload['text']
        )
        return {"status": "success", "data": response['message']}
    
    except SlackApiError as e:
        # Handle Slack API errors
        return {"status": "error", "error": str(e.response['error'])}
    except Exception as e:
        # Handle general exceptions
        return {"status": "error", "error": str(e)}

@app.post("/post-to-slack")
async def post_to_slack_endpoint(payload: dict):
    """
    FastAPI endpoint to receive data and post it to Slack.

    Args:
        payload (dict): The data to be posted to Slack.

    Returns:
        dict: A dictionary containing the success status and result data.
    """
    try:
        result = post_to_slack(payload)
        if result['status'] == 'error':
            raise HTTPException(status_code=400, detail=result['error'])
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the FastAPI application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


root_agent = Agent(
    name="fathom_slack_agent_1",
    model="gemini-2.0-flash",
    description="Generate a basic agent that can receive Fathom data and post to Slack",
    instruction="""agent should accept Fathom payload and post that data in to the slack channel workspace""",
    tools=[receive_fathom_data, post_to_slack],
)
