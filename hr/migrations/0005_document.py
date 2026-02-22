# Generated migration

from django.db import migrations, models
import django.db.models.deletion
import hr.models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0004_employee_email_hire_date_positionhistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('comment', models.TextField(blank=True, verbose_name='Комментарий')),
                ('file', models.FileField(upload_to='employee_documents/', validators=[hr.models.validate_file_size], verbose_name='Файл')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='hr.employee', verbose_name='Сотрудник')),
            ],
            options={
                'verbose_name': 'Документ',
                'verbose_name_plural': 'Документы',
                'ordering': ['-uploaded_at'],
            },
        ),
    ]
