import asyncio
import os
import re
import uuid
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import yt_dlp
from config import DOWNLOADS_DIR, COOKIES_FILE

try:
    import imageio_ffmpeg
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_PATH = None

logger = logging.getLogger(__name__)

# Instagram havolasini aniqlash uchun muntazam ifoda (Regex)
INSTAGRAM_URL_PATTERN = re.compile(
    r'(https?://(?:www\.)?instagram\.com/(?:p|reel|reels|tv|share/[a-zA-Z0-9_\-]+)/[a-zA-Z0-9_\-]+/?(?:[^\s]*))',
    re.IGNORECASE
)


def extract_instagram_url(text: str) -> Optional[str]:
    """Matn ichidan birinchi Instagram havolasini ajratib oladi."""
    if not text:
        return None
    match = INSTAGRAM_URL_PATTERN.search(text)
    if match:
        url = match.group(1)
        # Tracking parametrlarini tozalash (?igsh=..., &utm_source=...)
        clean_url = url.split('?')[0]
        return clean_url
    return None


def _extract_direct_url_sync(url: str) -> Dict[str, Any]:
    """
    Video faylini diskka yuklamasdan, to'g'ridan-to'g'ri Instagram CDN video havolasini oladi.
    Bu eng tezkor usul (1-3 soniya).
    """
    ydl_opts: Dict[str, Any] = {
        'format': 'best[ext=mp4]/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'check_formats': False,
        'no_check_certificate': True,
        'http_headers': {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/123.0.0.0 Safari/537.36'
            ),
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }
    if COOKIES_FILE.exists() and COOKIES_FILE.stat().st_size > 0:
        ydl_opts['cookiefile'] = str(COOKIES_FILE)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return {"success": False}

            if 'entries' in info:
                entries = [e for e in info['entries'] if e]
                if entries:
                    info = entries[0]

            direct_url = info.get('url')
            if not direct_url:
                return {"success": False}

            caption = info.get('description') or info.get('title') or ""
            if len(caption) > 900:
                caption = caption[:900] + "..."

            return {
                "success": True,
                "direct_url": direct_url,
                "caption": caption,
                "duration": info.get('duration'),
                "width": info.get('width'),
                "height": info.get('height')
            }
    except Exception as e:
        logger.info(f"Direct URL olib bo'lmadi ({e}), yuklab olish rejimiga o'tiladi.")
        return {"success": False}


async def extract_direct_url(url: str) -> Dict[str, Any]:
    """Asinxron o'rovchi: to'g'ridan-to'g'ri CDN video havolasini oladi."""
    return await asyncio.to_thread(_extract_direct_url_sync, url)


def _download_sync(url: str) -> Dict[str, Any]:
    """
    Sinxron ravishda yt-dlp orqali Instagram videosini yuklab oladi.
    Bu funksiya asyncio.to_thread orqali alohida oqimda ishga tushiriladi.
    """
    unique_prefix = uuid.uuid4().hex[:8]
    output_template = str(DOWNLOADS_DIR / f"{unique_prefix}_%(id)s.%(ext)s")

    ydl_opts: Dict[str, Any] = {
        'outtmpl': output_template,
        'format': 'best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'check_formats': False,
        'no_check_certificate': True,
        'concurrent_fragment_downloads': 10,
        'buffersize': 1024 * 1024,
        'max_filesize': 50 * 1024 * 1024,  # Telegram bot limiti (50 MB)
        'http_headers': {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/123.0.0.0 Safari/537.36'
            ),
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }

    # FFmpeg mavjud bo'lsa, yt-dlp unga murojaat qiladi
    if FFMPEG_PATH and os.path.exists(FFMPEG_PATH):
        ydl_opts['ffmpeg_location'] = FFMPEG_PATH
        ydl_opts['merge_output_format'] = 'mp4'

    # Agar cookies.txt mavjud bo'lsa, undan foydalanamiz
    if COOKIES_FILE.exists() and COOKIES_FILE.stat().st_size > 0:
        ydl_opts['cookiefile'] = str(COOKIES_FILE)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                return {
                    "success": False,
                    "error": "Instagramdan ma'lumot olib bo'lmadi. Havola to'g'riligini tekshiring."
                }

            # Agar bu karusel (bir nechta media) yoki faqat rasm bo'lsa
            if 'entries' in info:
                # Birinchi videoni olishga harakat qilamiz
                entries = [e for e in info['entries'] if e]
                if entries:
                    info = entries[0]

            # Yuklab olingan fayl yo'lini aniqlash
            downloaded_file = None
            if 'requested_downloads' in info and info['requested_downloads']:
                downloaded_file = info['requested_downloads'][0].get('filepath')

            if not downloaded_file or not os.path.exists(downloaded_file):
                downloaded_file = ydl.prepare_filename(info)

            # Agar fayl kengaytmasi o'zgargan bo'lsa (masalan .webm dan .mp4 ga)
            if not os.path.exists(downloaded_file):
                # Papkadan unique_prefix bilan boshlanadigan faylni qidiramiz
                matched_files = list(DOWNLOADS_DIR.glob(f"{unique_prefix}_*"))
                if matched_files:
                    downloaded_file = str(matched_files[0])
                else:
                    return {
                        "success": False,
                        "error": "Video fayli topilmadi yoki bu postda video mavjud emas (faqat rasm bo'lishi mumkin)."
                    }

            # Fayl hajmini tekshirish
            file_size = os.path.getsize(downloaded_file)
            if file_size > 50 * 1024 * 1024:
                try:
                    os.remove(downloaded_file)
                except OSError:
                    pass
                return {
                    "success": False,
                    "error": "Video hajmi 50 MB dan katta. Telegram bot faqat 50 MB gacha fayllarni yubora oladi."
                }

            caption = info.get('description') or info.get('title') or ""
            # Telegram caption limiti 1024 belgi
            if len(caption) > 900:
                caption = caption[:900] + "..."

            return {
                "success": True,
                "file_path": downloaded_file,
                "title": info.get('title', ''),
                "caption": caption,
                "duration": info.get('duration'),
                "width": info.get('width'),
                "height": info.get('height')
            }

    except yt_dlp.utils.DownloadError as e:
        err_msg = str(e)
        logger.error(f"yt-dlp xatosi: {err_msg}")
        if "login" in err_msg.lower() or "private" in err_msg.lower():
            return {
                "success": False,
                "error": "Bu Instagram hisobi yopiq (private) yoki Instagram kirishni talab qilmoqda."
            }
        return {
            "success": False,
            "error": "Videoni yuklab olishda xatolik yuz berdi. Havola to'g'ri ekanligini yoki post o'chirilmaganligini tekshiring."
        }
    except Exception as e:
        logger.exception("Kutilmagan xatolik yuz berdi:")
        return {
            "success": False,
            "error": f"Xatolik yuz berdi: {str(e)}"
        }


async def download_instagram_video(url: str) -> Dict[str, Any]:
    """Asinxron o'rovchi: yt-dlp yuklash jarayonini botni qotirmasdan bajaradi."""
    return await asyncio.to_thread(_download_sync, url)


def remove_file_safely(file_path: Optional[str]) -> None:
    """Yuborilgandan so'ng diskni to'ldirmaslik uchun vaqtinchalik faylni o'chiradi."""
    if not file_path or not os.path.exists(file_path):
        return

    import time
    for attempt in range(6):
        try:
            os.remove(file_path)
            logger.info(f"Vaqtinchalik fayl o'chirildi: {file_path}")
            return
        except OSError as e:
            if attempt < 5:
                time.sleep(1)
            else:
                logger.warning(f"Faylni o'chirishda xatolik: {e}")
