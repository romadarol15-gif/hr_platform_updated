from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('middle_name', models.CharField(blank=True, max_length=100, verbose_name='Отчество')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Телефон')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/', verbose_name='Аватар')),
                ('role', models.CharField(max_length=100, verbose_name='Роль')),
                ('position', models.CharField(max_length=100, verbose_name='Должность')),
                ('department', models.CharField(blank=True, max_length=100, verbose_name='Отдел')),
                ('annual_goal', models.TextField(blank=True, verbose_name='Цели на год')),
                ('internal_experience', models.TextField(blank=True, verbose_name='Опыт внутри компании')),
                ('external_experience', models.TextField(blank=True, verbose_name='Опыт вне компании')),
                ('status', models.CharField(choices=[('office', 'В офисе'), ('remote', 'Удаленно'), ('vacation', 'В отпуске'), ('sick', 'Больничный'), ('other', 'Другой')], default='office', max_length=20, verbose_name='Статус')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='employee_profile', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={'verbose_name': 'Сотрудник', 'verbose_name_plural': 'Сотрудники'},
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('institution', models.CharField(max_length=200, verbose_name='Учебное заведение')),
                ('degree', models.CharField(max_length=100, verbose_name='Степень/Квалификация')),
                ('field_of_study', models.CharField(max_length=200, verbose_name='Специальность')),
                ('start_year', models.IntegerField(verbose_name='Год начала')),
                ('end_year', models.IntegerField(blank=True, null=True, verbose_name='Год окончания')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('diploma_file', models.FileField(blank=True, null=True, upload_to='education_docs/', verbose_name='Диплом/Сертификат')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='educations', to='hr.employee', verbose_name='Сотрудник')),
            ],
            options={'verbose_name': 'Образование', 'verbose_name_plural': 'Образования', 'ordering': ['-end_year']},
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200, verbose_name='Название')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('status', models.CharField(choices=[('new', 'Новая'), ('in_progress', 'В работе'), ('done', 'Завершена')], default='new', max_length=20, verbose_name='Статус')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('due_date', models.DateField(blank=True, null=True, verbose_name='Срок выполнения')),
                ('attachment', models.FileField(blank=True, null=True, upload_to='task_attachments/', verbose_name='Вложение')),
                ('assignee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_tasks', to=settings.AUTH_USER_MODEL, verbose_name='Исполнитель')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_tasks', to=settings.AUTH_USER_MODEL, verbose_name='Создатель')),
            ],
            options={'verbose_name': 'Задача', 'verbose_name_plural': 'Задачи', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='WorkSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('date', models.DateField(verbose_name='Дата')),
                ('start_time', models.TimeField(verbose_name='Время начала')),
                ('end_time', models.TimeField(verbose_name='Время окончания')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='hr.employee', verbose_name='Сотрудник')),
            ],
            options={'verbose_name': 'График работы', 'verbose_name_plural': 'Графики работы', 'ordering': ['date']},
        ),
        migrations.CreateModel(
            name='WorkRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('request_type', models.CharField(choices=[('vacation', 'Отпуск'), ('certificate', 'Справка'), ('other', 'Другое')], max_length=20, verbose_name='Тип заявки')),
                ('description', models.TextField(verbose_name='Описание')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('approved', models.BooleanField(default=False, verbose_name='Одобрено')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='hr.employee', verbose_name='Сотрудник')),
                ('related_task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='work_request', to='hr.task', verbose_name='Связанная задача')),
            ],
            options={'verbose_name': 'Заявка', 'verbose_name_plural': 'Заявки', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='TimeEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('start_time', models.DateTimeField(verbose_name='Начало')),
                ('end_time', models.DateTimeField(blank=True, null=True, verbose_name='Окончание')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='time_entries', to='hr.employee', verbose_name='Сотрудник')),
            ],
            options={'verbose_name': 'Запись времени', 'verbose_name_plural': 'Записи времени', 'ordering': ['-start_time']},
        ),
    ]
