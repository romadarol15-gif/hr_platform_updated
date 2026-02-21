from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_test_data(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Group = apps.get_model('auth', 'Group')
    Employee = apps.get_model('hr', 'Employee')
    Task = apps.get_model('hr', 'Task')

    # Создаём группы
    admin_group, _ = Group.objects.get_or_create(name='Админ')
    accountant_group, _ = Group.objects.get_or_create(name='Бухгалтер')
    employee_group, _ = Group.objects.get_or_create(name='Сотрудник')

    # Данные пользователей (username, last_name, first_name, middle_name, role, position, department)
    users_data = [
        ('00000001', 'Петров', 'Иван', 'Сергеевич', 'Сотрудник', 'Разработчик', 'IT'),
        ('00000002', 'Иванов', 'Петр', 'Алексеевич', 'Сотрудник', 'Тестировщик', 'QA'),
        ('00000003', 'Сидоров', 'Сидор', 'Иванович', 'Сотрудник', 'Аналитик', 'Analytics'),
        ('00000004', 'Смирнова', 'Анна', 'Дмитриевна', 'Сотрудник', 'HR-менеджер', 'HR'),
        ('00000005', 'Кузнецова', 'Ольга', 'Петровна', 'Сотрудник', 'Маркетолог', 'Marketing'),
        ('00000006', 'Волков', 'Дмитрий', 'Николаевич', 'Сотрудник', 'Разработчик', 'IT'),
        ('00000007', 'Попова', 'Елена', 'Сергеевна', 'Сотрудник', 'Бизнес-аналитик', 'Business'),
        ('00000008', 'Морозов', 'Николай', 'Викторович', 'Сотрудник', 'Дизайнер', 'Design'),
        ('00000009', 'Егоров', 'Сергей', 'Михайлович', 'Бухгалтер', 'Бухгалтер', 'Finance'),
        ('00000010', 'Админов', 'Админ', 'Админович', 'Администратор', 'Администратор', 'Admin'),
    ]

    password = 'Pass1234!'
    created_users = []

    for username, last_name, first_name, middle_name, role, position, department in users_data:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': f'{username}@hr.local',
                'password': make_password(password)
            }
        )

        if created:
            # Назначаем права
            if role == 'Администратор':
                user.is_staff = True
                user.is_superuser = True
                user.save()
                user.groups.add(admin_group)
            elif role == 'Бухгалтер':
                user.is_staff = True
                user.save()
                user.groups.add(accountant_group)
            else:
                user.groups.add(employee_group)

            # Создаём профиль сотрудника
            Employee.objects.create(
                user=user,
                middle_name=middle_name,
                phone=f'+7-900-{int(username[-3:])}-45-67',
                role=role,
                position=position,
                department=department,
                annual_goal='Достичь ключевых показателей эффективности.',
                internal_experience='2 года работы в компании на текущей должности.',
                external_experience='3 года опыта работы в других компаниях.',
                status='office'
            )
            created_users.append(user)

    # Создаём тестовые задачи
    if created_users:
        admin_user = User.objects.get(username='00000010')
        tasks_data = [
            ('Разработать модуль авторизации', 'Реализовать систему входа с проверкой прав доступа'),
            ('Провести тестирование API', 'Протестировать все эндпоинты на корректность работы'),
            ('Подготовить квартальный отчёт', 'Собрать и проанализировать данные за последний квартал'),
            ('Провести собеседования', 'Провести собеседования с 5 кандидатами на должность junior'),
            ('Запустить рекламную кампанию', 'Настроить таргетированную рекламу в социальных сетях'),
            ('Оптимизировать базу данных', 'Провести анализ и оптимизацию узких мест в БД'),
            ('Подготовить бизнес-план', 'Разработать бизнес-план на следующий квартал'),
            ('Обновить дизайн главной страницы', 'Создать новые макеты для главной страницы сайта'),
        ]

        for i, user in enumerate(created_users[:-2]):  # Не назначаем бухгалтеру и админу
            if i < len(tasks_data):
                Task.objects.create(
                    title=tasks_data[i][0],
                    description=tasks_data[i][1],
                    creator=admin_user,
                    assignee=user,
                    status='new'
                )

def remove_test_data(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Group = apps.get_model('auth', 'Group')

    for i in range(1, 11):
        User.objects.filter(username=f'{i:08d}').delete()

    Group.objects.filter(name__in=['Админ', 'Бухгалтер', 'Сотрудник']).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('hr', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length')
    ]

    operations = [
        migrations.RunPython(create_test_data, remove_test_data)
    ]
