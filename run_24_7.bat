@echo off
title Instagram & AI Telegram Bot (24/7 Rejim)
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================================
echo   Telegram Bot 24/7 Rejimda Ishga Tushirilmoqda...
echo   Bot to'xtab qolsa, u avtomatik ravishda qayta ishga tushadi.
echo   Oynani yopmang! Yashirish uchun fon rejimida ishlating.
echo ========================================================
echo.

:loop
echo [%date% %time%] Bot ishga tushirilmoqda...
".\venv\Scripts\python.exe" bot.py
echo.
echo [%date% %time%] OGOHLANTIRISH: Bot to'xtadi!
echo 5 soniyadan keyin avtomatik qayta ishga tushiriladi...
timeout /t 5 /nobreak > nul
echo Qayta ishga tushirilmoqda...
echo.
goto loop
