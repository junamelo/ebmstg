import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()

from accounts.models import User

# Créer le superuser
if not User.objects.filter(email='admin@moov.tg').exists():
    User.objects.create_superuser(
        email='admin@moov.tg',
        username='admin',
        password='admin123',
        first_name='Admin',
        last_name='Moov',
        role='SUPER_ADMIN',
        telephone='90000000'
    )
    print("Superuser créé avec succès!")
    print("Email: admin@moov.tg")
    print("Password: admin123")
else:
    print("Le superuser existe déjà")
