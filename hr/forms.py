from django import forms
from .models import Employee, Task, WorkRequest, Education
from django.contrib.auth.models import User

class EmployeeRestrictedForm(forms.ModelForm):
    """Ограниченная форма профиля для обычных сотрудников"""
    class Meta:
        model = Employee
        fields = ['last_name', 'first_name', 'middle_name', 'email', 'phone', 'avatar', 'role', 'position', 'department', 
                  'hire_date', 'annual_goal', 'external_experience', 'status']
        labels = {
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'middle_name': 'Отчество',
            'email': 'Email',
            'phone': 'Телефон',
            'avatar': 'Аватар',
            'role': 'Роль',
            'position': 'Должность',
            'department': 'Отдел',
            'hire_date': 'Дата приёма на работу',
            'annual_goal': 'Цели на год',
            'external_experience': 'Опыт вне компании',
            'status': 'Статус'
        }
        widgets = {
            'last_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'readonly': 'readonly',
                'style': 'background-color: #e9ecef;'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'readonly': 'readonly',
                'style': 'background-color: #e9ecef;'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'readonly': 'readonly',
                'style': 'background-color: #e9ecef;'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',
                'style': 'background-color: #e9ecef;'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',
                'style': 'background-color: #e9ecef;',
                'placeholder': '+7-900-123-45-67'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'disabled': 'disabled'
            }),
            'role': forms.Select(
                choices=[
                    ('Сотрудник', 'Сотрудник'),
                    ('Бухгалтер', 'Бухгалтер'),
                    ('Администратор', 'Администратор')
                ],
                attrs={
                    'class': 'form-control',
                    'disabled': 'disabled',
                    'style': 'background-color: #e9ecef;'
                }
            ),
            'position': forms.TextInput(attrs={
                'class': 'form-control', 
                'readonly': 'readonly',
                'style': 'background-color: #e9ecef;'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control', 
                'readonly': 'readonly',
                'style': 'background-color: #e9ecef;'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'readonly': 'readonly',
                'style': 'background-color: #e9ecef;'
            }),
            'annual_goal': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'external_experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={
                'class': 'form-control',
                'disabled': 'disabled',
                'style': 'background-color: #e9ecef;'
            })
        }

class EmployeeFullForm(forms.ModelForm):
    """Полная форма профиля для админов и бухгалтеров"""
    class Meta:
        model = Employee
        fields = ['last_name', 'first_name', 'middle_name', 'email', 'phone', 'avatar', 'role', 'position', 'department', 
                  'hire_date', 'annual_goal', 'external_experience', 'status']
        labels = {
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'middle_name': 'Отчество',
            'email': 'Email',
            'phone': 'Телефон',
            'avatar': 'Аватар',
            'role': 'Роль',
            'position': 'Должность',
            'department': 'Отдел',
            'hire_date': 'Дата приёма на работу',
            'annual_goal': 'Цели на год',
            'external_experience': 'Опыт вне компании',
            'status': 'Статус'
        }
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Петров'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иван'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванович'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '00000001@company.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7-900-123-45-67'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'role': forms.Select(
                choices=[
                    ('Сотрудник', 'Сотрудник'),
                    ('Бухгалтер', 'Бухгалтер'),
                    ('Администратор', 'Администратор')
                ],
                attrs={'class': 'form-control'}
            ),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'annual_goal': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'external_experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'})
        }

class EmployeeCreateForm(forms.Form):
    """Форма создания нового сотрудника"""
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Pass1234!'}),
        min_length=6
    )
    
    last_name = forms.CharField(
        label='Фамилия',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Петров'})
    )
    first_name = forms.CharField(
        label='Имя',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иван'})
    )
    middle_name = forms.CharField(
        label='Отчество',
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванович'})
    )
    position = forms.CharField(
        label='Должность',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Разработчик'})
    )
    department = forms.CharField(
        label='Отдел',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IT'})
    )
    role = forms.ChoiceField(
        label='Роль',
        choices=[
            ('Сотрудник', 'Сотрудник'),
            ('Бухгалтер', 'Бухгалтер'),
            ('Администратор', 'Администратор')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        label='Телефон',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7-900-123-45-67'})
    )
    hire_date = forms.DateField(
        label='Дата приёма на работу',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

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
