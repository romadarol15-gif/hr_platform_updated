from django.urls import path
from . import views

app_name = 'hr'

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path('profile/<int:employee_id>/', views.profile, name='profile_view'),

    # Образование
    path('education/add/', views.education_add, name='education_add'),
    path('education/<int:education_id>/edit/', views.education_edit, name='education_edit'),
    path('education/<int:education_id>/delete/', views.education_delete, name='education_delete'),

    # Документы
    path('document/add/', views.document_add, name='document_add'),
    path('document/<int:document_id>/edit/', views.document_edit, name='document_edit'),
    path('document/<int:document_id>/delete/', views.document_delete, name='document_delete'),

    # Задачи
    path('tasks/', views.task_list, name='tasks'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:task_id>/update/', views.task_update, name='task_update'),

    # Работа
    path('work/', views.work, name='work'),
    path('work/request/', views.work_request_create, name='work_request_create'),

    # Сотрудники
    path('employee/create/', views.employee_create, name='employee_create'),
    path('employee/fire/<int:employee_id>/', views.employee_fire, name='employee_fire'),
    path('employee/restore/<int:employee_id>/', views.employee_restore, name='employee_restore'),

    # Трекер времени
    path('time/start/', views.time_start, name='time_start'),
    path('time/stop/', views.time_stop, name='time_stop'),

    # API просмотра времени сотрудника
    path('employee-time/<int:employee_id>/', views.employee_time_api, name='employee_time_api'),

    # Поиск
    path('employee-search/', views.employee_search, name='employee_search'),

    # Авторизация
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]
