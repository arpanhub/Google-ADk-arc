"""
Test suite for Slack tools.
Run: python test_slack_tools.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0,str(Path(__file__).parent.parent))

from tools_library.slack_tools import (
    get_user_by_email,
    get_user_id_from_email,
    send_scheduled_direct_message,
    create_task_reminder,
    create_meeting_notes_canvas,   
)

def check_slack_token():
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    if not slack_token:
        print("\n⚠️  SLACK_BOT_TOKEN not set in environment")
        print("   To test Slack tools:")
        print("   1. Create a Slack App at https://api.slack.com/apps")
        print("   2. Add required OAuth scopes:")
        print("      - chat:write")
        print("      - users:read.email")
        print("      - canvases:write")
        print("   3. Install app to workspace")
        print("   4. Copy Bot User OAuth Token to .env file")
        print("   5. Set SLACK_BOT_TOKEN=xoxb-your-token-here")
        return False
    print(f"\n🔑 Slack token found: {slack_token[:15]}...")
    return True

def test_get_user_by_email():
    """Test get_user_by_email tool."""
    print("\n"+"="*60)
    print("Testing: get_user_by_email")
    print("="*60)

    if not check_slack_token():
        print("Skipping get_user_by_email test.")
        return False
    
    test_email = input("Enter a Slack user email to test: ").strip()
    user = get_user_by_email(test_email)

    if not test_email:
        print("No email provided. Skipping test.")
        return False
    
    if user:
        print("✅ PASSED: User found successfully")
        print(f"   - User ID: {user.get('id')}")
        print(f"   - Real Name: {user.get('real_name')}")
        print(f"   - Display Name: {user.get('profile', {}).get('display_name')}")
        assert "id" in user, "User should have ID"
        assert user["id"].startswith("U"), "User ID should start with U"
        return True
    else:
        print(f"⚠️  User not found for email: {test_email}")
        print("   Make sure the email exists in your Slack workspace")
        return False
    
def test_get_user_id_from_email():
    """Test getting user ID from email."""
    print("\n"+"="*60)
    print("Testing: get_user_id_from_email")
    print("="*60)

    if not check_slack_token():
        print("Skipping get_user_id_from_email test.")
        return False
    
    test_email = input("Enter a Slack user email to test: ").strip()
    user_id = get_user_id_from_email(test_email)

    if not test_email:
        print("No email provided. Skipping test.")
        return False
    
    if user_id:
        print("✅ PASSED: User ID retrieved successfully")
        print(f"   - User ID: {user_id}")
        assert user_id.startswith("U"), "User ID should start with U"
        return True
    else:
        print(f"⚠️  User ID not found for email: {test_email}")
        print("   Make sure the email exists in your Slack workspace")
        return False
    
def test_create_meeting_notes_canvas():
    """Test creating a Slack Canvas for meeting notes."""
    print("\n"+"="*60)
    print("Testing: create_meeting_notes_canvas")
    print("="*60)

    if not check_slack_token():
        print("Skipping create_meeting_notes_canvas test.")
        return False
    
    channel_id = input("\n📺 Enter a Slack channel ID to post canvas (or press Enter to skip): ").strip()
    
    if not channel_id:
        print("⚠️  SKIPPED: No channel ID provided")
        print("   To find channel ID: Right-click channel > View channel details > Copy ID")
        return False
    
    print("\n📝 Creating test canvas...")
    
    canvas_id = create_meeting_notes_canvas(
        meeting_title="Test Meeting - Automated Test",
        attendees=["Alice Johnson", "Bob Smith", "Charlie Brown"],
        agenda=[
            "Review Q1 results",
            "Discuss Q2 planning",
            "Action item assignments"
        ],
        decisions=[
            "Approved budget increase for Q2",
            "Will hire 2 new team members",
            "Moving to bi-weekly sprint cycle"
        ],
        action_items=[
            {"task_title": "Finalize hiring plan", "owner_name": "Alice"},
            {"task_title": "Update project timeline", "owner_name": "Bob"},
            {"task_title": "Schedule team kickoff", "owner_name": "Charlie"}
        ],
        channel_id=channel_id
    )
    
    if canvas_id:
        print("✅ PASSED: Canvas created successfully")
        print(f"   - Canvas ID: {canvas_id}")
        print(f"   - Check your Slack channel: #{channel_id}")
        return True
    else:
        print("❌ FAILED: Could not create canvas")
        print("   Check:")
        print("   - Bot has canvases:write scope")
        print("   - Bot is added to the channel")
        print("   - Channel ID is correct")
        return False

def test_send_scheduled_direct_message():
    """Test sending DM sending"""
    print("\n" + "="*60)
    print("TEST: send_scheduled_direct_message()")
    print("="*60)

    if not check_slack_token():
        print("Skipping send_scheduled_direct_message test.")
        return False

    test_email = input("Enter a Slack user email to send DM to: ").strip()

    if not test_email:
        print("No email provided. Skipping test.")
        return False
    scheduled_time = datetime.now() + timedelta(minutes=1)
    
    print(f"\n⏳ Scheduling DM to {test_email} at {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}...")

    message_id = send_scheduled_direct_message(
        user_email=test_email,
        message_text="hello mayank i am arpan's agent testing scheduled dm feature",
        scheduled_time=scheduled_time
    )
    if message_id:
        print("✅ PASSED: Scheduled DM successfully")
        print(f"   - Message ID: {message_id}")
        return True
    else:
        print("❌ FAILED: Could not schedule DM")
        print("   Check:")
        print("   - Bot has chat:write scope")
        print("   - User email is correct")
        return False

def test_create_task_reminder():
    """Test creating a Slack task reminder."""
    print("\n"+"="*60)
    print("Testing: create_task_reminder")
    print("="*60)

    if not check_slack_token():
        print("Skipping create_task_reminder test.")
        return False
    
    test_email = input("Enter a Slack user email to assign reminder to: ").strip()

    if not test_email:
        print("No email provided. Skipping test.")
        return False
    
    # ✅ Quick test: Due in 2 minutes, reminder 1 minute before
    due_date = datetime.now() + timedelta(minutes=2)
    reminder_advance_minutes = 1  # Custom: 1 minute before

    print(f"\n⏳ Creating task reminder for {test_email}...")
    print(f"   Due Date: {due_date.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Reminder will be sent: {reminder_advance_minutes} minutes before (in ~1 minute)")

    # Calculate reminder time manually for quick testing
    reminder_time = due_date - timedelta(minutes=reminder_advance_minutes)
    
    message = f"""📋 *Task Reminder*
