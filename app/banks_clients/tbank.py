import re
from random import randint
from typing import Final

from app.banks_clients.base import BaseBankClient
from app.settings import logger
from app.telegram_client import TelegramClient


class TBankClient(BaseBankClient):
    LOGIN_URL: Final[str] = "https://www.tbank.ru/auth/login/"

    ENTER_LOGIN_MESSAGE: Final[str] = "Введите номер телефона в формате 79223334455"
    LOGIN_REGEX: Final[str] = r"^\d{11}$"

    ENTER_ONE_TIME_CODE_MESSAGE: Final[str] = "Введите код из СМС"
    ONE_TIME_CODE_REGEX: Final[str] = r"^\d{4}$"

    def __init__(self, telegram_client: TelegramClient) -> None:
        super().__init__(telegram_client)
        self._fast_login_code = tuple(str(randint(0, 9)) for _ in range(4))

    def pass_two_factor_authentication(self) -> None:
        logger.info("Первый вход")
        self._page.goto(self.LOGIN_URL)

        logger.info("Ожидаем ввод номера телефона в телеграмм")
        self._telegram_client.send_message(self.ENTER_LOGIN_MESSAGE)
        login = self._telegram_client.get_new_message(self.LOGIN_REGEX)
        self._page.locator('[automation-id="phone-input"]').fill(login)
        self._page.locator('[automation-id="button-submit"]').click()

        logger.info("Ожидаем ввод кода в телеграмм")
        self._telegram_client.send_message(self.ENTER_ONE_TIME_CODE_MESSAGE)
        code = self._telegram_client.get_new_message(self.ONE_TIME_CODE_REGEX)
        self._page.locator('[automation-id="otp-input"]').fill(code)

        logger.info("Заполняем код для повторного входа")
        for number, code_digit in enumerate(self._fast_login_code):
            self._page.locator(f'[automation-id="pin-code-input-{number}"]').fill(code_digit)

        self._page.locator('[automation-id="button-submit"]').click()

    def logout(self) -> None:
        logger.info("Выходим из аккаунта")
        self._page.locator('[data-qa-type="navigation/username"]').click()
        self._page.locator('[data-qa-type="navigation/popover.logout"]').click()

    def login(self) -> None:
        logger.info("Входим по многоразовому коду")
        self._page.goto(self.LOGIN_URL)
        for number, code_digit in enumerate(self._fast_login_code):
            self._page.locator(f'[automation-id="pin-code-input-{number}"]').fill(code_digit)

    def get_balance(self) -> int:
        raw_balance = self._page.locator('xpath=//a[contains(@href, "/mybank/accounts/debit/")]').inner_text()
        raw_balance = raw_balance.split(",")[0]
        balance = re.sub(r"[^0-9]", "", raw_balance)
        logger.info(f"Текущий баланс {balance}")
        return int(balance)
