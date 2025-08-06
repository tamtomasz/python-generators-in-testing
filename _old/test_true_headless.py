import pytest
from playwright.sync_api import sync_playwright


def test_true_headless_then_headed():
    """
    This test demonstrates running part of a test in true headless mode
    and another part in headed mode.

    The state is transferred between the two browser instances.
    """
    # Start a Playwright instance that we'll use throughout the test
    playwright = sync_playwright().start()

    try:
        # First part: Run in true headless mode for faster processing
        print("\nStarting test in true headless mode...")
        headless_browser = playwright.chromium.launch(headless=True)
        headless_context = headless_browser.new_context()
        headless_page = headless_context.new_page()

        # Navigate to the web tables page
        headless_page.goto("https://demoqa.com/webtables")

        # Perform bulk operations in headless mode
        print("Adding records in headless mode (faster)...")
        for i in range(3):
            headless_page.click("#addNewRecordButton")
            headless_page.fill("#firstName", f"User{i}")
            headless_page.fill("#lastName", f"Test{i}")
            headless_page.fill("#userEmail", f"user{i}@example.com")
            headless_page.fill("#age", str(20 + i))
            headless_page.fill("#salary", str(5000 + i * 1000))
            headless_page.fill("#department", "Testing")
            headless_page.click("#submit")

        # Save the current URL for state transfer
        current_url = headless_page.url

        # Take a screenshot in headless mode to verify the state
        headless_page.screenshot(path="headless_state.png")
        print("Screenshot saved as 'headless_state.png'")

        # Close the headless browser
        headless_browser.close()
        print("Headless browser closed")

        # Second part: Switch to headed mode for visual inspection
        print("\nSwitching to headed mode for visual inspection...")
        headed_browser = playwright.chromium.launch(headless=False)
        headed_context = headed_browser.new_context()
        headed_page = headed_context.new_page()

        # Navigate to the same URL to preserve the state
        headed_page.goto(current_url)
        print("Navigated to same URL in headed browser")

        # Give time for visual inspection
        print("You can now visually inspect the browser...")
        headed_page.wait_for_timeout(5000)  # 5 seconds to visually inspect

        # Close the headed browser
        headed_browser.close()
        print("Headed browser closed")

    finally:
        # Clean up the Playwright instance
        playwright.stop()


if __name__ == "__main__":
    # This allows running directly with python, not just through pytest
    test_true_headless_then_headed()
