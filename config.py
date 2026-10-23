import os
from pathlib import Path
from dotenv import load_dotenv

# .env faylini yuklash
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Yuklab olingan vaqtinchalik videolar papkasi
DOWNLOADS_DIR = BASE_DIR / "downloads"
DOWNLOADS_DIR.mkdir(exist_ok=True)

# Cookie fayli mavjud bo'lsa (ixtiyoriy, instagram bloklashlarining oldini olish uchun)
COOKIES_FILE = BASE_DIR / "cookies.txt"

# Majburiy obuna kanallari (vergul bilan ajratilgan, masalan: "@mening_kanalim")
raw_channels = os.getenv("REQUIRED_CHANNELS", "")
REQUIRED_CHANNELS = [ch.strip() for ch in raw_channels.split(",") if ch.strip()]

# Google Gemini API kaliti
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