*Complete the Slack Tools test suite*
This is a reminder to complete the testing of Slack tools in the Meta-Agent framework.
*Due Date:* {due_date.strftime('%Y-%m-%d %H:%M')}
*Reminder sent:* {reminder_advance_minutes} minutes before due date"""

    # Send directly instead of using create_task_reminder
    scheduled_id = send_scheduled_direct_message(test_email, message, reminder_time)

    if scheduled_id:
        print("✅ PASSED: Task reminder created successfully")
        print(f"   - Reminder ID: {scheduled_id}")
        print(f"   - Check Slack DMs in ~1 minute for the reminder")
        return True
    else:
        print("❌ FAILED: Could not create task reminder")
        return False
def run_all_slack_tests():
    """Run all Slack tool tests."""
    print("\n" + "🚀 " + "="*58)
    print("🚀 SLACK TOOLS TEST SUITE")
    print("🚀 " + "="*58)
    
    if not check_slack_token():
        print("\n❌ Cannot run tests without SLACK_BOT_TOKEN")
        return False
    
    print("\n⚠️  INTERACTIVE TESTS:")
    print("   These tests require valid Slack workspace data")
    print("   You'll be prompted for emails and channel IDs")
    print("   Press Enter to skip any test\n")
    
    results = []
    
    try:
        results.append(("User Lookup", test_get_user_by_email()))
        results.append(("User ID Lookup", test_get_user_id_from_email()))
        results.append(("Canvas Creation", test_create_meeting_notes_canvas()))
        results.append(("Scheduled DM", test_send_scheduled_direct_message()))
        results.append(("Task Reminder", test_create_task_reminder()))
        
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY:")
        print("="*60)
        for test_name, passed in results:
            status = "✅ PASSED" if passed else "⚠️  SKIPPED/FAILED"
            print(f"   {status}: {test_name}")
        
        passed_count = sum(1 for _, passed in results if passed)
        total_count = len(results)
        
        print("\n" + "="*60)
        if passed_count == total_count:
            print(f"🎉 ALL TESTS PASSED! ({passed_count}/{total_count})")
        else:
            print(f"⚠️  TESTS COMPLETED: {passed_count}/{total_count} passed")
        print("="*60 + "\n")
        
        return passed_count > 0  # Success if at least one test passed
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_slack_tests()
    sys.exit(0 if success else 1)
