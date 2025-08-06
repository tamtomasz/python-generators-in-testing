# conftest.py
import pytest
from playwright.sync_api import sync_playwright, Page, Browser
from typing import Tuple


@pytest.fixture
def browser_context() -> Tuple[sync_playwright, Browser]:
    """
    Returns the playwright instance and browser that can be used to
    create contexts and pages or switch between headless/headed modes.
    """
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)  # default is headed
    try:
        yield (playwright, browser)
    finally:
        browser.close()
        playwright.stop()


@pytest.fixture
def page(browser_context):
    """
    The standard page fixture that returns a ready-to-use page.
    """
    playwright, browser = browser_context
    context = browser.new_context()
    page = context.new_page()
    try:
        yield page
    finally:
        context.close()
