import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_platform.settings')
django.setup()

from django.contrib.auth.models import User, Group
from hr.models import Employee

print("Начинаем создание тестовых пользователей...\n")

# Создаём группу Бухгалтер
accountant_group, created = Group.objects.get_or_create(name='Бухгалтер')
if created:
    print("✓ Создана группа: Бухгалтер")

# Создаём тестовых пользователей
users_data = [
    {
        'username': 'admin',
        'password': 'admin12345',
        'first_name': 'Admin',
        'last_name': 'Administrator',
        'is_superuser': True,
        'is_staff': True,
        'employee_data': {
            'first_name': 'Admin',
            'last_name': 'Administrator',
            'middle_name': 'Adminovich',
            'role': 'Администратор',
            'position': 'Администратор системы',
            'department': 'IT',
            'phone': '+7-900-1-00-00'
        }
    },
    {
        'username': '00000009',
        'password': 'admin12345',
        'first_name': 'Сергей',
        'last_name': 'Егоров',
        'is_superuser': False,
        'is_staff': False,
        'group': 'Бухгалтер',
        'employee_data': {
            'first_name': 'Сергей',
            'last_name': 'Егоров',
            'middle_name': 'Михайлович',
            'role': 'Бухгалтер',
            'position': 'Бухгалтер',
            'department': 'Finance',
            'phone': '+7-900-9-45-67'
        }
    },
    {
        'username': '00000002',
        'password': 'admin12345',
        'first_name': 'Петр',
        'last_name': 'Иванов',
        'is_superuser': False,
        'is_staff': False,
        'employee_data': {
            'first_name': 'Петр',
            'last_name': 'Иванов',
            'middle_name': 'Алексеевич',
            'role': 'Тестировщик',
            'position': 'QA',
            'department': 'QA',
            'phone': '+7-900-2-45-67'
        }
    },
    {
        'username': '00000008',
        'password': 'admin12345',
        'first_name': 'Николай',
        'last_name': 'Морозов',
        'is_superuser': False,
        'is_staff': False,
        'employee_data': {
            'first_name': 'Николай',
            'last_name': 'Морозов',
            'middle_name': 'Викторович',
            'role': 'Дизайнер',
            'position': 'Дизайнер',
            'department': 'Design',
            'phone': '+7-900-8-45-67'
        }
    },
]

for user_data in users_data:
    # Удаляем старого пользователя если есть
    User.objects.filter(username=user_data['username']).delete()
    
    # Создаём пользователя
    user = User.objects.create_user(
        username=user_data['username'],
        password=user_data['password'],
        first_name=user_data['first_name'],
        last_name=user_data['last_name'],
        is_superuser=user_data['is_superuser'],
        is_staff=user_data['is_staff']
    )
    
    # Добавляем в группу если указана
    if 'group' in user_data:
        group = Group.objects.get(name=user_data['group'])
        user.groups.add(group)
    
    # Создаём профиль сотрудника
    employee, created = Employee.objects.get_or_create(
        user=user,
        defaults=user_data['employee_data']
    )
    
    if not created:
        # Обновляем существующего
        for key, value in user_data['employee_data'].items():
            setattr(employee, key, value)
        employee.save()
    
    group_info = f" (группа: {user_data['group']})" if 'group' in user_data else ""
    superuser_info = " [SUPERUSER]" if user_data['is_superuser'] else ""
    print(f"✓ Создан: {user_data['username']}{superuser_info} - {employee.last_name} {employee.first_name} {employee.middle_name}{group_info}")

print("\n" + "="*60)
print("✅ Все тестовые пользователи созданы!")
print("="*60)
print("\nДля входа используйте:")
print("  - admin / admin12345 (Администратор)")
print("  - 00000009 / admin12345 (Бухгалтер)")
print("  - 00000002 / admin12345 (Тестировщик)")
print("  - 00000008 / admin12345 (Дизайнер)")
print("\nТеперь запустите сервер: python manage.py runserver\n")
