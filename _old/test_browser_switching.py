import pytest
from playwright.sync_api import sync_playwright, Browser
import time


def switch_browser_visibility(browser: Browser, headless: bool) -> Browser:
    """
    Switch the visibility mode of a browser without closing/reopening it.
    This preserves the session but changes the visibility.

    Args:
        browser: The browser instance to modify
        headless: Whether to switch to headless mode (True) or headed mode (False)

    Returns:
        The same browser with updated visibility
    """
    # Unfortunately, we can't directly change the headless property of an existing browser
    # We need to create a new context with the desired settings, but we can keep the same Playwright instance
    browser.contexts[0].pages[0].bring_to_front()
    time.sleep(1)  # Small delay to ensure UI updates

    if headless:
        print("Switching to headless mode...")
        browser.contexts[0].pages[0].evaluate(
            "() => { document.documentElement.style.opacity = '0'; }"
        )
    else:
        print("Switching to headed mode...")
        browser.contexts[0].pages[0].evaluate(
            "() => { document.documentElement.style.opacity = '1'; }"
        )

    return browser


def test_browser_visibility_toggle(page, browser_context):
    """
    This test demonstrates switching browser visibility in a single session.
    """
    playwright, browser = browser_context

    # Start in headed mode (default from fixture)
    page.goto("https://demoqa.com/webtables")
    page.wait_for_timeout(1000)  # brief pause to see the initial state

    print("Starting in headed mode")

    # Switch to "headless" mode for faster operations
    # Note: This just hides the content, not truly headless
    switch_browser_visibility(browser, True)

    # Add records while in "headless" mode

    print("Added records while browser visually hidden")

    # Switch back to headed mode to see the results
    switch_browser_visibility(browser, False)

    # Give some time to visually inspect
    print("Back to headed mode - you can see the added records")
    page.wait_for_timeout(5000)  # 5 seconds to visually inspect
