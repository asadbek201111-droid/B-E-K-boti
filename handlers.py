import logging
from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    FSInputFile,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)
from aiogram.filters import CommandStart, Command
from aiogram.enums import ChatAction
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from downloader import (
    extract_instagram_url,
    extract_direct_url,
    download_instagram_video,
    remove_file_safely
)
from subscription import (
    check_user_subscriptions,
    get_subscription_keyboard
)
from ai_service import (
    ask_ai,
    clear_user_history
)

logger = logging.getLogger(__name__)
router = Router()


class BotState(StatesGroup):
    ai_chat = State()


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy menyu tugmalari"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🤖 Sun'iy Intellekt (AI Chat)"),
                KeyboardButton(text="📥 Instagram Video Yuklash")
            ],
            [
                KeyboardButton(text="ℹ️ Bot Haqida / Yordam")
            ]
        ],
        resize_keyboard=True
    )


def get_ai_chat_keyboard() -> ReplyKeyboardMarkup:
    """AI Chat rejimida ko'rinadigan tugmalar"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🔙 Chiqish (Asosiy Menyu)"),
                KeyboardButton(text="🗑 Suhbatni tozalash")
            ]
        ],
        resize_keyboard=True
    )


async def send_long_message(message: Message, text: str):
    """4000 belgidan uzun javoblarni bo'lib yuborish"""
    max_len = 4000
    for i in range(0, len(text), max_len):
        chunk = text[i:i + max_len]
        try:
            await message.answer(chunk, parse_mode="Markdown")
        except Exception:
            # Agar markdown formati xato bo'lsa, oddiy matn sifatida yuboramiz
            await message.answer(chunk)


@router.message(CommandStart())
@router.message(Command("menu"))
async def handle_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id if message.from_user else 0

    # Obunani tekshirish
    is_subscribed, unsubscribed = await check_user_subscriptions(message.bot, user_id)
    if not is_subscribed:
        keyboard = await get_subscription_keyboard(message.bot, unsubscribed)
        await message.answer(
            "⚠️ <b>Botdan foydalanish uchun quyidagi kanalimizga obuna bo'lishingiz shart!</b>\n\n"
            "Kanalga a'zo bo'ling va so'ng <b>«✅ Obunani tekshirish»</b> tugmasini bosing:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return

    user_name = message.from_user.full_name if message.from_user else "Foydalanuvchi"
    text = (
        f"Assalomu alaykum, <b>{user_name}</b>! 👋\n\n"
        "Botingiz xizmatingizga tayyor. Quyidagi bo'limlardan birini tanlang:\n\n"
        "📥 <b>Instagram Video Yuklash:</b> Reels yoki video havolasini yuboring.\n"
        "🤖 <b>Sun'iy Intellekt (AI Chat):</b> Istalgan mavzudagi savollaringizga aqlli javob oling!\n\n"
        "Kerakli bo'limni pastdagi tugmalar orqali tanlashingiz mumkin 👇"
    )
    await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="HTML")


