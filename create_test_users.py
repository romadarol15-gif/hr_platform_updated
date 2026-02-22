import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_platform.settings')
django.setup()

from django.contrib.auth.models import User, Group
from hr.models import Employee

print("Начинаем обновление данных пользователей...\n")

# Создаём группу Бухгалтер
accountant_group, created = Group.objects.get_or_create(name='Бухгалтер')
if created:
    print("✓ Создана группа: Бухгалтер")

# Обновляем / создаём пользователей
users_data = [
    {
        'username': 'admin',
        'password': 'Pass1234!',  # Изменён пароль для admin
        'first_name': 'Admin',
        'last_name': 'Administrator',
        'is_superuser': True,
        'is_staff': True,
        'update_password': True,  # Обновляем пароль для admin
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
        'password': 'Pass1234!',  # Оставляем прежний пароль
        'first_name': 'Сергей',
        'last_name': 'Егоров',
        'is_superuser': False,
        'is_staff': False,
        'update_password': False,  # НЕ обновляем пароль
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
]

for user_data in users_data:
    # Проверяем существует ли пользователь
    user = User.objects.filter(username=user_data['username']).first()
    
    if user:
        # Обновляем существующего
        user.first_name = user_data['first_name']
        user.last_name = user_data['last_name']
        user.is_superuser = user_data['is_superuser']
        user.is_staff = user_data['is_staff']
        
        # Обновляем пароль только если указано
        if user_data.get('update_password', False):
            user.set_password(user_data['password'])
        
        user.save()
        action = "Обновлён"
    else:
        # Создаём нового
        user = User.objects.create_user(
            username=user_data['username'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            is_superuser=user_data['is_superuser'],
            is_staff=user_data['is_staff']
        )
        action = "Создан"
    
    # Добавляем в группу если указана
    if 'group' in user_data:
        group = Group.objects.get(name=user_data['group'])
        user.groups.clear()
        user.groups.add(group)
    
    # Обновляем или создаём профиль сотрудника
    employee, emp_created = Employee.objects.get_or_create(
        user=user,
        defaults=user_data['employee_data']
    )
    
    if not emp_created:
        # Обновляем существующего
        for key, value in user_data['employee_data'].items():
            setattr(employee, key, value)
        employee.save()
    
    group_info = f" (группа: {user_data['group']})" if 'group' in user_data else ""
    superuser_info = " [SUPERUSER]" if user_data['is_superuser'] else ""
    password_info = f" [пароль: {user_data['password']}]" if user_data.get('update_password', False) else ""
    print(f"✓ {action}: {user_data['username']}{superuser_info} - {employee.last_name} {employee.first_name} {employee.middle_name}{group_info}{password_info}")

# Копируем ФИО для всех остальных пользователей
print("\nКопирование ФИО для остальных пользователей...")
other_count = 0
for employee in Employee.objects.exclude(user__username__in=['admin', '00000009']):
    if employee.user:
        employee.first_name = employee.user.first_name
        employee.last_name = employee.user.last_name
        employee.save(update_fields=['first_name', 'last_name'])
        print(f"✓ {employee.user.username} - {employee.last_name} {employee.first_name} {employee.middle_name}")
        other_count += 1

print("\n" + "="*60)
print("✅ Обновление завершено!")
print("="*60)
print(f"\nОбновлено пользователей: {len(users_data)}")
if other_count > 0:
    print(f"Скопировано ФИО для: {other_count}")
print("\nДля входа используйте:")
print("  - admin / Pass1234! (Администратор)")
print("  - 00000009 / Pass1234! (Бухгалтер)")
print("  - Остальные 00000001-00000010 / Pass1234!")
print("\n")
