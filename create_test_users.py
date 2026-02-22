import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

from django.contrib.auth.models import User, Group
from hr.models import Employee

print("Начинаем обновление данных пользователей...\n")

# Удаляем старого админа 00000010 если он есть
try:
    old_admin = User.objects.get(username='00000010')
    old_admin.delete()
    print("✓ Удалён старый пользователь 00000010")
except User.DoesNotExist:
    pass

# Создаём группу Бухгалтер
accountant_group, created = Group.objects.get_or_create(name='Бухгалтер')
if created:
    print("✓ Создана группа: Бухгалтер")

# Создаём / обновляем пользователей
users_data = [
    {
        'username': 'admin',
        'password': 'Pass1234!',
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
            'phone': '+7-900-000-00-00'
        }
    },
    {
        'username': '00000009',
        'password': 'Pass1234!',
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
]

for user_data in users_data:
    # Удаляем старого пользователя и создаём заново
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
    Employee.objects.create(
        user=user,
        **user_data['employee_data']
    )
    
    group_info = f" (группа: {user_data['group']})" if 'group' in user_data else ""
    superuser_info = " [SUPERUSER]" if user_data['is_superuser'] else ""
    print(f"✓ Создан: {user_data['username']}{superuser_info} - {user_data['employee_data']['last_name']} {user_data['employee_data']['first_name']} {user_data['employee_data']['middle_name']}{group_info} [пароль: {user_data['password']}]")

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
print(f"\nСоздано пользователей: {len(users_data)}")
if other_count > 0:
    print(f"Скопировано ФИО для: {other_count}")
print("\nДля входа используйте:")
print("  - admin / Pass1234! (Администратор)")
print("  - 00000009 / Pass1234! (Бухгалтер)")
print("  - Остальные 00000001-00000008 / Pass1234!")
print("\n")
