import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp import ClientTimeout, web
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


async def start_web_server():
    """Render kabi platformalar uchun port ochib turuvchi mini health-check server."""
    port_env = os.getenv("PORT")
    if not port_env:
        return

    try:
        port = int(port_env)
        app = web.Application()

        async def health_check(request):
            return web.Response(text="OK - Bot is running 24/7!")

        app.router.add_get("/", health_check)
        app.router.add_get("/health", health_check)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        logger.info(f"Render uchun health-check web server {port}-portda ishga tushirildi.")
    except Exception as e:
        logger.warning(f"Health-check serverni ishga tushirishda xatolik: {e}")


async def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        logger.error(
            "XATOLIK: Bot tokeni topilmadi!\n"
            "Iltimos, .env faylini oching va BOT_TOKEN o'rniga @BotFather'dan olgan tokeningizni kiriting."
        )
        sys.exit(1)

    logger.info("Bot ishga tushirilmoqda...")

    # Render va bulutli platformalar uchun health-check web server
    await start_web_server()

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
