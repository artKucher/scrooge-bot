import re
from datetime import datetime
from time import sleep

import requests

from app.settings import logger, settings


class TelegramClient:
    READINGS_DELAY_SECONDS: int = 10

    def __init__(self) -> None:
        self._bot_token = settings.TELEGRAM_BOT_TOKEN
        self._chat_id = settings.TELEGRAM_CHAT_ID

    def send_message(self, message: str) -> None:
        response = requests.post(
            url=f"https://api.telegram.org/bot{self._bot_token}/sendMessage",
            json={"chat_id": self._chat_id, "text": message},
        )
        response.raise_for_status()

    def get_new_message(self, message_pattern: str) -> str:
        now_timestamp = datetime.now().timestamp()
        while True:
            response = requests.get(
                url=f"https://api.telegram.org/bot{self._bot_token}/getUpdates",
            )
            response.raise_for_status()

            for message in response.json()["result"]:
                if message["message"]["chat"]["id"] != self._chat_id:
                    continue
                if message["message"]["date"] < now_timestamp:
                    continue
                message_text = message["message"]["text"]
                if re.match(message_pattern, message_text):
                    return message_text

            logger.warning(f"Сообщение, подходящее под паттерн {message_pattern} не получено")
            sleep(self.READINGS_DELAY_SECONDS)
