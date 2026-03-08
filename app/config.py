from pathlib import Path

from pydantic_settings import BaseSettings

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_ids: str = ""  # 콤마 구분 chat_id
    telegram_webhook_secret: str = ""

    # Gemini
    gemini_api_key: str = ""

    # Cloud Run
    webhook_base_url: str = ""  # 예: https://morning-sesangmansa-xxx.run.app

    # Cloud Scheduler 인증
    scheduler_auth_token: str = ""

    model_config = {
        "env_file": str(ENV_FILE),
        "extra": "ignore",
    }

    @property
    def parsed_chat_ids(self) -> list[int]:
        result = []
        for item in self.telegram_chat_ids.split(","):
            item = item.strip()
            if item:
                try:
                    result.append(int(item))
                except ValueError:
                    continue
        return result


settings = Settings()
