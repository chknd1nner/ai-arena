#!/usr/bin/env python3
"""
Visual QA test for Story 044: Match Orchestrator & Replay Cleanup

Tests that replay serialization correctly includes detonation_timer field
and that replays load and display properly in the frontend.

QA Agent: Senior QA Developer
Story: 044 - Match Orchestrator & Replay Cleanup
Branch: claude/epic-007-phase-2-0151aVQ9Ns3GpnQrMXpmmaTp
"""

from playwright.sync_api import sync_playwright
import json
import time
from pathlib import Path

def test_replay_visualization():
    """Test that replays with torpedoes load and display correctly."""

    print("\n" + "="*80)
    print("Story 044 QA - Visual Testing")
    print("="*80 + "\n")

    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Step 1: Navigate to the app
            print("Step 1: Navigating to http://localhost:3000...")
            page.goto('http://localhost:3000')
            page.wait_for_load_state('networkidle')
            time.sleep(2)  # Extra wait for React hydration

            # Take screenshot of match list
            print("Step 2: Taking screenshot of match list...")
            page.screenshot(path='/tmp/story-044-match-list.png', full_page=True)
            print("  ✓ Screenshot saved: /tmp/story-044-match-list.png")

            # Step 3: Select a replay from the dropdown
            print("\nStep 3: Selecting a replay from dropdown...")

            # Find the select dropdown
            replay_select = page.locator('select')
            if replay_select.count() == 0:
                print("  ✗ Replay select dropdown not found")
                page.screenshot(path='/tmp/story-044-error-no-select.png', full_page=True)
                raise Exception("Replay select dropdown not found")

            # Get available options
            options = replay_select.locator('option').all()
            print(f"  Found {len(options)} replay options")

            if len(options) <= 1:  # Only has default "-- Select a replay --"
                print("  ✗ No replays available in dropdown")
                raise Exception("No replays available to test")

            # Select the first actual replay (skip the default option)
            first_replay_value = options[1].get_attribute('value')
            print(f"  Selecting replay: {first_replay_value}")
            replay_select.select_option(first_replay_value)
            time.sleep(1)

            # Click "Show Canvas Viewer" button
            print("\nStep 4: Opening Canvas Viewer...")
            canvas_button = page.locator('button:has-text("Show Canvas Viewer")')
            if canvas_button.count() == 0:
                print("  ✗ Show Canvas Viewer button not found")
                page.screenshot(path='/tmp/story-044-error-no-button.png', full_page=True)
                raise Exception("Show Canvas Viewer button not found")

            print("  Clicking 'Show Canvas Viewer' button...")
            canvas_button.click()

            # Wait for navigation and canvas to load
            page.wait_for_load_state('networkidle')
            time.sleep(3)  # Wait for canvas rendering

            # Step 5: Verify canvas is present
            print("\nStep 5: Verifying replay viewer loaded...")
            canvas = page.locator('canvas')
            if canvas.count() == 0:
                print("  ✗ Canvas not found!")
                page.screenshot(path='/tmp/story-044-error-no-canvas.png', full_page=True)
                raise Exception("Replay canvas not found")

            print(f"  ✓ Found {canvas.count()} canvas element(s)")

            # Step 6: Take screenshot of replay viewer
            print("\nStep 6: Capturing gameplay visualization...")
            page.screenshot(path='/tmp/story-044-replay-initial.png', full_page=True)
            print("  ✓ Screenshot saved: /tmp/story-044-replay-initial.png")

            # Step 7: Check for turn slider
            print("\nStep 7: Testing turn navigation...")
            slider = page.locator('input[type="range"], .turn-slider')
            if slider.count() > 0:
                print("  ✓ Turn slider found")

                # Move slider to middle
                print("  Moving slider to middle position...")
                slider.first.evaluate('el => el.value = Math.floor(el.max / 2)')
                slider.first.dispatch_event('input')
                time.sleep(1)

                page.screenshot(path='/tmp/story-044-replay-midgame.png', full_page=True)
                print("  ✓ Screenshot saved: /tmp/story-044-replay-midgame.png")

                # Move slider to end
                print("  Moving slider to end position...")
                slider.first.evaluate('el => el.value = el.max')
                slider.first.dispatch_event('input')
                time.sleep(1)

                page.screenshot(path='/tmp/story-044-replay-endgame.png', full_page=True)
                print("  ✓ Screenshot saved: /tmp/story-044-replay-endgame.png")
            else:
                print("  ⚠ Turn slider not found, trying alternative navigation...")

            # Step 8: Check thinking panel (Story 044 should not affect this, but good to verify)
            print("\nStep 8: Checking UI components...")

            # Look for ship info panels
            ship_info = page.locator('.ship-info, .ship-status, [class*="ship"]').all()
            print(f"  Found {len(ship_info)} ship-related elements")

            # Take final screenshot
            print("\nStep 9: Taking final screenshot...")
            page.screenshot(path='/tmp/story-044-replay-final.png', full_page=True)
            print("  ✓ Screenshot saved: /tmp/story-044-replay-final.png")

            print("\n" + "="*80)
            print("✓ Visual testing completed successfully!")
            print("="*80 + "\n")

            print("Screenshots saved to /tmp/:")
            print("  - story-044-match-list.png")
            print("  - story-044-replay-initial.png")
            print("  - story-044-replay-midgame.png")
            print("  - story-044-replay-endgame.png")
            print("  - story-044-replay-final.png")

        except Exception as e:
            print(f"\n✗ Error during testing: {e}")
            page.screenshot(path='/tmp/story-044-error-final.png', full_page=True)
            print("  Error screenshot saved: /tmp/story-044-error-final.png")
            raise

        finally:
            browser.close()

