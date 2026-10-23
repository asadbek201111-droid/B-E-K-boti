import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp import ClientTimeout
from config import BOT_TOKEN
from handlers import router

# Loglarni sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("InstagramBot")


async def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        logger.error(
            "XATOLIK: Bot tokeni topilmadi!\n"
            "Iltimos, .env faylini oching va BOT_TOKEN o'rniga @BotFather'dan olgan tokeningizni kiriting."
        )
        sys.exit(1)

    logger.info("Bot ishga tushirilmoqda...")

    session = AiohttpSession(timeout=300.0)
    bot = Bot(token=BOT_TOKEN, session=session)
    dp = Dispatcher()

    # Handler routerini ulash
    dp.include_router(router)

    # Eski kutilayotgan xabarlarni tozalash va pollingni boshlash
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot muvaffaqiyatli ishga tushdi va xabarlarni qabul qilishga tayyor!")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot to'xtatildi.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Dastur foydalanuvchi tomonidan to'xtatildi.")
