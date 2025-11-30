import logging
from calendar import monthrange
from datetime import datetime, timedelta
from time import sleep
from typing import Final

from app.banks_clients.tbank import TBankClient
from app.settings import settings
from app.telegram_client import TelegramClient


class Scrooge:
    CHECK_TIME_DELAY_SECONDS: Final[int] = 60 * 60

    def __init__(self) -> None:
        self._telegram_client = TelegramClient()
        # TODO: Сделать выбор банков
        self._bank_client = TBankClient(self._telegram_client)
        self._yesterday_balance = 0
        self._next_balance_check_time = datetime.combine(datetime.today(), settings.SEND_BALANCE_MESSAGE_AT)

    def run(self) -> None:
        self._bank_client.pass_two_factor_authentication()
        self._bank_client.logout()

        while True:
            if datetime.now() < self._next_balance_check_time:
                sleep(self.CHECK_TIME_DELAY_SECONDS)
                continue

            self._check_balance()
            self._next_balance_check_time += timedelta(days=1)
            logging.info(f"Следующий запуск в {self._next_balance_check_time.isoformat()}")

    def _check_balance(self) -> None:
        self._bank_client.login()
        balance = self._bank_client.get_balance()
        self._bank_client.logout()

        message = self._make_balance_message(balance)
        self._yesterday_balance = balance

        self._telegram_client.send_message(message)

    def _make_balance_message(self, balance: int) -> str:
        today = datetime.today()
        days_in_current_month = monthrange(month=today.month, year=today.year)[-1]
        days_before_next_month = days_in_current_month - today.day

        allowed_expense_per_day = int(balance / days_before_next_month) if days_before_next_month else balance

        return (
            f"Вчера было потрачено {self._yesterday_balance - balance:_} ₽. "
            f"Осталось {allowed_expense_per_day:_} ₽ в день."
        )
