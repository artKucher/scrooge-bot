import re
from datetime import datetime
from time import sleep

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.decryptor import RSADecryptor
from app.settings import logger, settings


class TelegramClient:
    BASE_TELEGRAM_URL: str = "https://api.telegram.org"
    READINGS_DELAY_SECONDS: int = 10
    RETRY: Retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "POST"}),
        raise_on_status=False,
    )

    def __init__(self) -> None:
        self._bot_token = settings.TELEGRAM_BOT_TOKEN
        self._chat_id = settings.TELEGRAM_CHAT_ID
        self._session = requests.Session()
        self._session.mount("https://", HTTPAdapter(max_retries=self.RETRY))

    def send_message(self, message: str) -> None:
        response = self._session.post(
            url=f"{self.BASE_TELEGRAM_URL}/bot{self._bot_token}/sendMessage",
            json={"chat_id": self._chat_id, "text": message},
        )
        response.raise_for_status()

    def get_new_message(self, message_pattern: str) -> str:
        decryptor = RSADecryptor()
        now_timestamp = datetime.now().timestamp()

        self.send_message(decryptor.ENCRYPTION_GUIDE)
        self.send_message(decryptor.public_key)

        while True:
            response = self._session.get(
                url=f"{self.BASE_TELEGRAM_URL}/bot{self._bot_token}/getUpdates",
            )
            response.raise_for_status()

            for message in response.json()["result"]:
                if "message" not in message:
                    continue
                if message["message"]["chat"]["id"] != self._chat_id:
                    continue
                if message["message"]["date"] < now_timestamp:
                    continue
                message_text = message["message"].get("text", "")
                message_text = decryptor.decrypt(message_text)
                if re.match(message_pattern, message_text):
                    return message_text

            logger.warning(f"Сообщение, подходящее под паттерн {message_pattern} не получено")
            sleep(self.READINGS_DELAY_SECONDS)
