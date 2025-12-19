from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import date
from functools import wraps
from typing import Any, Final

from playwright.sync_api import sync_playwright

from app.settings import settings
from app.telegram_client import TelegramClient


class BaseBankClient(ABC):
    LOGIN_URL: str
    USER_AGENT: Final[str] = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
    )
    STARTUP_HEADERS: Final[dict[str, str]] = {
        "Sec-CH-UA": '"Google Chrome";v="125", "Chromium";v="125", "Not-A.Brand";v="24"'
    }

    def __init__(self, telegram_client: TelegramClient) -> None:
        playwright_instance = sync_playwright().start()
        browser = playwright_instance.chromium.launch(headless=settings.HEADLESS, slow_mo=settings.SLOW_MO)
        context = browser.new_context(user_agent=self.USER_AGENT, extra_http_headers=self.STARTUP_HEADERS)
        if settings.RECORD_TRACING:
            context.tracing.start(snapshots=True, screenshots=True)
        self._page = context.new_page()
        self._telegram_client = telegram_client

    @abstractmethod
    def pass_two_factor_authentication(self) -> None: ...

    @abstractmethod
    def login(self) -> None: ...

    @abstractmethod
    def logout(self) -> None: ...

    @abstractmethod
    def get_balance(self) -> int: ...

    @classmethod
    def handle_error(cls, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self: BaseBankClient, *args: Any, **kwargs: Any) -> Any:
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                if settings.RECORD_TRACING:
                    self._page.context.tracing.stop(path=f"tracing_{date.today().isoformat()}.zip")
                self._page.context.browser.close()
                raise e

        return wrapper
