# 📥 Instagram Video Yuklovchi Telegram Bot (Python)

Ushbu bot foydalanuvchilar tomonidan yuborilgan Instagram havolalarini (Reels, Post, IGTV, Video) avtomatik aniqlab, ularni video formatida Telegram'ga yuklab beradi.

---

## 🚀 Asosiy Imkoniyatlar

- **Reels va Postlarni yuklab olish:** Instagram havolasini yuborish kifoya, bot videoni avtomatik tarzda yuklab foydalanuvchiga taqdim etadi.
- **🤖 Sun'iy Intellekt (AI Chat):** Bot ichida to'laqonli AI Chat bo'limi mavjud. Foydalanuvchilar istalgan mavzudagi savollariga (dasturlash, tarjimalar, insholar, maslahatlar) o'zbek tilida aqlli javob olishlari mumkin.
- **📢 Majburiy obuna:** Kanalga obuna bo'lmagan foydalanuvchilar botdan foydalana olmaydi.
- **Asinxron va o'ta tezkor:** `Direct CDN streaming` va `aiogram 3.x` orqali videolar sanoqli soniyalarda yuboriladi.
- **Toza xotira:** Yuklab olingan vaqtinchalik video fayllar foydalanuvchiga yuborilgach, diskdan avtomatik ravishda o'chiriladi.
- **Xavfsiz konfiguratsiya:** Bot tokeni va kanal sozlamalari `.env` faylida xavfsiz saqlanadi.

---

## 📁 Loyiha Tuzilishi

```text
insatgram bek/
│
├── bot.py             # Botni ishga tushiruvchi asosiy fayl (Entrypoint)
├── config.py          # Sozlamalar va muhit o'zgaruvchilari (.env)
├── downloader.py      # Instagram'dan videoni yuklab oluvchi yordamchi modul (yt-dlp)
├── handlers.py        # /start, /help va Instagram havolalarini qabul qiluvchi handlerlar
├── requirements.txt   # Kerakli Python kutubxonalari
├── .env.example       # Konfiguratsiya namunasi
├── .env               # Haqiqiy bot tokeningiz yoziladigan fayl
└── README.md          # Foydalanish bo'yicha to'liq qo'llanma
```

---

## 🛠 O'rnatish va Ishga Tushirish

### 1-qadam: Bot Tokenini olish
1. Telegram'da [@BotFather](https://t.me/botfather) botiga kiring.
2. `/newbot` buyrug'ini yuboring.
3. Botingizga nom va `@` bilan tugaydigan username tanlang (masalan, `MyInstaDownloaderBot`).
4. Sizga berilgan **API Token**ni nusxalab oling (masalan: `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`).

### 2-qadam: `.env` Fayliga Toknni Kiritish
Loyiha papkasidagi `.env` faylini oching va tokenni yozing:

```env
BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
```

### 3-qadam: Virtual Muhitni Faollashtirish va Kutubxonalarni O'rnatish

**Windows PowerShell:**
```powershell
# Virtual muhitni faollashtirish
.\venv\Scripts\Activate.ps1

# Kutubxonalarni o'rnatish
pip install -r requirements.txt
```

### 4-qadam: Botni Ishga Tushirish

```powershell
python bot.py
```
Yoki to'g'ridan-to'g'ri virtual muhit orqali:
```powershell
.\venv\Scripts\python.exe bot.py
```

Konsolda quyidagi xabarni ko'rsangiz, bot muvaffaqiyatli ishlayapti:
```text
Bot muvaffaqiyatli ishga tushdi va xabarlarni qabul qilishga tayyor!
```

---

## 💡 Foydalanish Qo'llanmasi

1. Telegram'da yaratgan botingizni oching va `/start` tugmasini bosing.
2. Instagram ilovasidan istalgan **Reels** yoki **Video** havolasini oling:
   - Misol: `https://www.instagram.com/reel/C8.../`
3. Havolani botga yuboring.
4. Bot bir necha soniya ichida videoni sizga yuboradi!

---

## 🔒 Muhim Eslatmalar

- **50 MB limiti:** Telegram botlari oddiy rejimda maksimal 50 MB gacha hajmdagi fayllarni yubora oladi. Agar video 50 MB dan katta bo'lsa, bot bu haqda xabar beradi.
- **Yopiq profillar (Private accounts):** Instagram yopiq profillarning videolarini ruxsatsiz yuklashga ruxsat bermaydi.
- **Cookies (Ixtiyoriy):** Agar Instagram bot so'rovlarini cheklasa, brauzeringizdan eksport qilingan `cookies.txt` faylini loyiha papkasiga joylashtirishingiz mumkin. Bot uni avtomatik aniqlab, so'rovlarni uzluksiz amalga oshiradi.
