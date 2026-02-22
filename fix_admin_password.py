import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_platform.settings')
django.setup()

from django.contrib.auth.models import User

print("Исправление пароля для admin...\n")

try:
    admin = User.objects.get(username='admin')
    admin.set_password('Pass1234!')
    admin.save()
    print("✅ Пароль для admin успешно изменён на: Pass1234!")
    print("\nТеперь вы можете войти:")
    print("  - Логин: admin")
    print("  - Пароль: Pass1234!")
except User.DoesNotExist:
    print("❌ Пользователь admin не найден!")
    print("Запустите: python create_test_users.py")
