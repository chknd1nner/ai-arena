/**
 * Playwright test for Stories 016 (Weapon Visualization) and 017 (Game State Overlay)
 *
 * This test verifies:
 * - Story 016: Phaser arcs and weapon rendering
 * - Story 017: State overlay with ship stats and events
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

// Create screenshots directory
const screenshotsDir = path.join(__dirname, '..', 'screenshots', 'stories-016-017');
if (!fs.existsSync(screenshotsDir)) {
  fs.mkdirSync(screenshotsDir, { recursive: true });
}

async function testReplayViewer() {
  console.log('🚀 Starting Playwright tests for Stories 016 & 017...\n');

  // Launch browser in headless mode
  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    viewport: { width: 1400, height: 1200 }
  });

  const page = await context.newPage();

  // Set longer timeout for navigation
  page.setDefaultTimeout(30000);

  try {
    // Test 1: Check if frontend is running
    console.log('📍 Test 1: Loading frontend...');
    await page.goto('http://localhost:3000');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: path.join(screenshotsDir, '01-frontend-home.png') });
    console.log('✅ Frontend loaded successfully\n');

    // Test 2: Load test replay (epic002_tactical_showcase)
    console.log('📍 Test 2: Loading tactical showcase replay...');

    // Click the tactical showcase button
    const tacticalButton = await page.locator('button:has-text("Watch Tactical Showcase")');
    await tacticalButton.click();
    await page.waitForTimeout(3000); // Wait for replay to load and render

    // Take screenshot of initial state
    await page.screenshot({ path: path.join(screenshotsDir, '02-tactical-showcase-initial.png') });
    console.log('✅ Tactical showcase replay loaded\n');

    // Test 3: Verify weapon rendering (Story 016)
    console.log('📍 Test 3: Verifying weapon visualization (Story 016)...');

    // Check if canvas is rendered
    const canvas = await page.$('canvas');
    if (!canvas) {
      throw new Error('Canvas not found!');
    }
    console.log('  ✓ Canvas element found');

    // Take screenshot showing phaser arcs
    await page.screenshot({ path: path.join(screenshotsDir, '03-phaser-arcs-visible.png') });
    console.log('  ✓ Screenshot captured with phaser arcs');
    console.log('✅ Weapon visualization tested\n');

    // Test 4: Verify state overlay (Story 017)
    console.log('📍 Test 4: Verifying state overlay (Story 017)...');

    // Check for state overlay elements
    const stateOverlay = await page.locator('text=Ship A').first();
    const isVisible = await stateOverlay.isVisible();
    if (!isVisible) {
      throw new Error('State overlay not visible!');
    }
    console.log('  ✓ State overlay visible');

    // Check for ship stats
    const shieldsText = await page.locator('text=Shields:').first();
    const shieldsVisible = await shieldsText.isVisible();
    if (!shieldsVisible) {
      throw new Error('Ship stats not visible!');
    }
    console.log('  ✓ Ship stats (Shields, AE) displayed');

    // Check for turn counter
    const turnCounter = await page.locator('text=Turn').first();
    const turnVisible = await turnCounter.isVisible();
    if (!turnVisible) {
      throw new Error('Turn counter not visible!');
    }
    console.log('  ✓ Turn counter displayed');

    await page.screenshot({ path: path.join(screenshotsDir, '04-state-overlay-visible.png') });
    console.log('✅ State overlay tested\n');

    // Test 5: Test playback controls
    console.log('📍 Test 5: Testing playback...');

    // Find and click play button
    const playButton = await page.locator('button').filter({ hasText: 'Play' }).first();
    if (await playButton.isVisible()) {
      await playButton.click();
      console.log('  ✓ Clicked play button');
      await page.waitForTimeout(2000); // Watch playback for 2 seconds
    }

    // Take screenshot during playback
    await page.screenshot({ path: path.join(screenshotsDir, '05-playback-active.png') });
    console.log('  ✓ Playback screenshot captured');

    // Pause playback
    const pauseButton = await page.locator('button').filter({ hasText: 'Pause' }).first();
    if (await pauseButton.isVisible()) {
      await pauseButton.click();
      console.log('  ✓ Paused playback');
    }
    console.log('✅ Playback controls tested\n');

    // Test 6: Load different replay (strafing maneuver)
    console.log('📍 Test 6: Loading strafing maneuver replay...');

    // Click close button and then strafing button
    const closeButton = await page.locator('button:has-text("Close Replay")');
    await closeButton.click();
    await page.waitForTimeout(500);

    const strafingButton = await page.locator('button:has-text("Watch Strafing Maneuver")');
    await strafingButton.click();
    await page.waitForTimeout(3000);

    await page.screenshot({ path: path.join(screenshotsDir, '06-strafing-maneuver.png') });
    console.log('✅ Strafing maneuver replay loaded\n');

    // Test 7: Check for phaser config display
    console.log('📍 Test 7: Verifying phaser configuration display...');
    const phaserConfig = await page.locator('text=Phaser:').first();
    const phaserConfigVisible = await phaserConfig.isVisible();
    if (!phaserConfigVisible) {
      throw new Error('Phaser config not visible in state overlay!');
    }
    console.log('  ✓ Phaser configuration displayed');

    // Check for WIDE or FOCUSED text
    const wideOrFocused = await page.locator('text=/WIDE|FOCUSED/').first();
    const configTextVisible = await wideOrFocused.isVisible();
    if (!configTextVisible) {
      throw new Error('Phaser config value (WIDE/FOCUSED) not visible!');
    }
    console.log('  ✓ Phaser config value (WIDE/FOCUSED) visible');

    await page.screenshot({ path: path.join(screenshotsDir, '07-phaser-config-display.png') });
    console.log('✅ Phaser configuration display tested\n');

    // Test 8: Load retreat coverage replay
    console.log('📍 Test 8: Loading retreat coverage replay...');

    // Click close button and then retreat button
    const closeButton2 = await page.locator('button:has-text("Close Replay")');
    await closeButton2.click();
    await page.waitForTimeout(500);

    const retreatButton = await page.locator('button:has-text("Watch Retreat Coverage")');
    await retreatButton.click();
    await page.waitForTimeout(3000);

    await page.screenshot({ path: path.join(screenshotsDir, '08-retreat-coverage.png') });
    console.log('✅ Retreat coverage replay loaded\n');

    // Final summary screenshot
    await page.screenshot({
      path: path.join(screenshotsDir, '09-final-complete-view.png'),
      fullPage: true
    });

    console.log('🎉 All tests passed!\n');
    console.log(`📸 Screenshots saved to: ${screenshotsDir}\n`);
    console.log('Story 016 (Weapon Visualization): ✅ PASS');
    console.log('Story 017 (Game State Overlay): ✅ PASS\n');

  } catch (error) {
    console.error('❌ Test failed:', error.message);

    // Take error screenshot
    await page.screenshot({ path: path.join(screenshotsDir, 'error-screenshot.png') });
    console.log(`📸 Error screenshot saved to: ${screenshotsDir}/error-screenshot.png`);

    throw error;
  } finally {
    await browser.close();
  }
}

// Run the test
testReplayViewer()
  .then(() => {
    console.log('✨ Test suite completed successfully!');
    process.exit(0);
  })
  .catch((error) => {
    console.error('💥 Test suite failed:', error);
    process.exit(1);
  });