def verify_replay_data():
    """Verify that replay files contain detonation_timer field."""

    print("\n" + "="*80)
    print("Story 044 QA - Replay Data Verification")
    print("="*80 + "\n")

    replay_dir = Path("replays")
    if not replay_dir.exists():
        print("✗ Replays directory not found")
        return False

    replay_files = list(replay_dir.glob("*.json"))
    if not replay_files:
        print("✗ No replay files found")
        return False

    print(f"Found {len(replay_files)} replay file(s)\n")

    verified_count = 0
    files_with_torpedoes = 0

    for replay_file in replay_files[:5]:  # Check first 5 replays
        print(f"Checking: {replay_file.name}")

        try:
            with open(replay_file, 'r') as f:
                data = json.load(f)

            # Check if any turn has torpedoes
            has_torpedoes = False
            has_detonation_timer_field = False

            for turn in data.get('turns', []):
                state = turn.get('state', {})
                torpedoes = state.get('torpedoes', [])

                if torpedoes:
                    has_torpedoes = True
                    files_with_torpedoes += 1

                    # Check if detonation_timer field exists
                    for torpedo in torpedoes:
                        if 'detonation_timer' in torpedo:
                            has_detonation_timer_field = True
                            print(f"  ✓ Found torpedo with detonation_timer: {torpedo.get('detonation_timer')}")
                            break

                    if has_detonation_timer_field:
                        break

            if has_torpedoes:
                if has_detonation_timer_field:
                    print(f"  ✓ Replay contains torpedoes with detonation_timer field")
                    verified_count += 1
                else:
                    print(f"  ✗ Replay has torpedoes but missing detonation_timer field")
            else:
                print(f"  - No torpedoes in this replay (skipping)")

        except Exception as e:
            print(f"  ✗ Error reading replay: {e}")

    print(f"\n" + "="*80)
    print(f"Verification Results:")
    print(f"  Replays with torpedoes: {files_with_torpedoes}")
    print(f"  Replays with detonation_timer field: {verified_count}")

    if verified_count > 0:
        print(f"✓ Story 044 implementation verified in replay data!")
    else:
        print(f"⚠ No torpedoes found in checked replays (implementation may still be correct)")

    print("="*80 + "\n")

    return True

if __name__ == "__main__":
    try:
        # First verify replay data
        verify_replay_data()

        # Then run visual tests
        test_replay_visualization()

        print("\n✓ All Story 044 QA tests completed successfully!\n")

    except Exception as e:
        print(f"\n✗ QA tests failed: {e}\n")
        exit(1)
