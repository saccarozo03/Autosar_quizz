@echo off
title AUTOSAR Quiz
echo Đang chạy Flask app...
start "" /B python app.py
timeout /t 2 >nul
start http://localhost:5000/