@router.message(F.text == "🤖 Sun'iy Intellekt (AI Chat)")
@router.message(Command("ai"))
async def handle_enter_ai_chat(message: Message, state: FSMContext):
    user_id = message.from_user.id if message.from_user else 0
    is_subscribed, unsubscribed = await check_user_subscriptions(message.bot, user_id)
    if not is_subscribed:
        keyboard = await get_subscription_keyboard(message.bot, unsubscribed)
        await message.answer(
            "⚠️ <b>Botdan foydalanish uchun avval kanalimizga obuna bo'ling:</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return

    await state.set_state(BotState.ai_chat)
    text = (
        "🤖 <b>Sun'iy Intellekt (AI Chat) bo'limiga xush kelibsiz!</b>\n\n"
        "Menga istalgan savolingizni yozib yuborishingiz mumkin:\n"
        "• Dasturlash va texnologiyalar 💻\n"
        "• Chet tillari va tarjimalar 🌍\n"
        "• Maslahatlar, insholar, hisob-kitoblar 📝\n"
        "• Istalgan qiziqtirgan mavzuingiz bo'yicha 💡\n\n"
        "Savolingizni yozing, men javob berishga tayyorman!\n\n"
        "<i>🔙 Chiqish uchun pastdagi «Chiqish» tugmasini bosing.</i>"
    )
    await message.answer(text, reply_markup=get_ai_chat_keyboard(), parse_mode="HTML")


@router.message(BotState.ai_chat, F.text == "🔙 Chiqish (Asosiy Menyu)")
async def handle_exit_ai_chat(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🏠 <b>Asosiy menyuga qaytdingiz.</b>\n"
        "Instagram havolalarini yuborishingiz yoki boshqa bo'limlarni tanlashingiz mumkin:",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@router.message(BotState.ai_chat, F.text == "🗑 Suhbatni tozalash")
async def handle_clear_ai_history(message: Message):
    user_id = message.from_user.id if message.from_user else 0
    clear_user_history(user_id)
    await message.answer(
        "🧹 <b>Suhbat xotirasi tozalandi!</b>\nEndi yangi mavzuda savol berishingiz mumkin.",
        parse_mode="HTML"
    )


@router.message(F.text == "📥 Instagram Video Yuklash")
async def handle_info_instagram(message: Message):
    text = (
        "📥 <b>Instagram Video Yuklash</b>\n\n"
        "Menga Instagram'dan istalgan <b>Reels</b>, <b>Post</b> yoki <b>Video</b> havolasini yuboring, "
        "men uni sizga tezkor ravishda video formatida yuklab beraman!\n\n"
        "Misol: <code>https://www.instagram.com/reel/C8.../</code>"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "ℹ️ Bot Haqida / Yordam")
@router.message(Command("help"))
async def handle_help(message: Message):
    user_id = message.from_user.id if message.from_user else 0
    is_subscribed, unsubscribed = await check_user_subscriptions(message.bot, user_id)
    if not is_subscribed:
        keyboard = await get_subscription_keyboard(message.bot, unsubscribed)
        await message.answer(
            "⚠️ <b>Botdan foydalanish uchun avval kanalimizga obuna bo'ling:</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return

    text = (
        "📖 <b>Bot imkoniyatlari:</b>\n\n"
        "1. 📥 <b>Instagram Video Yuklash:</b>\n"
        "   Instagram ilovasidagi Reels yoki video havolasini nusxalab botga yuboring.\n"
        "   Bot bir necha soniyada videoni video formatida sizga yuboradi.\n\n"
        "2. 🤖 <b>Sun'iy Intellekt (AI Chat):</b>\n"
        "   Menyudan «AI Chat» bo'limini tanlab, istalgan savollaringizga aqlli javob olishingiz mumkin.\n\n"
        "⚠️ <i>Eslatma: Yopiq (private) profillardagi videolarni yuklab bo'lmaydi.</i>"
    )
    await message.answer(text, parse_mode="HTML")


@router.callback_query(F.data == "check_subscription")
async def handle_subscription_check(callback: CallbackQuery, state: FSMContext):
    """Foydalanuvchi 'Obunani tekshirish' tugmasini bosganda ishlaydi."""
    user_id = callback.from_user.id
    is_subscribed, unsubscribed = await check_user_subscriptions(callback.bot, user_id)

    if is_subscribed:
        try:
            await callback.message.delete()
        except Exception:
            pass

        await callback.message.answer(
            "✅ <b>Obunangiz tasdiqlandi!</b>\n\n"
            "Endi botdan to'liq foydalanishingiz mumkin. Quyidagi bo'limlardan birini tanlang:",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer("✅ Rahmat! Obuna tasdiqlandi.", show_alert=False)
    else:
        keyboard = await get_subscription_keyboard(callback.bot, unsubscribed)
        try:
            await callback.message.edit_reply_markup(reply_markup=keyboard)
        except Exception:
            pass
        await callback.answer(
            "❌ Siz hali kanalga a'zo bo'lmadingiz! Iltimos, avval kanalga obuna bo'ling.",
            show_alert=True
        )


@router.message(F.text)
async def handle_text_messages(message: Message, state: FSMContext):
    user_id = message.from_user.id if message.from_user else 0
    text = message.text.strip()

    # 1. Majburiy obuna tekshiruvi
    is_subscribed, unsubscribed = await check_user_subscriptions(message.bot, user_id)
    if not is_subscribed:
        keyboard = await get_subscription_keyboard(message.bot, unsubscribed)
        await message.answer(
            "⚠️ <b>Botdan foydalanish uchun quyidagi kanalimizga obuna bo'lishingiz shart!</b>\n\n"
            "Kanalga a'zo bo'ling va so'ng <b>«✅ Obunani tekshirish»</b> tugmasini bosing:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return

    # 2. Xabar ichida Instagram havolasi bormi?
    instagram_url = extract_instagram_url(text)

    # Agar Instagram havolasi bo'lsa -> Har qanday rejimda ham videoni yuklab berish
    if instagram_url:
        await process_instagram_download(message, instagram_url)
        return

    # 3. Agar foydalanuvchi AI Chat rejimida bo'lsa -> Sun'iy intellekt javob beradi
    current_state = await state.get_state()
    if current_state == BotState.ai_chat:
        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
        ai_response = await ask_ai(text, user_id=user_id)
        await send_long_message(message, ai_response)
        return

    # 4. Agar foydalanuvchi oddiy menyuda tasodifiy matn yozsa:
    await message.reply(
        "❓ <b>Tushunarsiz xabar.</b>\n\n"
        "• Instagram video yuklash uchun to'g'ri <b>Instagram havolasini</b> yuboring.\n"
        "• Savollaringizga javob olish uchun esa quyidagi <b>«🤖 Sun'iy Intellekt (AI Chat)»</b> tugmasini bosing!",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


async def process_instagram_download(message: Message, instagram_url: str):
    """Instagram videosini yuklab yuborish mexanizmi"""
    status_msg = await message.reply("⚡ <b>Video tayyorlanmoqda...</b>", parse_mode="HTML")
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_VIDEO)

    bot_info = await message.bot.get_me()
    bot_username = f"@{bot_info.username}" if bot_info.username else ""

    # 1-BOSQICH (ENG TEZKOR): To'g'ridan-to'g'ri Instagram CDN video havolasi orqali yuborish
    try:
        fast_res = await extract_direct_url(instagram_url)
        if fast_res.get("success") and fast_res.get("direct_url"):
            caption = fast_res.get("caption") or "Instagram orqali yuklab olindi 🎬"
            if bot_username:
                caption = f"{caption}\n\n🤖 <i>{bot_username} orqali yuklab olindi</i>"

            await message.answer_video(
                video=fast_res["direct_url"],
                caption=caption,
                duration=fast_res.get("duration"),
                width=fast_res.get("width"),
                height=fast_res.get("height"),
                parse_mode="HTML",
                request_timeout=35
            )
            try:
                await status_msg.delete()
            except Exception:
                pass
            return
    except Exception as fast_err:
        logger.info(f"Direct URL orqali yuborilmadi ({fast_err}), faylni yuklab olish rejimiga o'tiladi...")

    # 2-BOSQICH: Agar to'g'ridan-to'g'ri havola ishlamasa, faylni diskka yuklab yuborish
    file_path = None
    try:
        result = await download_instagram_video(instagram_url)

        if not result.get("success"):
            error_text = result.get("error", "Videoni yuklab bo'lmadi.")
            await status_msg.edit_text(f"❌ <b>Xatolik:</b>\n{error_text}", parse_mode="HTML")
            return

        file_path = result.get("file_path")
        caption = result.get("caption") or "Instagram orqali yuklab olindi 🎬"
        if bot_username:
            caption = f"{caption}\n\n🤖 <i>{bot_username} orqali yuklab olindi</i>"

        # Telegramga video sifatida yuborish
        video_input = FSInputFile(file_path)
        try:
            await message.answer_video(
                video=video_input,
                caption=caption,
                duration=result.get("duration"),
                width=result.get("width"),
                height=result.get("height"),
                parse_mode="HTML",
                request_timeout=300
            )
        except Exception as send_err:
            logger.warning(f"answer_video da muammo ({send_err}), fayl sifatida yuborishga urinilmoqda...")
            await message.answer_document(
                document=video_input,
                caption=caption,
                parse_mode="HTML",
                request_timeout=300
            )

        # Status xabarini o'chirish
        try:
            await status_msg.delete()
        except Exception:
            pass

    except Exception as e:
        logger.exception("Video yuborishda xatolik yuz berdi:")
        await status_msg.edit_text(
            f"❌ Videoni yuborishda xatolik yuz berdi: {str(e)}",
            parse_mode="HTML"
        )
    finally:
        # Disk xotirasini tejash uchun vaqtinchalik faylni o'chiramiz
        if file_path:
            remove_file_safely(file_path)
