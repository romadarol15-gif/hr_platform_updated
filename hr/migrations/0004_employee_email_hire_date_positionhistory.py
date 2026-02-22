from django.db import migrations, models
import django.db.models.deletion
from datetime import date, timedelta
import random

def create_position_history(apps, schema_editor):
    """Создаём начальную историю для всех сотрудников"""
    Employee = apps.get_model('hr', 'Employee')
    PositionHistory = apps.get_model('hr', 'PositionHistory')
    
    for employee in Employee.objects.all():
        if employee.hire_date and employee.position:
            PositionHistory.objects.create(
                employee=employee,
                position=employee.position,
                start_date=employee.hire_date,
                end_date=None
            )

class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0003_merge_20260222_1234'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='email',
            field=models.EmailField(blank=True, max_length=200, verbose_name='Email'),
        ),
        migrations.AddField(
            model_name='employee',
            name='hire_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата приёма на работу'),
        ),
        migrations.CreateModel(
            name='PositionHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(max_length=100, verbose_name='Должность')),
                ('start_date', models.DateField(verbose_name='Дата начала')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='Дата окончания')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='position_history', to='hr.employee', verbose_name='Сотрудник')),
            ],
            options={
                'verbose_name': 'История должности',
                'verbose_name_plural': 'История должностей',
                'ordering': ['-start_date'],
            },
        ),
        migrations.RunPython(create_position_history),
    ]
