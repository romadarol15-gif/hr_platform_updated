@echo off
SET PYTHON=python

echo ========================================
echo   УСТАНОВКА HR-ПЛАТФОРМЫ v3.0
echo ========================================
echo.

echo [1/9] Создание виртуального окружения...
%PYTHON% -m venv .venv
if errorlevel 1 (
    echo ОШИБКА: Не удалось создать виртуальное окружение
    pause
    exit /b 1
)

echo [2/9] Активация виртуального окружения...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ОШИБКА: Не удалось активировать виртуальное окружение
    pause
    exit /b 1
)

echo [3/9] Обновление pip...
python -m pip install --upgrade pip --quiet

echo [4/9] Установка зависимостей...
pip install -r requirements.txt
if errorlevel 1 (
    echo ОШИБКА: Не удалось установить зависимости
    pause
    exit /b 1
)

echo [5/9] Объединение миграций (если нужно)...
echo y | python manage.py makemigrations --merge 2>nul

echo [6/9] Применение миграций...
python manage.py migrate
if errorlevel 1 (
    echo ОШИБКА: Не удалось применить миграции
    echo Попробуйте удалить db.sqlite3 и запустить install.bat заново
    pause
    exit /b 1
)

echo [7/9] Создание суперпользователя admin...
echo from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@company.com', 'Pass1234!') | python manage.py shell
if errorlevel 1 (
    echo ОШИБКА: Не удалось создать admin
    pause
    exit /b 1
)

echo [8/9] Создание тестовых пользователей...
python create_test_users.py
if errorlevel 1 (
    echo ОШИБКА: Не удалось создать пользователей
    pause
    exit /b 1
)

echo.
echo ========================================
echo   УСТАНОВКА ЗАВЕРШЕНА!
echo ========================================
echo.
echo Для запуска сервера используйте: run.bat
echo.
echo Учетные данные:
echo  - Админ: admin / Pass1234!
echo  - Бухгалтер: 00000009 / Pass1234!
echo  - Сотрудники: 00000001-00000010 / Pass1234!
echo.
echo Новые возможности v3.0:
echo  - Увольнение/восстановление сотрудников
echo  - Дата приема и история должностей
echo  - Email сотрудников
echo  - ID задач TASK-X
echo.
echo Создайте задачи: python create_tasks.py
echo.
pause
