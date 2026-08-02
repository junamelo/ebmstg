# 🚀 Backend Moov e-Billings

Backend complet pour le portail de facturation Moov Africa Togo.

## 📊 Vue d'Ensemble

**Framework** : Django 6.0.3 + Django REST Framework  
**Base de données** : SQLite (dev) / PostgreSQL (prod recommandé)  
**Authentification** : JWT (Simple JWT)  
**Statut** : ✅ **Production-Ready**

### Statistiques

- **71 Endpoints** REST
- **63 Tests** automatisés
- **12 Modèles** de données
- **19 Permissions** personnalisées
- **4 Phases** complètes

---

## 🏗️ Architecture - 4 Phases

| Phase | Module | Endpoints | Tests | Doc |
|-------|--------|-----------|-------|-----|
| **1** | Authentification & Utilisateurs | 14 | 20 | [PHASE1_README.md](PHASE1_README.md) |
| **2** | Contrats & Lignes | 17 | 13 | [PHASE2_README.md](PHASE2_README.md) |
| **3** | Tarification & Services | 19 | 10 | [PHASE3_README.md](PHASE3_README.md) |
| **4** | Facturation Complète | 21 | 20 | [PHASE4_README.md](PHASE4_README.md) |

---

## ⚡ Démarrage Rapide

### Prérequis

- Python 3.10+
- pip

### Installation

```bash
# Installer les dépendances
pip install django djangorestframework djangorestframework-simplejwt
pip install django-cors-headers drf-spectacular django-filter

# Appliquer les migrations
python manage.py migrate

# Créer un superuser
python manage.py createsuperuser
```

### Lancement

```bash
# Démarrer le serveur de développement
python manage.py runserver

# API disponible sur
http://localhost:8000/api/

# Documentation interactive
http://localhost:8000/api/docs/       # Swagger UI
http://localhost:8000/api/redoc/      # ReDoc
```

---

## 🧪 Tests

### Lancer tous les tests

```bash
# Option 1 : Commande Django
python manage.py test

# Option 2 : Script interactif
python run_all_tests.py
```

### Tests par phase

```bash
# Phase 1 : Authentification
python manage.py test accounts

# Phases 2, 3, 4 : Billing
python manage.py test billing

# Suite spécifique
python manage.py test billing.tests.InvoiceTests
```

### Résultat attendu

```
Ran 63 tests in X.XXXs

OK
```

---

## 📡 API Endpoints

### Authentification

```bash
POST /api/auth/login/              # Connexion JWT
POST /api/auth/logout/             # Déconnexion
POST /api/auth/refresh/            # Refresh token
GET  /api/auth/profile/            # Mon profil
POST /api/auth/change-password/    # Changer MDP
```

### Gestion Utilisateurs

```bash
GET    /api/auth/users/            # Liste utilisateurs
POST   /api/auth/users/            # Créer utilisateur
GET    /api/auth/users/{id}/       # Détail utilisateur
PUT    /api/auth/users/{id}/       # Modifier
DELETE /api/auth/users/{id}/       # Supprimer
```

### Contrats & Lignes

```bash
GET  /api/billing/companies/       # Liste contrats
POST /api/billing/companies/       # Créer contrat
GET  /api/billing/lines/           # Liste lignes
POST /api/billing/lines/           # Créer ligne
```

### Tarification

```bash
GET  /api/billing/packages/        # Liste forfaits
POST /api/billing/packages/        # Créer forfait
GET  /api/billing/services/        # Liste services
POST /api/billing/services/        # Créer service
```

### Facturation

```bash
POST /api/billing/invoices/generate/         # Générer factures
POST /api/billing/invoices/calculate_line/   # Calculer ligne
POST /api/billing/invoices/{id}/valider/     # Valider
POST /api/billing/publications/{id}/publish/ # Publier masse
```

**Voir documentation complète** : http://localhost:8000/api/docs/

---

## 🔐 Authentification

### Obtenir un token

```bash
POST http://localhost:8000/api/auth/login/
Content-Type: application/json

{
  "email": "agent@moov.tg",
  "password": "agent123"
}
```

**Réponse** :
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 3,
    "email": "agent@moov.tg",
    "role": "AGENT_FACTURATION",
    ...
  }
}
```

### Utiliser le token

```bash
GET http://localhost:8000/api/billing/companies/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## 👥 Comptes de Test

| Rôle | Email | Password | Accès |
|------|-------|----------|-------|
| **Super Admin** | admin@moov.tg | admin123 | Tout |
| **Chef Facturation** | chef@moov.tg | chef123 | Gestion complète |
| **Agent Facturation** | agent@moov.tg | agent123 | Opérations courantes |
| **Payeur** | payeur@moov.tg | payeur123 | Ses factures |
| **Employé** | employe@moov.tg | employe123 | Sa ligne |

