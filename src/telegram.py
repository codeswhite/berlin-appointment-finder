from dotenv import load_dotenv
import httpx
import os

load_dotenv()


def parse_telegram_credentials_from_env() -> tuple[str, str]:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    return bot_token, chat_id


class TelegramModule:
    def __init__(self):
        self.bot_token, self.chat_id = parse_telegram_credentials_from_env()

        self.enabled = bool(self.bot_token) and bool(self.chat_id)
        if not self.enabled:
            print(
                "WARNING: Telegram credentials (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID) not set. DISABLING TG messaging."
            )
        else:
            print("Telegram messaging enabled.")

    async def send_telegram_message(self, text: str):
        if not self.enabled:
            print("Telegram messaging is disabled.")
            return

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"}
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, params=payload)
                if resp.status_code != 200:
                    print(f"Telegram error: {resp.status_code} {resp.text}")
            except Exception as e:
                print(f"Error sending Telegram message: {e}")
