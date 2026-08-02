# 📊 INFORMATIONS BASE DE DONNÉES

## ✅ OUI, la base de données est liée à SQLite !

---

## 🔧 CONFIGURATION

### Type de base de données
**SQLite 3** - Base de données légère fichier local

### Configuration Django
```python
# moov_backend/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Emplacement du fichier
```
Back/db.sqlite3
Taille : 339 KB (339,968 bytes)
Dernière modification : 30/07/2026 12:03 PM
```

---

## 📊 CONTENU ACTUEL DE LA BASE

### Tables et données
```
✅ Entreprises (companies)      : 9 enregistrements
✅ Lignes (lines)                : 23 enregistrements
✅ Factures (invoices)           : 29 enregistrements
✅ Publications                  : 0 enregistrements
✅ Utilisateurs                  : Au moins 2 (agent, payeur)
✅ Packages, Services, Tarifs    : Données de test
```

### Statistiques
```
Total factures par statut:
  - EN_COURS : 26
  - VALIDEE  : 3

Montant total facturé : 224,200 FCFA

Top entreprise : WACEM SA (53,100 FCFA, 10 factures)
```

---

## 🎯 COMMENT ÇA FONCTIONNE

### Django ORM
Django utilise son ORM (Object-Relational Mapping) pour :
1. **Abstraire** la base de données
2. **Traduire** les requêtes Python en SQL
3. **Gérer** automatiquement les connexions

### Exemple de requête
```python
# Python (Django ORM)
Invoice.objects.filter(statut='EN_COURS').count()

# SQL équivalent généré automatiquement
SELECT COUNT(*) FROM invoices WHERE statut = 'EN_COURS';
```

### Compatibilité
Le même code Django ORM fonctionne avec :
- ✅ **SQLite** (développement)
- ✅ **PostgreSQL** (production)
- ✅ **MySQL/MariaDB**
- ✅ **Oracle**

---

## 🔄 MIGRATIONS

### Migrations appliquées
Toutes les migrations sont synchronisées :
```
Phase 1 : Authentification (accounts)
Phase 2 : Entreprises et lignes (billing)
Phase 3 : Packages et services (billing)
Phase 4 : Factures et publications (billing)
```

### Schéma de la base
```
accounts_user
├── id (UUID)
├── email
├── role
├── created_by
└── ...

billing_company
├── id (auto)
├── compte
├── raison_sociale
├── payeur_id (FK → accounts_user)
└── ...

billing_line
├── id (auto)
├── company_id (FK → billing_company)
├── msisdn
├── employe_id (FK → accounts_user)
└── ...

billing_invoice
├── id (UUID)
├── company_id (FK → billing_company)
├── numero_facture
├── montant_ttc
└── ...

billing_publication
├── id (UUID)
├── agent_id (FK → accounts_user)
├── cycle_facturation
└── ...
```

---

## 🚀 AVANTAGES DE SQLITE POUR CE PROJET

### ✅ Pour le développement
1. **Simplicité** : Pas de serveur à installer
2. **Portabilité** : Un seul fichier
3. **Rapidité** : Setup immédiat
4. **Légèreté** : Pas de configuration complexe

### ✅ Pour ce projet spécifique
- Volume de données modéré
- Application monoposte/démonstration
- Projet de fin d'année (pas en production)
- Facile à partager/sauvegarder

---

## 📈 SI BESOIN DE PASSER EN PRODUCTION

### Migration vers PostgreSQL

#### 1. Installer PostgreSQL
```bash
# Windows
# Télécharger depuis postgresql.org

# Créer une base
CREATE DATABASE moov_billing;
CREATE USER moov_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE moov_billing TO moov_user;
```

#### 2. Modifier settings.py
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'moov_billing',
        'USER': 'moov_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### 3. Exporter/Importer les données
```bash
# Export depuis SQLite
python manage.py dumpdata > data.json

# Import vers PostgreSQL
python manage.py migrate
python manage.py loaddata data.json
```

---

## 🔍 OUTILS D'INSPECTION

### 1. Django Admin
```
http://localhost:8000/admin/
```

### 2. Django Shell
```bash
python manage.py shell

>>> from billing.models import Invoice
>>> Invoice.objects.count()
29
```

### 3. Outils SQLite
- **DB Browser for SQLite** (GUI)
- **sqlite3** (CLI)
```bash
sqlite3 db.sqlite3
.tables
SELECT * FROM billing_invoice LIMIT 5;
```

### 4. Django Debug Toolbar
Voir les requêtes SQL exécutées en temps réel

---

## 📊 PERFORMANCE

### SQLite est suffisant si :
- ✅ Moins de 100,000 factures
- ✅ Moins de 100 utilisateurs concurrents
- ✅ Principalement lecture
- ✅ Application locale/démonstration

### Passer à PostgreSQL si :
- ❌ Plus de 100,000 enregistrements
- ❌ Nombreux utilisateurs simultanés
- ❌ Écritures intensives
- ❌ Besoin de réplication/backup

---

## 🎯 CONCLUSION

### Pour votre projet
**SQLite est PARFAIT** car :
1. ✅ Projet de fin d'année
2. ✅ Démonstration/présentation
3. ✅ Volume de données raisonnable
4. ✅ Simplicité de setup
5. ✅ Facilité de partage

### La Phase 5 (Stats)
**Fonctionne parfaitement avec SQLite** :
- ✅ Agrégations SQL supportées
- ✅ Requêtes complexes OK
- ✅ Performance suffisante
- ✅ Toutes les données accessibles

---

## 📁 RÉSUMÉ TECHNIQUE

| Aspect | Détail |
|--------|--------|
| **Type** | SQLite 3 |
| **Fichier** | `Back/db.sqlite3` (339 KB) |
| **ORM** | Django ORM |
| **Entreprises** | 9 |
| **Lignes** | 23 |
| **Factures** | 29 |
| **Montant total** | 224,200 FCFA |
| **Migrations** | ✅ Toutes appliquées |
| **Stats Phase 5** | ✅ Compatible |
| **Production ready** | ⚠️ Pour démo uniquement |

---

**Date** : 30 Juillet 2026  
**Statut** : ✅ BASE DE DONNÉES OPÉRATIONNELLE  
**Recommandation** : SQLite parfait pour ce projet académique
