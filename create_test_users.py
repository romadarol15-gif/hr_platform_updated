import os
import django
from datetime import date, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

from django.contrib.auth.models import User, Group
from hr.models import Employee, PositionHistory

print("Удаление всех пользователей кроме admin...")
User.objects.exclude(username='admin').delete()
print("✓ Пользователи удалены\n")

# Создание группы Бухгалтер
accountant_group, created = Group.objects.get_or_create(name='Бухгалтер')
print(f"{'✓ Создана' if created else '✓ Найдена'} группа: Бухгалтер\n")

users_data = [
    # ИД, ФИО, Должность, Отдел, Роль, Дата приёма (дней назад)
    ('00000001', 'Петров', 'Иван', 'Иванович', 'Разработчик', 'IT', 'Сотрудник', 730),  # 2 года
    ('00000002', 'Сидорова', 'Анна', 'Петровна', 'Дизайнер', 'Креатив', 'Сотрудник', 580),  # ~1.6 года
    ('00000003', 'Кузнецов', 'Дмитрий', 'Сергеевич', 'Разработчик', 'IT', 'Сотрудник', 912),  # 2.5 года
    ('00000004', 'Смирнова', 'Ольга', 'Александровна', 'Менеджер', 'Продажи', 'Сотрудник', 450),  # ~1.2 года
    ('00000005', 'Новиков', 'Алексей', 'Викторович', 'Разработчик', 'IT', 'Сотрудник', 365),  # 1 год
    ('00000006', 'Васильева', 'Елена', 'Николаевна', 'Дизайнер', 'Креатив', 'Сотрудник', 655),  # ~1.8 года
    ('00000007', 'Михайлов', 'Сергей', 'Андреевич', 'Разработчик', 'IT', 'Сотрудник', 1095),  # 3 года
    ('00000008', 'Федорова', 'Наталья', 'Владимировна', 'Менеджер', 'Продажи', 'Сотрудник', 270),  # ~9 месяцев
    ('00000009', 'Соколова', 'Мария', 'Ивановна', 'Бухгалтер', 'Финансы', 'Бухгалтер', 1460),  # 4 года
    ('00000010', 'Захаров', 'Павел', 'Дмитриевич', 'Разработчик', 'IT', 'Сотрудник', 180),  # ~6 месяцев
]

print("Создание пользователей:\n")

for username, last_name, first_name, middle_name, position, department, role, days_ago in users_data:
    # Создаём пользователя
    user = User.objects.create_user(
        username=username,
        password='Pass1234!',
        first_name=first_name,
        last_name=last_name
    )
    
    # Добавляем в группу Бухгалтер если нужно
    if role == 'Бухгалтер':
        user.groups.add(accountant_group)
    
    # Вычисляем дату приёма
    hire_date = date.today() - timedelta(days=days_ago)
    
    # Создаём профиль
    employee = Employee.objects.create(
        user=user,
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        position=position,
        department=department,
        role=role,
        email=f"{username}@company.com",
        phone=f"+7-{random.randint(900, 999)}-{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}",
        hire_date=hire_date,
        annual_goal='Повышение квалификации и участие в важных проектах',
        external_experience='Опыт работы в других компаниях',
        status='office'
    )
    
    # Создаём начальную историю должности
    PositionHistory.objects.create(
        employee=employee,
        position=position,
        start_date=hire_date,
        end_date=None  # Текущая должность
    )
    
    # Обновляем опыт
    employee.internal_experience = employee.get_work_experience()
    employee.save()
    
    group_info = f" [{role}]" if role == 'Бухгалтер' else ""
    print(f"✓ {username}: {last_name} {first_name} {middle_name} - {position} ({department}){group_info}")
    print(f"  Email: {employee.email} | Дата приёма: {hire_date.strftime('%d.%m.%Y')}")

print("\n" + "="*60)
print("✅ Все пользователи созданы!")
print("="*60)
print("\nДля входа используйте:")
print("  Логин: 00000001-00000010")
print("  Пароль: Pass1234!\n")
print("👨‍💼 Бухгалтер: 00000009 / Pass1234!")
print("🔑 Admin: admin / Pass1234!\n")