---

## 📚 Documentation

### Guides par Phase

- **[PHASE1_README.md](PHASE1_README.md)** - Authentification & Utilisateurs
- **[PHASE2_README.md](PHASE2_README.md)** - Contrats & Lignes
- **[PHASE3_README.md](PHASE3_README.md)** - Tarification & Services
- **[PHASE4_README.md](PHASE4_README.md)** - Facturation Complète

### Documentation Récapitulative

- **[BACKEND_COMPLET.md](BACKEND_COMPLET.md)** - Vue d'ensemble complète
- **[BACKEND_FINAL_COMPLET.md](BACKEND_FINAL_COMPLET.md)** - Récap final avec métriques

### Documentation Technique

- **[GESTION_UTILISATEURS_API.md](GESTION_UTILISATEURS_API.md)** - API Utilisateurs
- **[INSTRUCTIONS_MIGRATION.md](INSTRUCTIONS_MIGRATION.md)** - Guide migrations

---

## 🔧 Configuration

### Base de données

**Développement** : SQLite (par défaut)

**Production** : PostgreSQL recommandé

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'moov_ebillings',
        'USER': 'moov_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### CORS

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Frontend React
]
```

### JWT

```python
# settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

---

## 🗂️ Structure du Projet

```
Back/
├── accounts/                   # Phase 1 : Auth & Users
│   ├── models.py              # User, StatusHistory
│   ├── serializers.py         # 8 serializers
│   ├── views.py               # Auth + UserManagement
│   ├── permissions.py         # 19 permissions
│   ├── middleware.py          # Audit + Status check
│   └── tests.py               # 20 tests
│
├── billing/                    # Phases 2, 3, 4
│   ├── models.py              # Company, Line, Package, Service, Invoice, etc.
│   ├── serializers.py         # 39 serializers
│   ├── views.py               # 11 ViewSets
│   ├── services/
│   │   └── calcul_tarification.py  # Service calcul tarifs
│   └── tests.py               # 43 tests
│
├── moov_backend/
│   ├── settings.py            # Configuration Django
│   ├── urls.py                # Routes principales
│   └── wsgi.py
│
├── logs/
│   ├── app.log                # Logs généraux
│   └── security.log           # Logs sécurité
│
├── media/
│   └── factures/              # PDF factures
│
├── manage.py
├── db.sqlite3
├── run_all_tests.py           # Script tests
└── README.md                  # Ce fichier
```

---

## 🚀 Déploiement Production

### Checklist

- [ ] Changer `DEBUG = False`
- [ ] Configurer `ALLOWED_HOSTS`
- [ ] Utiliser PostgreSQL
- [ ] Configurer variables d'environnement
- [ ] Configurer serveur web (Nginx + Gunicorn)
- [ ] Activer HTTPS
- [ ] Configurer logs externes
- [ ] Sauvegardes automatiques DB
- [ ] Monitoring (Sentry)
- [ ] Rate limiting
- [ ] CDN pour media files

### Variables d'Environnement

```bash
# .env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=api.moov-ebillings.tg,localhost
DATABASE_URL=postgresql://user:pass@localhost/moov_ebillings
CORS_ORIGINS=https://moov-ebillings.tg
```

### Gunicorn

```bash
# Installer Gunicorn
pip install gunicorn

# Lancer
gunicorn moov_backend.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## 🤝 Contribution

### Workflow Git

```bash
# Créer une branche
git checkout -b feature/nouvelle-fonctionnalite

# Faire les modifications
git add .
git commit -m "feat: ajout nouvelle fonctionnalité"

# Pousser
git push origin feature/nouvelle-fonctionnalite

# Créer une Pull Request
```

### Standards Code

- **PEP 8** pour Python
- **Tests** pour nouvelles fonctionnalités
- **Documentation** dans les docstrings
- **Migrations** pour changements DB

---

## 📞 Support

- **Documentation** : Voir fichiers PHASE*_README.md
- **API Docs** : http://localhost:8000/api/docs/
- **Issues** : Créer une issue GitHub

---

## 📄 Licence

© 2026 Moov Africa Togo - Tous droits réservés

---

## 🎉 Développé avec

- **Django** 6.0.3
- **Django REST Framework** 3.14+
- **Simple JWT** pour authentification
- **DRF Spectacular** pour documentation
- **Django Filter** pour filtres avancés
- **Django CORS Headers** pour CORS

---

**Statut** : ✅ Production-Ready  
**Version** : 1.0.0  
**Date** : Juillet 2026
