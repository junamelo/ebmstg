#!/usr/bin/env python
"""Script pour créer un compte chef de facturation"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()

from accounts.models import User

# Créer chef de facturation
chef, created = User.objects.get_or_create(
    username='chef@moov.tg',
    defaults={
        'email': 'chef@moov.tg',
        'first_name': 'Chef',
        'last_name': 'Facturation',
        'role': 'CHEF_FACTURATION',
        'is_active': True,
        'is_staff': False
    }
)

if created:
    chef.set_password('chef123')
    chef.save()
    print(f'✓ Chef de facturation créé: chef@moov.tg / chef123')
else:
    print(f'✓ Chef de facturation existe déjà: chef@moov.tg')
