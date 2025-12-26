from playwright.sync_api import Locator
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


def is_visible(locator: Locator) -> bool:
    try:
        locator.wait_for()
        return True
    except PlaywrightTimeoutError:
        return False
