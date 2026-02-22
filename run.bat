@echo off
call .venv\Scripts\activate.bat
echo.
echo ========================================
echo   HR PLATFORM v3.0
echo   Running on http://127.0.0.1:8000/
echo ========================================
echo.
python manage.py runserver 127.0.0.1:8000
pause
