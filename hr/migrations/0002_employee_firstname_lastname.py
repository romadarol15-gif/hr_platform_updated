# Generated migration
from django.db import migrations, models

def copy_names_from_user(apps, schema_editor):
    """Копируем ФИО из User модели в Employee"""
    Employee = apps.get_model('hr', 'Employee')
    for employee in Employee.objects.all():
        if hasattr(employee, 'user'):
            employee.first_name = employee.user.first_name
            employee.last_name = employee.user.last_name
            employee.save(update_fields=['first_name', 'last_name'])

class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='Имя'),
        ),
        migrations.AddField(
            model_name='employee',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='Фамилия'),
        ),
        # Копируем данные из User в Employee
        migrations.RunPython(copy_names_from_user, migrations.RunPython.noop),
    ]
