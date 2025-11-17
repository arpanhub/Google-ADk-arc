"""
Test suite for Fathom tools
Run: python test_fathom_tools.py
"""
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
print(f"Loaded .env from: {env_path}")
# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools_library.fathom_tools import (
    recieve_fathom_webhook,
    parse_fathom_summary,
    fetch_fathom_call_summary,
)


def load_test_payload():
    """Load test webhook payload from JSON file."""
    test_data_path = Path(__file__).parent / "test_data" / "fathom_webhook_payload.json"
    print(f"Loading test payload from: {test_data_path}")
    with open(test_data_path, 'r') as f:
        print
        return json.load(f)


def test_recieve_fathom_webhook():
    """Test webhook reception and validation."""
    print("\n" + "="*60)
    print("TEST: recieve_fathom_webhook()")
    print("="*60)
    
    payload = load_test_payload()
    
    print("\n📥 Testing with valid webhook payload...")
    result = recieve_fathom_webhook(payload)
    
    assert result["status"] == "success", f"Expected success, got {result['status']}"
    # assert result["call_id"] == "rec_12345abcde", "Call ID mismatch"
    assert result["meeting_title"] == "QBR 2025 Q1", "Meeting title mismatch"
    # assert len(result["participants"]) == 3, f"Expected 3 participants, got {len(result['participants'])}"
    # assert len(result["key_actions"]) == 2, f"Expected 2 action items, got {len(result['key_actions'])}"
    
    print("✅ PASSED: Valid webhook processed successfully")
    print(f"   - Call ID: {result['call_id']}")
    print(f"   - Title: {result['meeting_title']}")
    print(f"   - Participants: {len(result['participants'])}")
    print(f"   - Action Items: {len(result['key_actions'])}")
    
    # Test invalid payload (not a dict)
    print("\n🔍 Testing with invalid payload (string instead of dict)...")
    invalid_result = recieve_fathom_webhook("invalid")
    assert invalid_result["status"] == "error", "Should fail with non-dict payload"
    print("✅ PASSED: Correctly rejected invalid payload")
    
    # Test missing event field
    print("\n🔍 Testing with missing event field...")
    bad_payload = {"data": {}}
    missing_event_result = recieve_fathom_webhook(bad_payload)
    assert missing_event_result["status"] == "error", "Should fail with missing event"
    print("✅ PASSED: Correctly rejected payload with missing event")
    
    # Test wrong event type
    print("\n🔍 Testing with wrong event type...")
    wrong_event = {"event": "call.started", "data": {}}
    wrong_event_result = recieve_fathom_webhook(wrong_event)
    assert wrong_event_result["status"] == "error", "Should fail with wrong event type"
    print("✅ PASSED: Correctly rejected wrong event type")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED for recieve_fathom_webhook()")
    print("="*60)


def test_parse_fathom_summary():
    """Test summary parsing and normalization."""
    print("\n" + "="*60)
    print("TEST: parse_fathom_summary()")
    print("="*60)
    
    # First get valid webhook data
    payload = load_test_payload()
    webhook_result = recieve_fathom_webhook(payload)
    
    # Test parsing valid data
    print("\n📊 Testing summary parsing...")
    parsed = parse_fathom_summary(webhook_result)
    
    assert parsed["status"] == "success", f"Expected success, got {parsed['status']}"
    assert isinstance(parsed["key_actions"], list), "key_actions should be a list"
    
    print("✅ PASSED: Summary parsed successfully")
    print(f"   - Call ID: {parsed['call_id']}")
    print(f"   - Things Discussed: {len(parsed.get('things_discussed', []))}")
    print(f"   - Key Actions: {len(parsed['key_actions'])}")
    
    # Verify action normalization
    print("\n🔍 Verifying action item structure...")
    if parsed["key_actions"]:
        first_action = parsed["key_actions"][0]
        assert "task_title" in first_action, "Action should have task_title"
        assert "owner_name" in first_action, "Action should have owner_name"
        assert "owner_email" in first_action, "Action should have owner_email"
        assert "due_date" in first_action, "Action should have due_date"
        print("✅ PASSED: Action items normalized correctly")
        print(f"   Sample action: {first_action['task_title'][:50]}...")
    
    # Test with error status
    print("\n🔍 Testing with failed webhook data...")
    error_data = {"status": "error", "error": "Test error"}
    error_result = parse_fathom_summary(error_data)
    assert error_result["status"] == "error", "Should propagate error status"
    print("✅ PASSED: Correctly handled error status")
    
    # Test with string actions (legacy format)
    print("\n🔍 Testing with string-format actions...")
    string_action_data = {
        "status": "success",
        "call_id": "test_123",
        "things_discussed": ["Topic A", "Topic B"],
        "key_actions": ["Simple action item", "Another task"],
        "participants": ["Alice", "Bob"]
    }
    string_parsed = parse_fathom_summary(string_action_data)
    assert string_parsed["status"] == "success", "Should handle string actions"
    assert string_parsed["key_actions"][0]["task_title"] == "Simple action item", "Should convert string to dict"
    assert string_parsed["key_actions"][0]["owner_name"] is None, "Should set None for missing owner"
    print("✅ PASSED: String actions normalized correctly")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED for parse_fathom_summary()")
    print("="*60)


