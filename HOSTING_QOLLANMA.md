# 🌐 Botni 24/7 (Kunu Tun) To'xtovsiz Ishlatish Qo'llanmasi

Telegram botingiz 24 soat davomida to'xtovsiz ishlashi uchun **2 xil yo'l** mavjud:

---

## 💻 1-USUL: O'z Kompyuteringizda 24/7 Ishlatish (Bepul)

Agar kompyuteringizni (yoki noutbukingizni) o'chirmasdan yoniq qoldirsangiz, bot uzluksiz ishlayveradi.

### 1. Avtomatik qayta tirilish (Watchdog):
Loyiha papkasida [run_24_7.bat](file:///c:/Users/user/Desktop/insatgram%20bek/run_24_7.bat) fayli yaratildi. 
- Agar bot tasodifan to'xtab qolsa yoki internet uzilib qaytsa, ushbu skript **5 soniyadan keyin botni avtomatik ravishda qayta ishga tushiradi**.

### 2. Konsol oynasisiz fonda ishga tushirish:
- [start_hidden.vbs](file:///c:/Users/user/Desktop/insatgram%20bek/start_hidden.vbs) faylini 2 marta bosing. Bot hech qanday qora oynalarsiz, orqa fonda jimgina 24/7 ishlayveradi.

### 3. Kompyuter yoqilganda avtomatik ishga tushishi (Avtozagruzka):
1. Klaviaturada `Win + R` tugmalarini bosing.
2. Chiqqan oynaga `shell:startup` deb yozing va **Enter** bosing.
3. Ochilgan papkaga [start_hidden.vbs](file:///c:/Users/user/Desktop/insatgram%20bek/start_hidden.vbs) faylining yorlig'ini (Yarlik / Shortcut) tashlab qo'ying.
4. Endi har safar kompyuter yonganda bot o'zi avtomatik ishga tushadi!

> ⚠️ *Eslatma: Agar kompyuteringiz o'chsa yoki «Uyqu rejimi»ga (Sleep mode) o'tsa, bot ham to'xtaydi.*

---

## ☁️ 2-USUL: Serverda (VPS yoki Bulutda) 24/7 Ishlatish (Eng Zo'r Usul)

Bu usulda bot maxsus serverda joylashadi. Kompyuteringizni o'chirib qo'ysangiz ham bot internetda kunu tun to'xtovsiz ishlayveradi!

### A) Tayyor Docker orqali (Koyeb / Render / Railway):
Loyiha papkasida [Dockerfile](file:///c:/Users/user/Desktop/insatgram%20bek/Dockerfile) va [Procfile](file:///c:/Users/user/Desktop/insatgram%20bek/Procfile) allaqachon tayyorlangan:
1. Loyihani GitHub'dagi shaxsiy repositoriyingizga yuklaysiz.
2. [Koyeb.com](https://www.koyeb.com) yoki [Railway.app](https://railway.app) platformasida ro'yxatdan o'tasiz.
3. GitHub repositoriyangizni ulab, **Environment Variables** bo'limiga `.env` dagi ma'lumotlarni (`BOT_TOKEN`, `GEMINI_API_KEY`) kiritasiz.
4. Server avtomatik ravishda Docker orqali botni 24/7 ishga tushirib beradi.

### B) Shaxsiy Linux VPS Serverda (Ubuntu):
Agar sizda VPS bo'lsa (Hetzner, VDSina, Reg.ru, DigitalOcean va h.k. - oyiga $2-$3):
1. Serverga kiring va fayllarni yuklang:
   ```bash
   cd /root
   git clone <repo_url> instagram_bot
   cd instagram_bot
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   sudo apt update && sudo apt install -y ffmpeg
   ```
2. Loyiha papkasidagi [instagram_bot.service](file:///c:/Users/user/Desktop/insatgram%20bek/instagram_bot.service) faylini serverdagi `/etc/systemd/system/` papkasiga ko'chiring:
   ```bash
   sudo cp instagram_bot.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable instagram_bot
   sudo systemctl start instagram_bot
   ```
3. Endi bot Linux xizmati sifatida 24/7, yillab to'xtovsiz ishlaydi!
