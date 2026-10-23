import logging
from typing import List, Tuple
from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import REQUIRED_CHANNELS

logger = logging.getLogger(__name__)


async def check_user_subscriptions(bot: Bot, user_id: int) -> Tuple[bool, List[str]]:
    """
    Foydalanuvchi majburiy kanallarga a'zo bo'lganligini tekshiradi.
    Qaytaradi: (barchasiga a'zomi: bool, a'zo bo'linmagan kanallar ro'yxati: list)
    """
    if not REQUIRED_CHANNELS:
        return True, []

    unsubscribed: List[str] = []

    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in [
                ChatMemberStatus.LEFT,
                ChatMemberStatus.KICKED,
            ]:
                unsubscribed.append(channel)
        except Exception as e:
            logger.warning(
                f"Kanalni tekshirishda xatolik ({channel}): {e}. "
                "Bot ushbu kanalda administrator ekanligiga ishonch hosil qiling!"
            )
            # Agar bot kanalda admin bo'lmasa yoki kanal topilmasa,
            # foydalanuvchini bloklab qo'ymaslik uchun kanalni ro'yxatga kiritmaymiz
            continue

    is_subscribed = len(unsubscribed) == 0
    return is_subscribed, unsubscribed


async def get_subscription_keyboard(bot: Bot, unsubscribed_channels: List[str]) -> InlineKeyboardMarkup:
    """
    A'zo bo'linmagan kanallar uchun inline tugmalar (havolalar) va tekshirish tugmasini yaratadi.
    """
    keyboard_buttons = []

    for channel in unsubscribed_channels:
        # Kanal havolasini aniqlash
        if channel.startswith("@"):
            channel_url = f"https://t.me/{channel[1:]}"
            button_text = f"📢 Kanalga a'zo bo'lish ({channel})"
        else:
            try:
                chat = await bot.get_chat(channel)
                channel_url = chat.invite_link or f"https://t.me/{chat.username}"
                button_text = f"📢 {chat.title or 'Kanalga'} a'zo bo'lish"
            except Exception:
                channel_url = f"https://t.me/{channel.replace('@', '')}"
                button_text = "📢 Kanalga a'zo bo'lish"

        keyboard_buttons.append([InlineKeyboardButton(text=button_text, url=channel_url)])

    # Tekshirish tugmasi
    keyboard_buttons.append([
        InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_subscription")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
