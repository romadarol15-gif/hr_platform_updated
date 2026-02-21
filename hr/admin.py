from django.contrib import admin
from .models import Employee, Task, WorkSchedule, WorkRequest, TimeEntry, Education

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_full_name', 'position', 'department', 'status')
    list_filter = ('status', 'department')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'middle_name')

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'institution', 'degree', 'start_year', 'end_year')
    list_filter = ('degree',)
    search_fields = ('employee__user__username', 'institution', 'field_of_study')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'assignee', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'description')

@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'start_time', 'end_time')
    list_filter = ('date',)

@admin.register(WorkRequest)
class WorkRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'request_type', 'created_at', 'approved', 'related_task')
    list_filter = ('request_type', 'approved')
    search_fields = ('employee__user__username', 'description')

@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'start_time', 'end_time', 'get_duration')
    list_filter = ('start_time',)
