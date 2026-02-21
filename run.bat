@echo off
call .venv\Scripts\activate.bat
echo.
echo ========================================
echo   HR ПЛАТФОРМА v2.0
echo   Запуск на http://127.0.0.1:8000/
echo ========================================
echo.
python manage.py runserver 127.0.0.1:8000
pause
