# 📍 OÙ TROUVER TOUS LES FICHIERS IMPORTANTS

## 📂 STRUCTURE DU PROJET BACKEND

```
Back/
├── 📄 manage.py                    # Commandes Django
├── 📄 db.sqlite3                   # Base de données SQLite (créée automatiquement)
├── 📄 .env                         # ❌ N'EXISTE PAS ENCORE (à créer)
├── 📄 requirements.txt             # ❌ À créer pour les dépendances
│
├── 📁 moov_backend/                # Configuration du projet
│   ├── 📄 settings.py              # ⭐ CONFIGURATION (DB, CORS, etc.)
│   ├── 📄 urls.py                  # Routes principales
│   ├── 📄 wsgi.py
│   └── 📄 asgi.py
│
├── 📁 accounts/                    # App Utilisateurs
│   ├── 📄 models.py                # ⭐ MODÈLE USER
│   ├── 📄 views.py                 # Endpoints auth
│   ├── 📄 serializers.py
│   ├── 📄 urls.py
│   └── 📁 migrations/
│
└── 📁 billing/                     # App Facturation
    ├── 📄 models.py                # ⭐⭐⭐ TOUS LES 10 MODÈLES ICI
    ├── 📄 views.py                 # Tous les endpoints
    ├── 📄 serializers.py           # Tous les serializers
    ├── 📄 urls.py                  # Routes API
    └── 📁 migrations/              # Migrations de la DB
        ├── 0001_initial.py
        ├── 0002_alter_line_cycle.py
        └── 0003_package_service_invoice_historiquefacturation_and_more.py
```

---

## ⭐ FICHIER PRINCIPAL : `billing/models.py`

**📍 Chemin complet :**
```
c:\Users\Benoit\Documents\BURRO\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026\Back\billing\models.py
```

**Ce fichier contient :**
1. ✅ Company (existant)
2. ✅ Line (existant)
3. ✅ Package (nouveau)
4. ✅ Service (nouveau)
5. ✅ TarifService (nouveau)
6. ✅ Invoice (nouveau)
7. ✅ HistoriqueFacturation (nouveau)
8. ✅ Cycle (nouveau)
9. ✅ Simulation (nouveau)
10. ✅ Publication (nouveau)

**Pour l'ouvrir :**
- Dans VS Code : `Ctrl+P` → `billing/models.py`
- Ou naviguer vers le dossier `Back/billing/`

---

## 🗄️ BASE DE DONNÉES ACTUELLE

### SQLite (par défaut)

**📍 Fichier :**
```
c:\Users\Benoit\Documents\BURRO\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026\Back\db.sqlite3
```

**Configuration dans :** `moov_backend/settings.py`
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Avantages SQLite :**
- ✅ Aucune installation requise
- ✅ Parfait pour développement
- ✅ Fichier unique, facile à sauvegarder

**Inconvénients SQLite :**
- ❌ Ne supporte pas bien la concurrence
- ❌ Limité pour la production
- ❌ Pas de features avancées

---

## 🐘 CHANGER POUR POSTGRESQL (RECOMMANDÉ)

### Option 1 : PostgreSQL Local

#### 1. Installer PostgreSQL
**Télécharger :** https://www.postgresql.org/download/windows/

Pendant l'installation :
- Port : 5432
- Mot de passe : choisir un mot de passe (ex: `postgres123`)

#### 2. Créer la base de données
```bash
# Ouvrir PowerShell
psql -U postgres

# Dans psql :
CREATE DATABASE moov_africa;
CREATE USER moov_user WITH PASSWORD 'motdepasse123';
GRANT ALL PRIVILEGES ON DATABASE moov_africa TO moov_user;
\q
```

#### 3. Installer psycopg2
```bash
cd Back
pip install psycopg2-binary
```

#### 4. Créer le fichier `.env`

**📍 Créer :** `Back/.env`

```env
# Base de données PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=moov_africa
DB_USER=moov_user
DB_PASSWORD=motdepasse123
DB_HOST=localhost
DB_PORT=5432

# Secret Key Django
SECRET_KEY=django-insecure-ujjg22q3bi*6m0ksj2-@q!l#l$_lcmjuo7b^!iq+#^uk#5xqtq

# Debug
DEBUG=True
```

#### 5. Installer python-decouple
```bash
pip install python-decouple
```

#### 6. Modifier `settings.py`

**📍 Fichier :** `moov_backend/settings.py`

**Remplacer :**
```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-ujjg22q3bi*6m0ksj2-@q!l#l$_lcmjuo7b^!iq+#^uk#5xqtq'

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Par :**
```python
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-ujjg22q3bi*6m0ksj2-@q!l#l$_lcmjuo7b^!iq+#^uk#5xqtq')

DEBUG = config('DEBUG', default=True, cast=bool)

DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=BASE_DIR / 'db.sqlite3'),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
    }
}
```

#### 7. Appliquer les migrations
```bash
cd Back
python manage.py migrate
```

---

### Option 2 : PostgreSQL Cloud (GRATUIT)

#### 1. Créer un compte sur ElephantSQL (gratuit)
**URL :** https://www.elephantsql.com/

1. S'inscrire gratuitement
2. Créer une nouvelle instance (plan Tiny Turtle - gratuit)
3. Copier l'URL de connexion

Exemple d'URL :
```
postgres://username:password@host.db.elephantsql.com/database
```

#### 2. Créer le fichier `.env`

**📍 Créer :** `Back/.env`

```env
# URL complète PostgreSQL
DATABASE_URL=postgres://username:password@host.db.elephantsql.com/database

# Secret Key Django
SECRET_KEY=django-insecure-ujjg22q3bi*6m0ksj2-@q!l#l$_lcmjuo7b^!iq+#^uk#5xqtq

# Debug
DEBUG=True
```

#### 3. Installer les dépendances
```bash
cd Back
pip install psycopg2-binary dj-database-url python-decouple
```

#### 4. Modifier `settings.py`

**Ajouter en haut :**
```python
from pathlib import Path
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', cast=bool)

# Database avec dj-database-url
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600
    )
}
```

#### 5. Appliquer les migrations
```bash
python manage.py migrate
```

---

## 🐬 MYSQL / MARIADB (Alternative)

### 1. Installer MySQL
**Télécharger :** https://dev.mysql.com/downloads/mysql/

### 2. Créer la base de données
```sql
CREATE DATABASE moov_africa CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'moov_user'@'localhost' IDENTIFIED BY 'motdepasse123';
GRANT ALL PRIVILEGES ON moov_africa.* TO 'moov_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Installer mysqlclient
```bash
pip install mysqlclient
```

### 4. Fichier `.env`
```env
DB_ENGINE=django.db.backends.mysql
DB_NAME=moov_africa
DB_USER=moov_user
DB_PASSWORD=motdepasse123
DB_HOST=localhost
DB_PORT=3306
```

---

## 📄 CRÉER `requirements.txt`

**📍 Créer :** `Back/requirements.txt`

```txt
Django==6.0.3
djangorestframework==3.15.1
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.1
drf-spectacular==0.27.1
python-decouple==3.8
psycopg2-binary==2.9.9
dj-database-url==2.1.0
Pillow==10.2.0
```

**Pour installer :**
```bash
pip install -r requirements.txt
```

---

## 🔒 SÉCURITÉ : `.gitignore`

**📍 Créer/Modifier :** `Back/.gitignore`

```gitignore
# Environment variables
.env
.env.local

# Database
*.sqlite3
../Back/db.sqlite3

# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# Django
*.log
local_settings.py

# Media files
media/

# Static files
staticfiles/
static_root/

# IDE
.vscode/
.idea/
*.swp
*.swo
```

---

## 📋 RÉSUMÉ DES CHEMINS IMPORTANTS

| Fichier | Chemin | Contenu |
|---------|--------|---------|
| **Tous les modèles** | `Back/billing/models.py` | 10 modèles Django |
| **Configuration** | `Back/moov_backend/settings.py` | DB, CORS, JWT |
| **Base de données SQLite** | `Back/db.sqlite3` | Fichier DB actuel |
| **Variables d'environnement** | `Back/.env` | À créer |
| **Dépendances** | `Back/requirements.txt` | À créer |
| **Migrations** | `Back/billing/migrations/` | Historique DB |
| **User model** | `Back/accounts/models.py` | Modèle User |

---

## 🚀 COMMANDES UTILES

### Voir les modèles
```bash
cd Back
python manage.py showmigrations
```

### Créer une migration
```bash
python manage.py makemigrations
```

### Appliquer les migrations
```bash
python manage.py migrate
```

### Voir la structure de la DB
```bash
python manage.py sqlmigrate billing 0003
```

### Créer un superuser
```bash
python manage.py createsuperuser
```

### Shell Django (tester les modèles)
```bash
python manage.py shell

# Dans le shell :
from billing.models import Package, Service
Package.objects.all()
Service.objects.create(nom="Test", code="TEST", type_service="PASS")
```

---

## 🎯 MA RECOMMANDATION

### Pour développement (maintenant) :
✅ **Garder SQLite** - Simple, rapide, aucune config

### Pour production (plus tard) :
✅ **PostgreSQL Cloud (ElephantSQL)** - Gratuit, fiable, facile

### Migration SQLite → PostgreSQL :
```bash
# 1. Exporter les données
python manage.py dumpdata > data.json

# 2. Changer la config vers PostgreSQL

# 3. Appliquer les migrations
python manage.py migrate

# 4. Importer les données
python manage.py loaddata data.json
```

---

**Tu veux que je t'aide à configurer PostgreSQL ou tu préfères rester sur SQLite pour l'instant ?**
