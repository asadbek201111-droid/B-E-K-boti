import logging
from typing import Dict, List, Optional
import aiohttp
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

# Har bir foydalanuvchi uchun suhbat tarixini xotirada saqlash (oxirgi 8 ta xabar)
USER_HISTORIES: Dict[int, List[Dict[str, str]]] = {}

# Ishonchli va tezkor Gemini modellar ro'yxati (navbat bilan sinab ko'riladi)
GEMINI_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash"
]

SYSTEM_PROMPT = (
    "Siz Telegram bot ichidagi juda aqlli, xushmuomala, bilimdon sun'iy intellektsiz. "
    "Foydalanuvchining istalgan mavzudagi savollariga (fan, texnologiya, dasturlash, tillar, "
    "hayotiy maslahatlar, ijodiy yozishmalar, hisob-kitoblar va h.k.) aniq, tushunarli va batafsil javob bering. "
    "Foydalanuvchi qaysi tilda yozsa, o'sha tilda (asosan o'zbek tilida) javob bering. "
    "Javoblaringiz chiroyli formatda (Telegram Markdown/HTML) bo'lsin."
)


async def ask_gemini(prompt: str, user_id: int) -> Optional[str]:
    """Google Gemini modellari orqali navbatma-navbat javob olishga urinadi."""
    if not GEMINI_API_KEY:
        return None

    if user_id not in USER_HISTORIES:
        USER_HISTORIES[user_id] = []

    history = USER_HISTORIES[user_id]
    history.append({"role": "user", "content": prompt})

    if len(history) > 8:
        history = history[-8:]
        USER_HISTORIES[user_id] = history

    # Gemini formatiga o'tkazish
    gemini_contents = []
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        gemini_contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })

    payload = {
        "system_instruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "contents": gemini_contents
    }

    async with aiohttp.ClientSession() as session:
        for model in GEMINI_MODELS:
            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
                f"?key={GEMINI_API_KEY}"
            )
            try:
                async with session.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                answer = parts[0].get("text", "").strip()
                                history.append({"role": "model", "content": answer})
                                return answer
                    else:
                        logger.warning(f"Model {model} xatosi: status {response.status}")
            except Exception as e:
                logger.warning(f"Model {model} bilan ulanishda xatolik: {e}")
                continue

    return None


async def ask_pollinations(prompt: str, user_id: int) -> str:
    """Zaxira (Fallback) AI tizimi."""
    if user_id not in USER_HISTORIES:
        USER_HISTORIES[user_id] = []

    history = USER_HISTORIES[user_id]
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
        {"role": "user" if m["role"] == "user" else "assistant", "content": m["content"]}
        for m in history
    ]

    payload = {
        "messages": messages,
        "model": "openai",
        "temperature": 0.7
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://text.pollinations.ai/",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                if response.status == 200:
                    answer = await response.text()
                    answer = answer.strip()
                    history.append({"role": "model", "content": answer})
                    return answer
    except Exception as e:
        logger.exception("Fallback AI xatosi:")

    return "Kechirasiz, sun'iy intellekt serverida vaqtinchalik xatolik yuz berdi. Iltimos, yana bir bor savolingizni yuboring."


async def ask_ai(prompt: str, user_id: int = 0) -> str:
    """Asosiy funksiya: Navbatma-navbat Gemini modellarini sinab, eng tez javobni oladi."""
    gemini_answer = await ask_gemini(prompt, user_id)
    if gemini_answer:
        return gemini_answer

    return await ask_pollinations(prompt, user_id)


def clear_user_history(user_id: int) -> None:
    """Foydalanuvchi suhbat tarixini tozalaydi."""
    if user_id in USER_HISTORIES:
        USER_HISTORIES[user_id] = []
