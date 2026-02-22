import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

from hr.models import Employee

print("Начинаем копирование данных ФИО из User в Employee...\n")

# Копируем данные из User в Employee
count = 0
for employee in Employee.objects.all():
    if employee.user:
        # Копируем ФИО
        employee.first_name = employee.user.first_name
        employee.last_name = employee.user.last_name
        employee.save(update_fields=['first_name', 'last_name'])
        print(f"✓ Обновлён: {employee.user.username} - {employee.last_name} {employee.first_name} {employee.middle_name}")
        count += 1

print(f"\n✅ Готово! Обновлено записей: {count}")
print("\nТеперь можете запустить сервер: python manage.py runserver")
