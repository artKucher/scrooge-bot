from playwright.sync_api import Locator


def is_visible(locator: Locator) -> bool:
    try:
        locator.wait_for()
        return True
    except TimeoutError:
        return False
