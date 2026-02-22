from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q, Case, When, IntegerField
from .forms import EmployeeSelfForm, EmployeeRestrictedForm, EmployeeFullForm, EmployeeCreateForm, TaskForm, WorkRequestForm, EducationForm, DocumentForm
from .models import Employee, Task, WorkRequest, TimeEntry, Education, Document, PositionHistory
from datetime import date, timedelta
import calendar

# Русские названия месяцев
MONTH_NAMES_RU = {
    1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
    5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
    9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
}

def user_login(request):
    """Вход в систему (включая уволенных)"""
    if request.user.is_authenticated:
        return redirect('hr:index')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Проверяем пароль вручную для неактивных пользователей
        try:
            user_obj = User.objects.get(username=username)
            if not user_obj.is_active:
                # Для неактивных проверяем пароль вручную
                if user_obj.check_password(password):
                    # Временно активируем для входа
                    user_obj.is_active = True
                    user_obj.save()
                    login(request, user_obj)
                    # Сразу деактивируем обратно
                    user_obj.is_active = False
                    user_obj.save()
                    messages.warning(request, 'Вы вошли как уволенный сотрудник. Доступ ограничен.')
                    return redirect('hr:index')
                else:
                    messages.error(request, 'Неверный логин или пароль')
                    return render(request, 'login.html')
        except User.DoesNotExist:
            pass
        
        # Стандартная аутентификация для активных
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Добро пожаловать!')
            return redirect('hr:index')
        else:
            messages.error(request, 'Неверный логин или пароль')
    return render(request, 'login.html')

@login_required
def user_logout(request):
    """Выход из системы"""
    logout(request)
    return redirect('hr:login')

@login_required
def index(request):
    """Главная страница"""
    employee = getattr(request.user, 'employee_profile', None)
    active_entry = None
    tasks = []

    if employee:
        active_entry = employee.time_entries.filter(end_time__isnull=True).first()
        # На главной только задачи со статусом "Новая"
        tasks = Task.objects.filter(
            assignee=request.user, 
            status='new'
        ).order_by('-created_at')[:10]

    return render(request, 'index.html', {
        'employee': employee,
        'active_entry': active_entry,
        'tasks': tasks
    })

