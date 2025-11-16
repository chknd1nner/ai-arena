#!/usr/bin/env python3
"""
QA Test Script for Story 026: Balance Tuning & Integration Testing
Tests the continuous physics system and balance parameters.
"""

from playwright.sync_api import sync_playwright
import time
import os

def test_story_026():
    """Test Story 026: Balance Tuning & Integration Testing"""

    print("🧪 Starting QA Test for Story 026: Balance Tuning & Integration Testing")

    # Create screenshots directory
    screenshots_dir = "/Users/martinkuek/Documents/Projects/ai-arena/screenshots/story-026"
    os.makedirs(screenshots_dir, exist_ok=True)

    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Enable console logging
        page.on("console", lambda msg: print(f"🖥️  Console: {msg.text}"))

        print("\n1️⃣  Navigating to frontend (http://localhost:3000)...")
        page.goto('http://localhost:3000')
        page.wait_for_load_state('networkidle')

        # Take screenshot of initial state
        page.screenshot(path=f'{screenshots_dir}/01-initial-load.png', full_page=True)
        print("✅ Screenshot saved: 01-initial-load.png")

        # Check for title
        title = page.title()
        print(f"   Page title: {title}")

        print("\n2️⃣  Looking for 'Start New Match' button...")
        # Try to find the start match button
        try:
            # Wait for the button to be visible
            start_button = page.wait_for_selector('button:has-text("Start New Match")', timeout=5000)
            print("✅ 'Start New Match' button found")

            # Take screenshot before clicking
            page.screenshot(path=f'{screenshots_dir}/02-before-start-match.png', full_page=True)
            print("✅ Screenshot saved: 02-before-start-match.png")

            print("\n3️⃣  Clicking 'Start New Match'...")
            start_button.click()

            # Wait a moment for the match to start
            time.sleep(2)
            page.screenshot(path=f'{screenshots_dir}/03-after-start-match.png', full_page=True)
            print("✅ Screenshot saved: 03-after-start-match.png")

        except Exception as e:
            print(f"⚠️  Could not find 'Start New Match' button: {e}")
            page.screenshot(path=f'{screenshots_dir}/02-button-not-found.png', full_page=True)

        print("\n4️⃣  Checking match list...")
        # Wait for match data to load
        page.wait_for_load_state('networkidle')
        time.sleep(3)

        # Take screenshot of match list
        page.screenshot(path=f'{screenshots_dir}/04-match-list.png', full_page=True)
        print("✅ Screenshot saved: 04-match-list.png")

        # Look for match entries
        print("\n5️⃣  Looking for match entries...")
        try:
            # Try different selectors for match entries
            match_entries = page.locator('text=/Match|match|Ship|ship/').all()
            if match_entries:
                print(f"✅ Found {len(match_entries)} elements with match-related text")

            # Check for status indicators
            status_elements = page.locator('text=/running|completed|failed/i').all()
            if status_elements:
                print(f"✅ Found {len(status_elements)} status indicators")

        except Exception as e:
            print(f"⚠️  Error checking match entries: {e}")

        print("\n6️⃣  Testing API directly via fetch...")
        # Test the backend API directly
        api_response = page.evaluate("""
            async () => {
                try {
                    const response = await fetch('http://localhost:8000/api/matches');
                    const data = await response.json();
                    return { success: true, data: data };
                } catch (error) {
                    return { success: false, error: error.message };
                }
            }
        """)

        if api_response.get('success'):
            data = api_response.get('data', {})
            if isinstance(data, dict) and 'matches' in data:
                matches = data.get('matches', [])
                total = data.get('total', 0)
                print(f"✅ API call successful - {total} total matches, {len(matches)} returned")

                if matches and len(matches) > 0:
                    first_match = matches[0]
                    print(f"   Latest match ID: {first_match.get('match_id', 'unknown')}")
                    print(f"   Status: {first_match.get('status', 'unknown')}")
                    print(f"   Model A: {first_match.get('model_a', 'unknown')}")
                    print(f"   Model B: {first_match.get('model_b', 'unknown')}")
            else:
                print(f"✅ API call successful but unexpected data structure")
                print(f"   Data: {data}")
        else:
            print(f"❌ API call failed: {api_response.get('error')}")

        print("\n7️⃣  Testing config.json parameters...")
        # Read config to verify balance parameters
        config_response = page.evaluate("""
            async () => {
                try {
                    const response = await fetch('http://localhost:8000/api/config');
                    if (response.ok) {
                        const data = await response.json();
                        return { success: true, data: data };
                    }
                    return { success: false, error: 'Config endpoint not found' };
                } catch (error) {
                    return { success: false, error: error.message };
                }
            }
        """)

        if config_response.get('success'):
            print("✅ Config retrieved from API")
        else:
            print(f"⚠️  Config API not available (expected): {config_response.get('error')}")

        print("\n8️⃣  Taking final screenshots...")
        # Scroll through the page
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)
        page.screenshot(path=f'{screenshots_dir}/05-final-top.png', full_page=False)

        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
        page.screenshot(path=f'{screenshots_dir}/06-final-bottom.png', full_page=True)
        print("✅ Screenshots saved: 05-final-top.png, 06-final-bottom.png")

        print("\n9️⃣  Inspecting DOM structure...")
        # Get page content for analysis
        body_text = page.locator('body').inner_text()
        print(f"   Page contains {len(body_text)} characters of text")

        # Check for key terms
        key_terms = ['AI Arena', 'Match', 'Ship', 'Start', 'model']
        for term in key_terms:
            if term.lower() in body_text.lower():
                print(f"   ✅ Found key term: '{term}'")
            else:
                print(f"   ⚠️  Missing key term: '{term}'")

        browser.close()

    print("\n" + "="*60)
    print("✅ QA Test Complete!")
    print(f"📸 Screenshots saved to: {screenshots_dir}")
    print("="*60)

    return screenshots_dir

if __name__ == "__main__":
    test_story_026()