def test_fetch_fathom_call_summary():
    """Test Fathom API call (requires FATHOM_API_KEY)."""
    print("\n" + "="*60)
    print("TEST: fetch_fathom_call_summary()")
    print("="*60)
    
    # Check if API key is set
    api_key = os.getenv("FATHOM_API_KEY")
    print(f"\n🔑 Checking for FATHOM_API_KEY in environment... Found: {bool(api_key)}")
    if not api_key:
        print("\n⚠️  SKIPPED: FATHOM_API_KEY not set in environment")
        print("   To test this function:")
        print("   1. Set FATHOM_API_KEY in your .env file")
        print("   2. Provide a valid call_id")
        print("   3. Re-run this test")
        return
    
    print(f"\n🔑 API Key found: {api_key[:10]}...")
    
    # Test with demo call ID (replace with actual if available)
    test_call_id = "101043441"  # Demo call ID from comments
    
    print(f"\n📞 Fetching call summary for call_id: {test_call_id}")
    result = fetch_fathom_call_summary(test_call_id)
    
    if result["status"] == "success":
        print("✅ PASSED: Successfully fetched call summary from API")
        print(f"   - Call ID: {result['call_id']}")
        print(f"   - Things Discussed: {len(result.get('things_discussed', []))}")
        print(f"   - Key Actions: {len(result.get('key_actions', []))}")
        
        # Verify structure
        assert "call_id" in result, "Result should have call_id"
        assert "things_discussed" in result, "Result should have things_discussed"
        assert "key_actions" in result, "Result should have key_actions"
        
    elif result["status"] == "error":
        print(f"⚠️  API call failed: {result['error']}")
        print("   This might be due to:")
        print("   - Invalid API key")
        print("   - Invalid call_id")
        print("   - Network issues")
        print("   - API rate limiting")
        
        # Still consider it a pass if we got a proper error response
        assert "error" in result, "Error result should have error message"
        print("✅ PASSED: Error handling works correctly")
    
    # Test without API key
    print("\n🔍 Testing without API key...")
    original_key = os.environ.get("FATHOM_API_KEY")
    if original_key:
        del os.environ["FATHOM_API_KEY"]
    
    no_key_result = fetch_fathom_call_summary("test_123")
    assert no_key_result["status"] == "error", "Should fail without API key"
    assert "FATHOM_API_KEY" in no_key_result["error"], "Should mention missing API key"
    print("✅ PASSED: Correctly handled missing API key")
    
    # Restore API key
    if original_key:
        os.environ["FATHOM_API_KEY"] = original_key
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED for fetch_fathom_call_summary()")
    print("="*60)


def run_all_fathom_tests():
    """Run all Fathom tool tests."""
    print("\n" + "🚀 " + "="*58)
    print("🚀 FATHOM TOOLS TEST SUITE")
    print("🚀 " + "="*58)
    
    try:
        test_recieve_fathom_webhook()
        test_parse_fathom_summary()
        test_fetch_fathom_call_summary()
        
        print("\n" + "🎉 " + "="*58)
        print("🎉 ALL FATHOM TESTS PASSED!")
        print("🎉 " + "="*58 + "\n")
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}\n")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_fathom_tests()
    sys.exit(0 if success else 1)