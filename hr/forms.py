from django import forms
from .models import Employee, Task, WorkRequest, Education
from django.contrib.auth.models import User

class EmployeeRestrictedForm(forms.ModelForm):
    """Ограниченная форма профиля для обычных сотрудников"""
    class Meta:
        model = Employee
        fields = ['middle_name', 'phone', 'avatar', 'annual_goal', 
                  'internal_experience', 'external_experience', 'status']
        labels = {
            'middle_name': 'Отчество',
            'phone': 'Телефон',
            'avatar': 'Аватар',
            'annual_goal': 'Цели на год',
            'internal_experience': 'Опыт внутри компании',
            'external_experience': 'Опыт вне компании',
            'status': 'Статус'
        }
        widgets = {
            'middle_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванович', 'readonly': 'readonly'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7-900-123-45-67'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'annual_goal': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'internal_experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'external_experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'})
        }

class EmployeeFullForm(forms.ModelForm):
    """Полная форма профиля для админов и бухгалтеров (включая ФИО, роль, должность, отдел)"""
    first_name = forms.CharField(
        max_length=150,
        required=False,
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иван'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Петров'})
    )
    
    class Meta:
        model = Employee
        fields = ['middle_name', 'phone', 'avatar', 'role', 'position', 'department', 
                  'annual_goal', 'internal_experience', 'external_experience', 'status']
        labels = {
            'middle_name': 'Отчество',
            'phone': 'Телефон',
            'avatar': 'Аватар',
            'role': 'Роль',
            'position': 'Должность',
            'department': 'Отдел',
            'annual_goal': 'Цели на год',
            'internal_experience': 'Опыт внутри компании',
            'external_experience': 'Опыт вне компании',
            'status': 'Статус'
        }
        widgets = {
            'middle_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванович'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7-900-123-45-67'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'role': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'annual_goal': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'internal_experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'external_experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Предзаполнение полей ФИО из связанного User
        if self.instance and self.instance.pk:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
    
    def save(self, commit=True):
        employee = super().save(commit=False)
        # Сохранение ФИО в модель User
        if self.cleaned_data.get('first_name') is not None:
            employee.user.first_name = self.cleaned_data['first_name']
        if self.cleaned_data.get('last_name') is not None:
            employee.user.last_name = self.cleaned_data['last_name']
        if commit:
            employee.user.save()
            employee.save()
        return employee

# Для обратной совместимости - базовая форма
class EmployeeForm(forms.ModelForm):
    """Базовая форма профиля сотрудника (используется как fallback)"""
    class Meta:
        model = Employee
        fields = ['middle_name', 'phone', 'avatar', 'role', 'position', 'department', 
                  'annual_goal', 'internal_experience', 'external_experience', 'status']
        labels = {
            'middle_name': 'Отчество',
            'phone': 'Телефон',
            'avatar': 'Аватар',
            'role': 'Роль',
            'position': 'Должность',
            'department': 'Отдел',
            'annual_goal': 'Цели на год',
            'internal_experience': 'Опыт внутри компании',
            'external_experience': 'Опыт вне компании',
            'status': 'Статус'
        }
        widgets = {
            'middle_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванович'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7-900-123-45-67'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'role': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'annual_goal': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'internal_experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'external_experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'})
        }

class EducationForm(forms.ModelForm):
    """Форма образования с возможностью прикрепления файлов"""
    class Meta:
        model = Education
        fields = ['institution', 'degree', 'field_of_study', 'start_year', 'end_year', 'description', 'diploma_file']
        labels = {
            'institution': 'Учебное заведение',
            'degree': 'Степень/Квалификация',
            'field_of_study': 'Специальность',
            'start_year': 'Год начала',
            'end_year': 'Год окончания',
            'description': 'Описание',
            'diploma_file': 'Диплом/Сертификат'
        }
        widgets = {
            'institution': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'МГУ им. Ломоносова'}),
            'degree': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Бакалавр'}),
            'field_of_study': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Информатика'}),
            'start_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2018'}),
            'end_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2022'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Дополнительная информация...'}),
            'diploma_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx'})
        }

class TaskForm(forms.ModelForm):
    """Форма задачи с возможностью прикрепления файлов"""
    class Meta:
        model = Task
        fields = ['title', 'description', 'assignee', 'status', 'due_date', 'attachment']
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'assignee': 'Исполнитель',
            'status': 'Статус',
            'due_date': 'Срок выполнения',
            'attachment': 'Вложение'
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название задачи'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Подробное описание...'}),
            'assignee': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assignee'].queryset = User.objects.filter(is_active=True)
        self.fields['assignee'].label_from_instance = lambda obj: f"{obj.get_full_name() or obj.username} ({obj.username})"

class WorkRequestForm(forms.ModelForm):
    """Форма заявки на отпуск/справку"""
    class Meta:
        model = WorkRequest
        fields = ['request_type', 'description']
        labels = {
            'request_type': 'Тип заявки',
            'description': 'Описание'
        }
        widgets = {
            'request_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Подробности заявки...'})
        }
