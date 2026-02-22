import os
import django
from datetime import date, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

from django.contrib.auth.models import User
from hr.models import Task, Employee

print("Начинаем обновление задач...\n")

# Удаляем все задачи
old_count = Task.objects.count()
Task.objects.all().delete()
print(f"✓ Удалено старых задач: {old_count}\n")

# Шаблоны задач по должностям
task_templates = {
    'Разработчик': [
        'Рефакторинг модуля авторизации',
        'Исправление багов в API',
        'Разработка нового функционала',
        'Написание юнит-тестов',
        'Оптимизация запросов к базе',
        'Обновление документации',
    ],
    'Бухгалтер': [
        'Подготовка финансового отчёта',
        'Обработка заявок на отпуск',
        'Расчёт зарплаты за месяц',
        'Проверка первичных документов',
        'Сверка с контрагентами',
    ],
    'Менеджер': [
        'Проведение встречи с клиентом',
        'Подготовка коммерческого предложения',
        'Анализ рынка конкурентов',
        'Обзвон потенциальных клиентов',
        'Оформление договора',
    ],
    'Аналитик': [
        'Анализ пользовательских метрик',
        'Подготовка дашборда в Tableau',
        'Исследование воронки продаж',
        'Сегментация клиентской базы',
        'A/B тестирование нового функционала',
    ],
    'Дефолт': [
        'Подготовка отчёта по проекту',
        'Обновление рабочей документации',
        'Участие в командной встрече',
        'Проверка входящей корреспонденции',
        'Организация рабочего процесса',
    ]
}

# Получаем admin
admin_user = User.objects.get(username='admin')

# Получаем всех сотрудников кроме admin
users = User.objects.exclude(username='admin').filter(is_active=True)

created_count = 0

for user in users:
    employee = getattr(user, 'employee_profile', None)
    if not employee:
        continue
    
    # Определяем шаблоны задач по должности
    position_key = None
    for key in task_templates.keys():
        if key.lower() in employee.position.lower():
            position_key = key
            break
    
    if not position_key:
        position_key = 'Дефолт'
    
    templates = task_templates[position_key]
    
    # Создаём 2 задачи
    selected_tasks = random.sample(templates, min(2, len(templates)))
    
    for i, task_title in enumerate(selected_tasks):
        # Статус: первая задача - новая, вторая - в работе
        status = 'new' if i == 0 else 'in_progress'
        
        # Срок выполнения: от 3 до 14 дней
        due_date = date.today() + timedelta(days=random.randint(3, 14))
        
        task = Task.objects.create(
            title=task_title,
            description=f"Необходимо выполнить: {task_title.lower()}",
            creator=admin_user,
            assignee=user,
            status=status,
            due_date=due_date
        )
        
        created_count += 1
        print(f"✓ {task.get_task_id()} | {user.username} ({employee.position}) | {task_title} | {task.get_status_display()}")

print("\n" + "="*60)
print(f"✅ Создано новых задач: {created_count}")
print("="*60)
