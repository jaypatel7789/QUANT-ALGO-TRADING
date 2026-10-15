@echo off
title MT5 BTCUSD# Algorithmic Trading Bot
cd /d "%~dp0"
echo ========================================================
echo       Launching MT5 BTC/USD Algorithmic Bot             
echo       Account: 1301597088 (XMGlobal)                    
echo ========================================================
.\venv\Scripts\python core\mt5_live_bot.py
pause
