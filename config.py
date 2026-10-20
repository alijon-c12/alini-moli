import os
from dotenv import load_dotenv

# .env faylini yuklaymiz
load_dotenv()

# Telegram API sozlamalari
TG_API_ID = os.getenv("TG_API_ID")
if TG_API_ID:
    try:
        TG_API_ID = int(str(TG_API_ID).strip())
    except ValueError:
        TG_API_ID = None

TG_API_HASH = os.getenv("TG_API_HASH", "").strip()

# AI sozlamalari
AI_API_KEY = os.getenv("AI_API_KEY", "").strip()
AI_MODEL = os.getenv("AI_MODEL", "gemini-2.5-flash").strip()

# Ruxsat etilgan foydalanuvchilar (ID yoki username larni qabul qiladi)
ALLOWED_USER_IDS = set()
ALLOWED_USERNAMES = set()

allowed_raw = os.getenv("ALLOWED_USERS", "").strip()
if allowed_raw:
    for item in allowed_raw.split(","):
        val = item.strip().lstrip("@").lower()
        if not val:
            continue
        if val.isdigit():
            ALLOWED_USER_IDS.add(int(val))
        else:
            ALLOWED_USERNAMES.add(val)

# Standart System Prompt
SYSTEM_PROMPT = (
    "Sen Muhammadsodiqning yordamchisisan, "
    "o'zbek tilida qisqa va aniq javob ber."
)

# Chat boshqaruvi va limitlar
HISTORY_LIMIT = 10         # Har bir chat uchun saqlanadigan xabarlar soni
MANUAL_REPLY_SILENCE = 600 # Foydalanuvchi o'zi javob yozsa jim turish vaqti (10 daqiqa = 600 soniya)
RATE_LIMIT_DELAY = 3.0     # Bir chatga ketma-ket javoblar orasidagi minimal oraliq (3 soniya)
