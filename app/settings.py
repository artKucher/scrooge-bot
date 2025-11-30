import logging
from datetime import time

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore", env_file=".environment", env_file_encoding="utf-8")

    HEADLESS: bool = True
    SLOW_MO: int = 500
    LOGGING_LEVEL: str = "INFO"
    DELAY_SECONDS: int = 10

    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: int

    SEND_BALANCE_MESSAGE_AT: time


settings = Settings()


logging.basicConfig(
    level=logging.getLevelName(settings.LOGGING_LEVEL),
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
