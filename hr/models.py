from django.db import models
from django.contrib.auth.models import User
from datetime import date, datetime

class Employee(models.Model):
    """Модель сотрудника с расширенными полями"""
    STATUS_CHOICES = [
        ('office', 'В офисе'),
        ('remote', 'Удаленно'),
        ('vacation', 'В отпуске'),
        ('sick', 'Больничный'),
        ('other', 'Другой')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile', verbose_name='Пользователь')
    
    # Поля ФИО
    last_name = models.CharField(max_length=150, blank=True, verbose_name='Фамилия')
    first_name = models.CharField(max_length=150, blank=True, verbose_name='Имя')
    middle_name = models.CharField(max_length=100, blank=True, verbose_name='Отчество')
    
    email = models.EmailField(max_length=200, blank=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    role = models.CharField(max_length=100, verbose_name='Роль')
    position = models.CharField(max_length=100, verbose_name='Должность')
    department = models.CharField(max_length=100, blank=True, verbose_name='Отдел')
    hire_date = models.DateField(null=True, blank=True, verbose_name='Дата приёма на работу')
    annual_goal = models.TextField(blank=True, verbose_name='Цели на год')
    internal_experience = models.TextField(blank=True, verbose_name='Опыт внутри компании')
    external_experience = models.TextField(blank=True, verbose_name='Опыт вне компании')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='office', verbose_name='Статус')

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return self.get_full_name() or self.user.username

    def get_full_name(self):
        """Возвращает полное ФИО"""
        parts = [self.last_name, self.first_name, self.middle_name]
        return ' '.join(filter(None, parts))
    
    def get_work_experience(self):
        """Возвращает опыт работы с периодами должностей"""
        history = self.position_history.all().order_by('start_date')
        experience_lines = []
        
        for entry in history:
            # Рассчитываем длительность
            end = entry.end_date or date.today()
            delta = end - entry.start_date
            years = delta.days // 365
            days = delta.days % 365
            
            # Форматируем строку с периодом
            duration = f"{years} лет {days} дней" if years > 0 else f"{days} дней"
            start_str = entry.start_date.strftime("%d.%m.%Y")
            end_str = entry.end_date.strftime("%d.%m.%Y") if entry.end_date else "настоящее время"
            
            line = f"{entry.position}: с {start_str} по {end_str} ({duration})"
            experience_lines.append(line)
        
        return "\n".join(experience_lines) if experience_lines else "Опыт не указан"
    
    def update_position_history(self, new_position):
        """Обновляет историю должностей при смене"""
        # Закрываем текущую должность
        current = self.position_history.filter(end_date__isnull=True).first()
        if current:
            current.end_date = date.today()
            current.save()
        
        # Создаём новую запись
        PositionHistory.objects.create(
            employee=self,
            position=new_position,
            start_date=date.today()
        )

class PositionHistory(models.Model):
    """История должностей сотрудника"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='position_history', verbose_name='Сотрудник')
    position = models.CharField(max_length=100, verbose_name='Должность')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(null=True, blank=True, verbose_name='Дата окончания')

    class Meta:
        verbose_name = 'История должности'
        verbose_name_plural = 'История должностей'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.position}"

class Education(models.Model):
    """Модель образования с прикрепляемыми файлами"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='educations', verbose_name='Сотрудник')
    institution = models.CharField(max_length=200, verbose_name='Учебное заведение')
    degree = models.CharField(max_length=100, verbose_name='Степень/Квалификация')
    field_of_study = models.CharField(max_length=200, verbose_name='Специальность')
    start_year = models.IntegerField(verbose_name='Год начала')
    end_year = models.IntegerField(null=True, blank=True, verbose_name='Год окончания')
    description = models.TextField(blank=True, verbose_name='Описание')
    diploma_file = models.FileField(upload_to='education_docs/', blank=True, null=True, verbose_name='Диплом/Сертификат')

    class Meta:
        verbose_name = 'Образование'
        verbose_name_plural = 'Образования'
        ordering = ['-end_year']

    def __str__(self):
        return f"{self.institution} - {self.degree}"

class Task(models.Model):
    """Модель задачи с прикрепляемыми файлами"""
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('done', 'Завершена')
    ]

    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks', verbose_name='Создатель')
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks', verbose_name='Исполнитель')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    due_date = models.DateField(null=True, blank=True, verbose_name='Срок выполнения')
    attachment = models.FileField(upload_to='task_attachments/', blank=True, null=True, verbose_name='Вложение')

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    def get_task_id(self):
        """Возвращает ID задачи в формате TASK-X"""
        return f"TASK-{self.id}"
    
    def is_assignee_fired(self):
        """Проверяет уволен ли исполнитель"""
        return not self.assignee.is_active

class WorkSchedule(models.Model):
    """График работы"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='schedules', verbose_name='Сотрудник')
    date = models.DateField(verbose_name='Дата')
    start_time = models.TimeField(verbose_name='Время начала')
    end_time = models.TimeField(verbose_name='Время окончания')

    class Meta:
        verbose_name = 'График работы'
        verbose_name_plural = 'Графики работы'
        ordering = ['date']

    def __str__(self):
        return f'{self.employee} - {self.date}'

class WorkRequest(models.Model):
    """Заявка на отпуск/справку - автоматически создаёт задачу для бухгалтера"""
    REQUEST_TYPE_CHOICES = [
        ('vacation', 'Отпуск'),
        ('certificate', 'Справка'),
        ('other', 'Другое')
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='requests', verbose_name='Сотрудник')
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES, verbose_name='Тип заявки')
    description = models.TextField(verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    approved = models.BooleanField(default=False, verbose_name='Одобрено')
    related_task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True, related_name='work_request', verbose_name='Связанная задача')

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_request_type_display()} - {self.employee}'

class TimeEntry(models.Model):
    """Запись трекера времени"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='time_entries', verbose_name='Сотрудник')
    start_time = models.DateTimeField(verbose_name='Начало')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='Окончание')

    class Meta:
        verbose_name = 'Запись времени'
        verbose_name_plural = 'Записи времени'
        ordering = ['-start_time']

    def __str__(self):
        return f'{self.employee} - {self.start_time}'

    def get_duration(self):
        """Возвращает длительность работы"""
        from django.utils import timezone
        from datetime import timedelta

        if self.end_time:
            delta = self.end_time - self.start_time
        else:
            delta = timezone.now() - self.start_time

        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        return f"{hours}ч {minutes}мин"
