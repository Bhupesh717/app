import requests
import sys
from datetime import datetime
import time

class APITester:
    def __init__(self, base_url="https://post-pusher.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, description=""):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n{'='*60}")
        print(f"🔍 Test {self.tests_run}: {name}")
        print(f"   Description: {description}")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - Status: {response.status_code}")
                self.test_results.append({
                    "test": name,
                    "status": "PASSED",
                    "status_code": response.status_code
                })
            else:
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                self.test_results.append({
                    "test": name,
                    "status": "FAILED",
                    "expected": expected_status,
                    "actual": response.status_code,
                    "response": response.text[:200]
                })

            try:
                response_json = response.json()
                print(f"   Response preview: {str(response_json)[:150]}...")
                return success, response_json
            except:
                return success, {}

        except requests.exceptions.Timeout:
            print(f"❌ FAILED - Request timeout after 30 seconds")
            self.test_results.append({
                "test": name,
                "status": "FAILED",
                "error": "Timeout"
            })
            return False, {}
        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
            self.test_results.append({
                "test": name,
                "status": "FAILED",
                "error": str(e)
            })
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test(
            "Root Endpoint",
            "GET",
            "",
            200,
            description="Check if API is accessible"
        )

    def test_get_schedule_settings(self):
        """Test getting schedule settings"""
        return self.run_test(
            "Get Schedule Settings",
            "GET",
            "schedule/settings",
            200,
            description="Fetch current schedule configuration"
        )

    def test_get_schedule_status(self):
        """Test getting schedule status"""
        return self.run_test(
            "Get Schedule Status",
            "GET",
            "schedule/status",
            200,
            description="Fetch current schedule status and next run time"
        )

    def test_update_schedule_settings(self):
        """Test updating schedule settings"""
        success, _ = self.run_test(
            "Update Schedule Settings - Disable",
            "PUT",
            "schedule/settings",
            200,
            data={"enabled": False},
            description="Disable scheduled notifications"
        )
        
        if success:
            # Re-enable it
            self.run_test(
                "Update Schedule Settings - Enable",
                "PUT",
                "schedule/settings",
                200,
                data={"enabled": True},
                description="Re-enable scheduled notifications"
            )
        
        return success

    def test_update_schedule_time(self):
        """Test updating schedule time"""
        return self.run_test(
            "Update Schedule Time",
            "PUT",
            "schedule/settings",
            200,
            data={"schedule_time": "10:00"},
            description="Change notification time to 10:00 UTC"
        )

    def test_get_notification_logs(self):
        """Test getting notification logs"""
        return self.run_test(
            "Get Notification Logs",
            "GET",
            "notifications/logs",
            200,
            description="Fetch notification history"
        )

    def test_manual_trigger(self):
        """Test manual notification trigger"""
        print("\n⚠️  This test will send a real notification and may take 10-15 seconds...")
        success, response = self.run_test(
            "Manual Trigger Notification",
            "POST",
            "notifications/trigger",
            200,
            description="Manually trigger a notification (sends real notification)"
        )
        
        if success:
            print(f"   Notification ID: {response.get('notification_id', 'N/A')}")
            print(f"   Message: {response.get('message', 'N/A')}")
        
        return success, response

    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*60}")
        print(f"📊 TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        print(f"{'='*60}")
        
        if self.tests_run - self.tests_passed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if result["status"] == "FAILED":
                    print(f"   - {result['test']}")
                    if "error" in result:
                        print(f"     Error: {result['error']}")
                    elif "actual" in result:
                        print(f"     Expected: {result['expected']}, Got: {result['actual']}")

def main():
    print("="*60)
    print("🚀 Starting Backend API Tests")
    print("="*60)
    print(f"Base URL: https://post-pusher.preview.emergentagent.com")
    print(f"Testing WordPress to OneSignal Push Notification Service")
    print("="*60)

    tester = APITester()

    # Test 1: Root endpoint
    print("\n📍 PHASE 1: Basic Connectivity")
    tester.test_root_endpoint()

    # Test 2: Schedule settings
    print("\n📍 PHASE 2: Schedule Configuration")
    tester.test_get_schedule_settings()
    tester.test_get_schedule_status()
    tester.test_update_schedule_settings()
    tester.test_update_schedule_time()

    # Test 3: Notification logs
    print("\n📍 PHASE 3: Notification Logs")
    tester.test_get_notification_logs()

    # Test 4: Manual trigger (this sends a real notification)
    print("\n📍 PHASE 4: Manual Notification Trigger")
    print("⚠️  WARNING: This will send a real push notification!")
    trigger_success, trigger_response = tester.test_manual_trigger()
    
    if trigger_success:
        print("\n⏳ Waiting 3 seconds for notification to be logged...")
        time.sleep(3)
        
        # Verify the notification was logged
        print("\n📍 PHASE 5: Verify Notification Logged")
        success, logs = tester.test_get_notification_logs()
        if success and logs:
            print(f"\n✅ Found {len(logs)} notification(s) in history")
            if len(logs) > 0:
                latest = logs[0]
                print(f"   Latest notification:")
                print(f"   - Title: {latest.get('post_title', 'N/A')}")
                print(f"   - Status: {latest.get('status', 'N/A')}")
                print(f"   - Recipients: {latest.get('recipient_count', 'N/A')}")

    # Print summary
    tester.print_summary()

    # Return exit code
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
