import os
import django
import random
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_platform.settings')
django.setup()

from hr.models import Task

print("Начинаем установку случайных дат в апреле для задач...\n")

# Получаем все задачи
tasks = Task.objects.all()
count = 0

for task in tasks:
    # Генерируем случайный день в апреле (1-30)
    random_day = random.randint(1, 30)
    due_date = date(2026, 4, random_day)
    
    task.due_date = due_date
    task.save(update_fields=['due_date'])
    
    print(f"✓ Задача #{task.id} '{task.title[:50]}' - срок: {due_date.strftime('%d.%m.%Y')}")
    count += 1

print("\n" + "="*60)
print(f"✅ Готово! Обновлено задач: {count}")
print("="*60)
print("\nВсе задачи теперь имеют случайные даты в апреле 2026.\n")
