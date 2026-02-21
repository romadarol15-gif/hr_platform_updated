@echo off
SET PYTHON=python

echo ========================================
echo   УСТАНОВКА HR ПЛАТФОРМЫ v2.0
echo ========================================
echo.

echo [1/6] Создание виртуального окружения...
%PYTHON% -m venv .venv

echo [2/6] Активация виртуального окружения...
call .venv\Scripts\activate.bat

echo [3/6] Обновление pip...
python -m pip install --upgrade pip

echo [4/6] Установка зависимостей...
pip install -r requirements.txt

echo [5/6] Применение миграций...
python manage.py migrate

echo [6/6] Создание суперпользователя admin...
python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); username='admin'; password='admin12345'; email='admin@example.com'; (not User.objects.filter(username=username).exists() and User.objects.create_superuser(username, email, password)); print('OK');"

echo.
echo ========================================
echo   УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!
echo ========================================
echo.
echo Тестовые пользователи: 00000001-00000010
echo Пароль: Pass1234!
echo Админ: admin / admin12345
echo.
echo Новые возможности v2.0:
echo  - Загрузка аватарок
echo  - Отчество для всех пользователей
echo  - Файлы к задачам и образованию
echo  - Поиск по сотрудникам
echo  - Заявки создают задачи для бухгалтера
echo  - Трекер времени с отображением
echo.
pause
