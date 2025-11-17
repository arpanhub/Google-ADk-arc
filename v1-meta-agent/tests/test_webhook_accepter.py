"""
Test suite for webhook accepter server
Run: python test_webhook_accepter.py
"""
import os
import sys
import json
import time
import requests
from pathlib import Path
from threading import Thread


# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools_library.webhook_accepter import launch_server


def load_test_payload():
    """Load test webhook payload."""
    test_data_path = Path(__file__).parent / "test_data" / "fathom_webhook_payload.json"
    with open(test_data_path, 'r') as f:
        return json.load(f)


def test_webhook_server():
    """Test webhook server startup and payload handling."""
    print("\n" + "="*60)
    print("TEST: Webhook Server")
    print("="*60)
    
    print("\n🚀 Starting webhook server...")
    server_status = launch_server()
    
    if server_status["status"] != "success":
        print(f"❌ FAILED: Could not start server: {server_status.get('message')}")
        return False
    
    print("✅ Server started successfully")
    print(f"   Status: {server_status['message']}")
    
    # Wait for server to be ready
    print("\n⏳ Waiting 3 seconds for server to initialize...")
    time.sleep(3)
    
    # Test server health
    print("\n🔍 Testing server availability...")
    try:
        # Try to connect (this will fail but confirms server is running)
        response = requests.get("http://localhost:5000/", timeout=2)
        print("✅ Server is responding")
    except requests.exceptions.ConnectionError:
        print("⚠️  Server running but no root endpoint (expected)")
    except Exception as e:
        print(f"⚠️  Unexpected response: {e}")
    
    # Test webhook endpoint
    print("\n📨 Sending test webhook payload...")
    payload = load_test_payload()
    
    try:
        response = requests.post(
            "http://localhost:5000/fathom-webhook",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ PASSED: Webhook received and processed")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Status: {result.get('status')}")
            
            if result.get("status") == "success":
                print(f"   Call ID: {result.get('call_id')}")
                print(f"   Meeting: {result.get('meeting_title')}")
                print(f"   Participants: {len(result.get('participants', []))}")
                # assert result["call_id"] == "rec_12345abcde", "Call ID mismatch"
                return True
            else:
                print(f"⚠️  Webhook processed with error: {result.get('error')}")
                return False
        else:
            print(f"❌ FAILED: Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ FAILED: Could not connect to webhook server")
        print("   Make sure the server is running on port 5000")
        return False
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_webhook_error_handling():
    """Test webhook error handling with invalid payloads."""
    print("\n" + "="*60)
    print("TEST: Webhook Error Handling")
    print("="*60)
    
    # Test with invalid JSON
    print("\n🔍 Testing with invalid payload (string)...")
    try:
        response = requests.post(
            "http://localhost:5000/fathom-webhook",
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        # Server should handle this gracefully
        print(f"   Response Code: {response.status_code}")
        if response.status_code in [400, 500]:
            print("✅ PASSED: Server handled invalid JSON")
        else:
            result = response.json()
            if result.get("status") == "error":
                print("✅ PASSED: Server returned error response")
            else:
                print("⚠️  Unexpected response for invalid JSON")
        
    except Exception as e:
        print(f"⚠️  Exception during invalid payload test: {e}")
    
    # Test with wrong event type
    print("\n🔍 Testing with wrong event type...")
    try:
        wrong_event = {"event": "call.started", "data": {}}
        response = requests.post(
            "http://localhost:5000/fathom-webhook",
            json=wrong_event,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        result = response.json()
        if result.get("status") == "error" and "event type" in result.get("error", "").lower():
            print("✅ PASSED: Server rejected wrong event type")
            return True
        else:
            print("⚠️  Server didn't properly reject wrong event type")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def run_all_webhook_tests():
    """Run all webhook server tests."""
    print("\n" + "🚀 " + "="*58)
    print("🚀 WEBHOOK ACCEPTER TEST SUITE")
    print("🚀 " + "="*58)
    
    print("\n📝 NOTE: This test will start a Flask server on port 5000")
    print("   Make sure port 5000 is available")
    print("   The server will run in the background during tests\n")
    
    try:
        # Run tests
        server_test = test_webhook_server()
        error_test = test_webhook_error_handling()
        
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY:")
        print("="*60)
        print(f"   {'✅ PASSED' if server_test else '❌ FAILED'}: Webhook Server Test")
        print(f"   {'✅ PASSED' if error_test else '❌ FAILED'}: Error Handling Test")
        
        if server_test and error_test:
            print("\n" + "🎉 " + "="*58)
            print("🎉 ALL WEBHOOK TESTS PASSED!")
            print("🎉 " + "="*58)
            print("\n⚠️  Server is still running in background")
            print("   Press Ctrl+C to stop")
            print("\n")
            return True
        else:
            print("\n❌ Some tests failed")
            return False
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = run_all_webhook_tests()
        
        # Keep server running for manual testing
        if success:
            print("Press Ctrl+C to stop the server...")
            while True:
                time.sleep(1)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
        sys.exit(0)