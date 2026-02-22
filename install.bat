@echo off
SET PYTHON=python

echo ========================================
echo   УСТАНОВКА HR ПЛАТФОРМЫ v2.0
echo ========================================
echo.

echo [1/8] Создание виртуального окружения...
%PYTHON% -m venv .venv
if errorlevel 1 (
    echo ОШИБКА: Не удалось создать виртуальное окружение
    pause
    exit /b 1
)

echo [2/8] Активация виртуального окружения...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ОШИБКА: Не удалось активировать виртуальное окружение
    pause
    exit /b 1
)

echo [3/8] Обновление pip...
python -m pip install --upgrade pip --quiet

echo [4/8] Установка зависимостей...
pip install -r requirements.txt
if errorlevel 1 (
    echo ОШИБКА: Не удалось установить зависимости
    pause
    exit /b 1
)

echo [5/8] Объединение миграций (если нужно)...
echo y | python manage.py makemigrations --merge 2>nul

echo [6/8] Применение миграций...
python manage.py migrate
if errorlevel 1 (
    echo ОШИБКА: Не удалось применить миграции
    echo Попробуйте удалить db.sqlite3 и запустить install.bat заново
    pause
    exit /b 1
)

echo [7/8] Обновление данных пользователей...
python create_test_users.py
if errorlevel 1 (
    echo ОШИБКА: Не удалось обновить пользователей
    pause
    exit /b 1
)

echo.
echo ========================================
echo   УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!
echo ========================================
echo.
echo Для запуска сервера используйте: run.bat
echo.
echo Учетные данные:
echo  - Админ: admin / Pass1234!
echo  - Бухгалтер: 00000009 / Pass1234!
echo  - Сотрудники: 00000001-00000010 / Pass1234!
echo.
echo Новые возможности v2.0:
echo  - Поля ФИО в Employee модели
echo  - Разграничение прав (бухгалтер/админ)
echo  - Readonly поля с серым фоном
echo  - Загрузка аватарок и файлов
echo  - Поиск по сотрудникам
echo  - Сортировка задач: завершенные в конце
echo  - Трекер времени
echo.
pause
