@echo off
SET PYTHON=python

echo ========================================
echo   УСТАНОВКА HR ПЛАТФОРМЫ v2.0
echo ========================================
echo.

echo [1/7] Создание виртуального окружения...
%PYTHON% -m venv .venv

echo [2/7] Активация виртуального окружения...
call .venv\Scripts\activate.bat

echo [3/7] Обновление pip...
python -m pip install --upgrade pip

echo [4/7] Установка зависимостей...
pip install -r requirements.txt

echo [5/7] Применение миграций...
python manage.py migrate

echo [6/7] Создание тестовых пользователей...
python create_test_users.py

echo.
echo ========================================
echo   УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!
echo ========================================
echo.
echo Тестовые пользователи: 00000001-00000010
echo Пароль: Pass1234!
echo Админ: admin / admin12345
echo Бухгалтер: 00000009 / Pass1234!
echo.
echo Новые возможности v2.0:
echo  - Загрузка аватарок
echo  - Поля ФИО в Employee модели
echo  - Разграничение прав доступа (бухгалтер/админ)
echo  - Readonly поля с серым фоном
echo  - Файлы к задачам и образованию
echo  - Поиск по сотрудникам
echo  - Заявки создают задачи для бухгалтера
echo  - Трекер времени
echo.
pause
