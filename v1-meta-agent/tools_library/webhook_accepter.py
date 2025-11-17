"""
Webhook Accepter Tool
"""

import threading
from flask import Flask, request
from .fathom_tools import recieve_fathom_webhook


# destination URL: http://localhost:5000/fathom-webhook


def start_server():
    """Starts a simple Flask server to accept Fathom webhook payloads."""
    app = Flask(__name__)

    @app.route('/fathom-webhook', methods=['POST'])
    def handle_webhook():
        payload = request.get_json()
        # print("Received webhook payload:", payload)
        output = recieve_fathom_webhook(payload)
        return output, 200

    print("Starting webhook server on port 5000...")
    app.run(port=5000)

def launch_server():
    """Launches the webhook server in a background thread."""
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    return {"status": "success", "message": "Webhook server started and ready to accept payloads."}

# Usage:
if __name__ == "__main__":
    status = launch_server()
    print(status)
    # Your main process can do other tasks here, or simply wait
    # Example: block until the server exits (optional)
    while True:
        pass
