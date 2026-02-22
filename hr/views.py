from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q, Case, When, IntegerField
from .forms import EmployeeRestrictedForm, EmployeeFullForm, TaskForm, WorkRequestForm, EducationForm
from .models import Employee, Task, WorkRequest, TimeEntry, Education
from datetime import date

def user_login(request):
    """Вход в систему"""
    if request.user.is_authenticated:
        return redirect('hr:index')
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
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
        # Любой авторизованный пользователь может просматривать профили
        employee = get_object_or_404(Employee, id=employee_id)
        # Редактировать может только владелец, бухгалтер или админ
        can_edit = (
            request.user == employee.user or
            is_admin_or_accountant
        )
    else:
        # Свой профиль
        employee, _ = Employee.objects.get_or_create(
            user=request.user,
            defaults={'role': 'Сотрудник', 'position': 'Специалист'}
        )
        can_edit = True

    # Определяем какую форму использовать
    # Админы/бухгалтеры могут редактировать всё
    if can_edit and is_admin_or_accountant:
        FormClass = EmployeeFullForm
    else:
        # Обычные сотрудники видят форму с readonly полями
        FormClass = EmployeeRestrictedForm

    if request.method == 'POST':
        if can_edit:
            form = FormClass(request.POST, request.FILES, instance=employee)
            if form.is_valid():
                form.save()
                messages.success(request, 'Профиль обновлён')
                # Исправленный редирект
                if employee_id:
                    return redirect('hr:profile_view', employee_id=employee.id)
                else:
                    return redirect('hr:profile')
        else:
            messages.error(request, 'Недостаточно прав для редактирования')
    else:
        form = FormClass(instance=employee)

    # Образование
    educations = employee.educations.all()

    return render(request, 'profile.html', {
        'form': form,
        'employee': employee,
        'educations': educations,
        'can_edit': can_edit,
        'is_admin_or_accountant': is_admin_or_accountant,
        'viewing_own_profile': employee.user == request.user
    })

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
def task_list(request):
    """Список задач с сортировкой: сначала новые/в работе, потом завершенные"""
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
                # Получаем связанную заявку (если есть)
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

    return render(request, 'task_form.html', {'form': form, 'title': 'Редактировать задачу'})

@login_required
def work(request):
    """Раздел работы"""
    employee = getattr(request.user, 'employee_profile', None)
    today = date.today()
    schedules = []
    requests_qs = []

    if employee:
        schedules = employee.schedules.filter(date__month=today.month)
        requests_qs = employee.requests.all()

    return render(request, 'work.html', {
        'employee': employee,
        'schedules': schedules,
        'requests': requests_qs,
        'today': today
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
    """Поиск сотрудников по ФИО и табельному номеру"""
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
            results.append({
                'id': employee.id,
                'username': user.username,
                'full_name': employee.get_full_name(),
                'position': employee.position
            })

    return JsonResponse({'results': results})
