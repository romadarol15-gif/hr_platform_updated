import os
import django
from datetime import date, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

from django.contrib.auth.models import User
from hr.models import Employee, PositionHistory

print("Начинаем обновление данных сотрудников...\n")

# Удаляем старую историю
PositionHistory.objects.all().delete()
print("✓ Удалена старая история должностей\n")

# Обрабатываем каждого сотрудника
employees = Employee.objects.all()

for employee in employees:
    # Устанавливаем email
    employee.email = f"{employee.user.username}@company.com"
    
    # Устанавливаем дату приёма (случайная в прошлом)
    if not employee.hire_date:
        # От 1 до 3 лет назад
        days_ago = random.randint(365, 1095)
        employee.hire_date = date.today() - timedelta(days=days_ago)
    
    employee.save()
    
    # Создаём историю должности
    PositionHistory.objects.create(
        employee=employee,
        position=employee.position,
        start_date=employee.hire_date
    )
    
    # Обновляем internal_experience
    employee.internal_experience = employee.get_work_experience()
    employee.save()
    
    print(f"✓ {employee.user.username} - {employee.get_full_name()}")
    print(f"  Email: {employee.email}")
    print(f"  Дата приёма: {employee.hire_date.strftime('%d.%m.%Y')}")
    print(f"  Опыт: {employee.internal_experience}")
    print()

print("="*60)
print("✅ Обновление завершено!")
print("="*60)
