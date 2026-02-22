@echo off
SET PYTHON=python

echo ========================================
echo   INSTALL HR-PLATFORM v3.0
echo ========================================
echo.

echo [1/10] Creating virtual environment...
%PYTHON% -m venv .venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/10] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo [3/10] Updating pip...
python -m pip install --upgrade pip --quiet

echo [4/10] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [5/10] Merging migrations (if needed)...
echo y | python manage.py makemigrations --merge 2>nul

echo [6/10] Applying migrations...
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Failed to apply migrations
    echo Try deleting db.sqlite3 and run install.bat again
    pause
    exit /b 1
)

echo [7/10] Creating superuser admin...
echo from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@company.com', 'Pass1234!') | python manage.py shell
if errorlevel 1 (
    echo ERROR: Failed to create admin
    pause
    exit /b 1
)

echo [8/10] Creating test users...
python create_test_users.py
if errorlevel 1 (
    echo ERROR: Failed to create users
    pause
    exit /b 1
)

echo [9/10] Creating test tasks...
python create_tasks.py
if errorlevel 1 (
    echo ERROR: Failed to create tasks
    pause
    exit /b 1
)

echo.
echo ========================================
echo   INSTALLATION COMPLETE!
echo ========================================
echo.
echo To start the server use: run.bat
echo.
echo Login credentials:
echo  - Admin: admin / Pass1234!
echo  - Accountant: 00000009 / Pass1234!
echo  - Employees: 00000001-00000010 / Pass1234!
echo.
echo Automatically created:
echo  - 10 employees
echo  - 15 tasks (new, in progress, completed)
echo.
echo New features v3.0:
echo  - Fire/restore employees
echo  - Hire date and position history
echo  - Employee emails
echo  - Task IDs TASK-X
echo  - Automatic task creation
echo.
pause
