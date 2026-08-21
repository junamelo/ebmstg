"""Paramètres isolés pour les tests automatisés du projet."""

from .settings import *  # noqa: F403


# Les tests ne touchent jamais la base PostgreSQL de développement.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