@login_required
def profile(request, employee_id=None):
    """Просмотр и редактирование профиля"""
    # Проверяем права админа/бухгалтера
    is_admin_or_accountant = (
        request.user.is_superuser or 
        request.user.groups.filter(name='Бухгалтер').exists()
    )
    
    # Определяем чей профиль смотрим
    if employee_id:
        employee = get_object_or_404(Employee, id=employee_id)
        is_owner = request.user == employee.user
        
        # Редактировать может только владелец, бухгалтер или админ
        # Но уволенных может редактировать только админ
        if not employee.user.is_active:
            can_edit = request.user.is_superuser
        else:
            can_edit = is_owner or is_admin_or_accountant
    else:
        # Свой профиль
        employee, _ = Employee.objects.get_or_create(
            user=request.user,
            defaults={'role': 'Сотрудник', 'position': 'Специалист'}
        )
        is_owner = True
        can_edit = True

    # Определяем какую форму использовать
    if is_admin_or_accountant:
        # Admin/бухгалтер - полный доступ
        FormClass = EmployeeFullForm
    elif is_owner:
        # Владелец своего профиля - может редактировать Телефон/Аватар/Статус
        FormClass = EmployeeSelfForm
    else:
        # Чужой профиль - только просмотр
        FormClass = EmployeeRestrictedForm

    if request.method == 'POST' and can_edit:
        # Сохраняем старую должность ДО save!
        old_position = employee.position
        
        form = FormClass(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            employee = form.save()
            
            # Если должность изменилась - обновляем историю
            if old_position != employee.position:
                employee.update_position_history(employee.position)
                employee.internal_experience = employee.get_work_experience()
                employee.save()
            
            messages.success(request, 'Профиль обновлён')
            if employee_id:
                return redirect('hr:profile_view', employee_id=employee.id)
            else:
                return redirect('hr:profile')
        else:
            # Показываем ошибки формы
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = FormClass(instance=employee)

    # Образование
    educations = employee.educations.all()
    
    # Документы - владелец видит свои, admin/бухгалтер - все
    if is_owner or is_admin_or_accountant:
        documents = employee.documents.all()
    else:
        documents = []
    
    # Можно ли уволить/восстановить
    can_fire = is_admin_or_accountant and employee.user != request.user

    return render(request, 'profile.html', {
        'form': form,
        'employee': employee,
        'educations': educations,
        'documents': documents,
        'can_edit': can_edit,
        'is_admin_or_accountant': is_admin_or_accountant,
        'viewing_own_profile': is_owner,
        'can_fire': can_fire
    })

@login_required
def employee_fire(request, employee_id):
    """Увольнение сотрудника (только admin/бухгалтер)"""
    # Проверка прав
    if not (request.user.is_superuser or request.user.groups.filter(name='Бухгалтер').exists()):
        messages.error(request, 'Недостаточно прав')
        return redirect('hr:index')
    
    employee = get_object_or_404(Employee, id=employee_id)
    
    # Нельзя уволить самого себя
    if employee.user == request.user:
        messages.error(request, 'Нельзя уволить самого себя')
        return redirect('hr:profile_view', employee_id=employee_id)
    
    if request.method == 'POST':
        # Деактивируем пользователя
        employee.user.is_active = False
        employee.user.set_password('Pass1234!!')
        employee.user.save()
        
        messages.success(request, f'Сотрудник {employee.get_full_name()} уволен. Пароль: Pass1234!!')
        return redirect('hr:profile_view', employee_id=employee_id)
    
    return redirect('hr:profile_view', employee_id=employee_id)

@login_required
def employee_restore(request, employee_id):
    """Восстановление сотрудника (только admin)"""
    # Проверка прав - только admin
    if not request.user.is_superuser:
        messages.error(request, 'Недостаточно прав (только администратор)')
        return redirect('hr:index')
    
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        # Активируем пользователя
        employee.user.is_active = True
        employee.user.set_password('Pass1234!')  # Стандартный пароль
        employee.user.save()
        
        messages.success(request, f'Сотрудник {employee.get_full_name()} восстановлен. Пароль: Pass1234!')
        return redirect('hr:profile_view', employee_id=employee.id)
    
    return redirect('hr:profile_view', employee_id=employee_id)

@login_required
def employee_create(request):
    """Создание нового сотрудника (только для admin/бухгалтера)"""
    # Проверка прав
    if not (request.user.is_superuser or request.user.groups.filter(name='Бухгалтер').exists()):
        messages.error(request, 'Недостаточно прав для создания сотрудников')
        return redirect('hr:work')

    if request.method == 'POST':
        form = EmployeeCreateForm(request.POST)
        if form.is_valid():
            # Генерируем следующий ID
            max_username = User.objects.filter(
                username__regex=r'^[0-9]{8}$'
            ).order_by('-username').first()
            
            if max_username:
                next_id = int(max_username.username) + 1
            else:
                next_id = 1
            
            new_username = f"{next_id:08d}"  # Формат 00000011
            
            # Создаём User
            user = User.objects.create_user(
                username=new_username,
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            
            # Добавляем в группу если бухгалтер
            if form.cleaned_data['role'] == 'Бухгалтер':
                accountant_group, _ = Group.objects.get_or_create(name='Бухгалтер')
                user.groups.add(accountant_group)
            
            # Если администратор - даём права
            if form.cleaned_data['role'] == 'Администратор':
                user.is_staff = True
                user.is_superuser = True
                user.save()
            
            # Создаём Employee
            employee = Employee.objects.create(
                user=user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                middle_name=form.cleaned_data['middle_name'],
                position=form.cleaned_data['position'],
                department=form.cleaned_data['department'],
                role=form.cleaned_data['role'],
                phone=form.cleaned_data['phone'],
                email=f"{new_username}@company.com",  # Автоматический email
                hire_date=form.cleaned_data['hire_date']  # Из формы
            )
            
            # Создаём историю должности
            PositionHistory.objects.create(
                employee=employee,
                position=employee.position,
                start_date=employee.hire_date
            )
            
            # Обновляем опыт
            employee.internal_experience = employee.get_work_experience()
            employee.save()
            
            messages.success(request, f'Сотрудник создан! Табельный номер: {new_username}')
            return redirect('hr:profile_view', employee_id=employee.id)
    else:
        form = EmployeeCreateForm()
    
    return render(request, 'employee_create.html', {'form': form})

@login_required
def education_add(request):
    """Добавление образования"""
    employee = getattr(request.user, 'employee_profile', None)
    if not employee:
        messages.error(request, 'Нет профиля')
        return redirect('hr:profile')

    if request.method == 'POST':
        form = EducationForm(request.POST, request.FILES)
        if form.is_valid():
            education = form.save(commit=False)
            education.employee = employee
            education.save()
            messages.success(request, 'Образование добавлено')
            return redirect('hr:profile')
    else:
        form = EducationForm()

    return render(request, 'education_form.html', {'form': form, 'title': 'Добавить образование'})

@login_required
def education_edit(request, education_id):
    """Редактирование образования"""
    education = get_object_or_404(Education, id=education_id)

    # Проверяем права
    can_edit = (
        request.user == education.employee.user or
        request.user.is_superuser or
        request.user.groups.filter(name='Бухгалтер').exists()
    )

    if not can_edit:
        messages.error(request, 'Недостаточно прав')
        return redirect('hr:profile')

    if request.method == 'POST':
        form = EducationForm(request.POST, request.FILES, instance=education)
        if form.is_valid():
            form.save()
            messages.success(request, 'Образование обновлено')
            return redirect('hr:profile')
    else:
        form = EducationForm(instance=education)

    return render(request, 'education_form.html', {'form': form, 'title': 'Редактировать образование'})

@login_required
def education_delete(request, education_id):
    """Удаление образования"""
    education = get_object_or_404(Education, id=education_id)

    # Проверяем права
    can_delete = (
        request.user == education.employee.user or
        request.user.is_superuser or
        request.user.groups.filter(name='Бухгалтер').exists()
    )

    if can_delete and request.method == 'POST':
        education.delete()
        messages.success(request, 'Образование удалено')
    else:
        messages.error(request, 'Недостаточно прав')

    return redirect('hr:profile')

@login_required
def document_add(request):
    """Добавление документа"""
    employee = getattr(request.user, 'employee_profile', None)
    if not employee:
        messages.error(request, 'Нет профиля')
        return redirect('hr:profile')

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.employee = employee
            document.save()
            messages.success(request, 'Документ добавлен')
            return redirect('hr:profile')
    else:
        form = DocumentForm()

    return render(request, 'document_form.html', {'form': form, 'title': 'Добавить документ'})

@login_required
def document_edit(request, document_id):
    """Редактирование документа"""
    document = get_object_or_404(Document, id=document_id)

    # Проверяем права
    can_edit = (
        request.user == document.employee.user or
        request.user.is_superuser or
        request.user.groups.filter(name='Бухгалтер').exists()
    )

    if not can_edit:
        messages.error(request, 'Недостаточно прав')
        return redirect('hr:profile')

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            messages.success(request, 'Документ обновлён')
            return redirect('hr:profile')
    else:
        form = DocumentForm(instance=document)

    return render(request, 'document_form.html', {'form': form, 'title': 'Редактировать документ', 'document': document})

@login_required
def document_delete(request, document_id):
    """Удаление документа"""
    document = get_object_or_404(Document, id=document_id)

    # Проверяем права
    can_delete = (
        request.user == document.employee.user or
        request.user.is_superuser or
        request.user.groups.filter(name='Бухгалтер').exists()
    )

    if can_delete and request.method == 'POST':
        document.delete()
        messages.success(request, 'Документ удалён')
    else:
        messages.error(request, 'Недостаточно прав')

    return redirect('hr:profile')

@login_required
def task_list(request):
    """Список задач с сортировкой: сначала новые/в работе, потом завершенные"""
    # Admin видит все задачи
    if request.user.is_superuser:
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(Q(assignee=request.user) | Q(creator=request.user)).distinct()

    # Сортировка: сначала new/in_progress, потом done
    tasks = tasks.annotate(
        status_order=Case(
            When(status='new', then=1),
            When(status='in_progress', then=2),
            When(status='done', then=3),
            default=4,
            output_field=IntegerField()
        )
    ).order_by('status_order', '-created_at')

    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def task_create(request):
    """Создание задачи"""
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.creator = request.user
            task.save()
            messages.success(request, 'Задача создана')
            return redirect('hr:tasks')
    else:
        form = TaskForm()

    return render(request, 'task_form.html', {'form': form, 'title': 'Создать задачу'})

@login_required
def task_update(request, task_id):
    """Обновление задачи"""
    task = get_object_or_404(Task, id=task_id)

    # Проверка прав
    if not (request.user.is_superuser or task.creator == request.user or task.assignee == request.user):
        messages.error(request, 'Недостаточно прав')
        return redirect('hr:tasks')

    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            task = form.save()

            # Если задача завершена и связана с заявкой - одобряем заявку
            if task.status == 'done':
                work_request = task.work_request.first()
                if work_request and not work_request.approved:
                    work_request.approved = True
                    work_request.save()
                    messages.success(request, f'Задача выполнена. Заявка "{work_request.get_request_type_display()}" одобрена.')
                else:
                    messages.success(request, 'Задача обновлена')
            else:
                messages.success(request, 'Задача обновлена')

            return redirect('hr:tasks')
    else:
        form = TaskForm(instance=task)

    return render(request, 'task_form.html', {'form': form, 'title': 'Редактировать задачу', 'task': task})

@login_required
def work(request):
    """Раздел работы с календарем трекера времени"""
    employee = getattr(request.user, 'employee_profile', None)
    today = date.today()
    
    # Получаем текущий месяц и год из GET или используем текущий
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    
    # Проверка прав для создания сотрудников
    can_create_employee = (
        request.user.is_superuser or 
        request.user.groups.filter(name='Бухгалтер').exists()
    )
    
    # Проверка прав для просмотра времени сотрудников
    can_view_employee_time = can_create_employee

    schedules = []
    requests_qs = []
    calendar_data = None
    
    if employee:
        schedules = employee.schedules.filter(date__month=month, date__year=year)
        requests_qs = employee.requests.all()
        
        # Создаём календарь
        cal = calendar.monthcalendar(year, month)
        
        # Получаем все записи времени за этот месяц
        time_entries = TimeEntry.objects.filter(
            employee=employee,
            start_time__year=year,
            start_time__month=month
        ).select_related('employee')
        
        # Группируем по датам
        entries_by_date = {}
        for entry in time_entries:
            day = entry.start_time.date().day
            if day not in entries_by_date:
                entries_by_date[day] = []
            entries_by_date[day].append(entry)
        
        # Формируем данные для календаря
        calendar_data = {
            'year': year,
            'month': month,
            'month_name': calendar.month_name[month],
            'month_name_rus': MONTH_NAMES_RU[month],
            'weeks': cal,
            'entries_by_date': entries_by_date,
            'today': today
        }
        
        # Навигация
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1
        
        calendar_data['prev_month'] = prev_month
        calendar_data['prev_year'] = prev_year
        calendar_data['next_month'] = next_month
        calendar_data['next_year'] = next_year

    return render(request, 'work.html', {
        'employee': employee,
        'schedules': schedules,
        'requests': requests_qs,
        'today': today,
        'can_create_employee': can_create_employee,
        'can_view_employee_time': can_view_employee_time,
        'calendar_data': calendar_data
    })

@login_required
def employee_time_api(request, employee_id):
    """API для получения календаря времени работы выбранного сотрудника"""
    # Проверка прав
    if not (request.user.is_superuser or request.user.groups.filter(name='Бухгалтер').exists()):
        return JsonResponse({'error': 'Недостаточно прав'}, status=403)
    
    employee = get_object_or_404(Employee, id=employee_id)
    today = date.today()
    
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    
    # Создаём календарь
    cal = calendar.monthcalendar(year, month)
    
    # Получаем все записи времени за месяц
    time_entries = TimeEntry.objects.filter(
        employee=employee,
        start_time__year=year,
        start_time__month=month
    ).select_related('employee')
    
    # Группируем по датам
    entries_by_date = {}
    total_seconds = 0
    working_days = set()
    
    for entry in time_entries:
        day = entry.start_time.date().day
        if day not in entries_by_date:
            entries_by_date[day] = []
        
        entry_data = {
            'start': entry.start_time.strftime('%H:%M'),
            'end': entry.end_time.strftime('%H:%M') if entry.end_time else None,
            'duration': entry.get_duration() if entry.end_time else None
        }
        entries_by_date[day].append(entry_data)
        working_days.add(day)
        
        # Считаем общее время
        if entry.end_time:
            delta = entry.end_time - entry.start_time
            total_seconds += delta.total_seconds()
    
    # Форматируем общее время
    total_hours = int(total_seconds // 3600)
    total_minutes = int((total_seconds % 3600) // 60)
    total_hours_formatted = f"{total_hours}ч {total_minutes}мин"
    
    return JsonResponse({
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'month_name_rus': MONTH_NAMES_RU[month],
        'weeks': cal,
        'entries_by_date': entries_by_date,
        'today': {'day': today.day, 'month': today.month, 'year': today.year},
        'total_sessions': len(time_entries),
        'total_hours': total_hours_formatted,
        'working_days': len(working_days)
    })

@login_required
def work_request_create(request):
    """Создание заявки - автоматически создаёт задачу для бухгалтера"""
    employee = getattr(request.user, 'employee_profile', None)
    if not employee:
        messages.error(request, 'Нет профиля')
        return redirect('hr:work')

    if request.method == 'POST':
        form = WorkRequestForm(request.POST)
        if form.is_valid():
            work_request = form.save(commit=False)
            work_request.employee = employee
            work_request.save()

            # Создаём задачу для бухгалтера
            accountant_group = Group.objects.get(name='Бухгалтер')
            accountant = accountant_group.user_set.first()

            if accountant:
                task = Task.objects.create(
                    title=f'Обработать заявку: {work_request.get_request_type_display()}',
                    description=f'От: {employee.get_full_name()}\nТип: {work_request.get_request_type_display()}\nОписание: {work_request.description}',
                    creator=request.user,
                    assignee=accountant,
                    status='new'
                )
                work_request.related_task = task
                work_request.save()

                messages.success(request, f'Заявка отправлена. Создана задача для бухгалтера.')
            else:
                messages.warning(request, 'Заявка создана, но бухгалтер не найден в системе')

            return redirect('hr:work')
    else:
        form = WorkRequestForm()

    return render(request, 'work_request_form.html', {'form': form})

@login_required
def time_start(request):
    """Запуск трекера времени"""
    employee = getattr(request.user, 'employee_profile', None)
    if not employee:
        messages.error(request, 'Нет профиля')
        return redirect('hr:index')

    active = employee.time_entries.filter(end_time__isnull=True).first()
    if active:
        messages.warning(request, 'Трекер уже запущен')
    else:
        TimeEntry.objects.create(employee=employee, start_time=timezone.now())
        messages.success(request, 'Трекер запущен')

    return redirect('hr:index')

@login_required
def time_stop(request):
    """Остановка трекера времени"""
    employee = getattr(request.user, 'employee_profile', None)
    if not employee:
        messages.error(request, 'Нет профиля')
        return redirect('hr:index')

    active = employee.time_entries.filter(end_time__isnull=True).first()
    if not active:
        messages.warning(request, 'Нет активного трекера')
    else:
        active.end_time = timezone.now()
        active.save()
        messages.success(request, f'Трекер остановлен. Отработано: {active.get_duration()}')

    return redirect('hr:index')

@login_required
def employee_search(request):
    """Поиск сотрудников по ФИО и табельному номеру (включая уволенных)"""
    query = request.GET.get('q', '').strip()

    if len(query) < 2:
        return JsonResponse({'results': []})

    # Поиск по табельному номеру (username) или ФИО
    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(employee_profile__middle_name__icontains=query)
    ).exclude(username='admin')[:10]

    results = []
    for user in users:
        employee = getattr(user, 'employee_profile', None)
        if employee:
            # Помечаем уволенных
            status = '' if user.is_active else ' (неактивен)'
            results.append({
                'id': employee.id,
                'username': user.username,
                'full_name': employee.get_full_name() + status,
                'position': employee.position
            })

    return JsonResponse({'results': results})
