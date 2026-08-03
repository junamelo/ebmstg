# Commandes Rapides - Tests et Lancement

## 🚀 Lancement Rapide

### Backend Django
```bash
cd Back
python manage.py runserver
```
→ API disponible sur `http://127.0.0.1:8000`

### Frontend React
```bash
cd Front
npm run dev
```
→ Interface disponible sur `http://localhost:5173`

---

## ✅ Vérifications Backend

### Check configuration
```bash
cd Back
python manage.py check
```
**Attendu :** `System check identified no issues (0 silenced)`

### Lancer tous les tests
```bash
cd Back
python manage.py test
```
**Attendu :** `Ran 97 tests in ~320s - OK`

### Lancer tests spécifiques
```bash
# Tests d'authentification
python manage.py test accounts.test_auth

# Tests d'affectation
python manage.py test billing.test_affectation

# Tests de publication
python manage.py test billing.test_publication

# Tests généraux billing
python manage.py test billing.tests
```

### Créer le compte chef (si besoin)
```bash
cd Back
python create_chef.py
```

---

## ✅ Vérifications Frontend

### Build de production
```bash
cd Front
npm run build
```
**Attendu :** `✓ built in ~10s`

### Lint (optionnel)
```bash
cd Front
npm run lint
```

### Vérifier structure node_modules
```bash
cd Front
npm list --depth=0
```

---

## 🔍 Debug et Logs

### Logs backend en mode verbose
```bash
cd Back
python manage.py runserver --verbosity 2
```

### Shell Django interactif
```bash
cd Back
python manage.py shell
```

**Commandes utiles dans le shell :**
```python
# Vérifier les services actifs
from billing.models import Service, Package
Service.objects.filter(est_actif=True).count()
Package.objects.filter(est_actif=True).count()

# Vérifier les utilisateurs
from accounts.models import User
User.objects.filter(role='EMPLOYE').count()
User.objects.filter(is_active=True).count()

# Vérifier les entreprises et lignes
from billing.models import Company, Line
Company.objects.count()
Line.objects.filter(statut='ACTIF').count()
```

### Inspecter la base de données
```bash
cd Back
python manage.py dbshell
```

**Requêtes SQL utiles :**
```sql
-- Compter les services actifs
SELECT COUNT(*) FROM services WHERE est_actif = 1;

-- Lister les utilisateurs par rôle
SELECT role, COUNT(*) FROM accounts_user GROUP BY role;

-- Vérifier les lignes affectées
SELECT COUNT(*) FROM lines WHERE employe_id IS NOT NULL;
```

---

## 🧪 Tests API Manuels (curl)

### Tester connexion
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@moov.tg","password":"admin123"}'
```

### Tester stats admin (avec token)
```bash
TOKEN="votre_token_ici"
curl http://127.0.0.1:8000/api/billing/stats/admin/ \
  -H "Authorization: Bearer $TOKEN"
```

### Tester liste services
```bash
curl http://127.0.0.1:8000/api/billing/services/ \
  -H "Authorization: Bearer $TOKEN"
```

### Tester liste forfaits
```bash
curl http://127.0.0.1:8000/api/billing/packages/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔧 Maintenance Base de Données

### Créer migrations
```bash
cd Back
python manage.py makemigrations
```

### Appliquer migrations
```bash
cd Back
python manage.py migrate
```

### Reset base de données (⚠️ ATTENTION : supprime toutes les données)
```bash
cd Back
# Windows
del db.sqlite3
# Linux/Mac
rm db.sqlite3

python manage.py migrate
python manage.py createsuperuser
python create_chef.py
```

---

## 📊 Monitoring et Performance

### Temps de réponse API
```bash
curl -w "@curl-format.txt" -o /dev/null -s http://127.0.0.1:8000/api/billing/stats/admin/
```

**Créer curl-format.txt :**
```
time_total:  %{time_total}s
```

### Taille du bundle frontend
```bash
cd Front
npm run build
ls -lh dist/assets/*.js
```

---

## 🐛 Résolution Problèmes Courants

### Erreur "Port already in use"
```bash
# Backend (port 8000)
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Frontend (port 5173)
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

### Erreur "Module not found"
```bash
# Backend
cd Back
pip install -r requirements.txt

# Frontend
cd Front
npm install
```

### Erreur CORS
Vérifier dans `Back/config/settings.py` :
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

---

## 📋 Checklist Pré-Test

Avant de lancer les tests manuels :

```bash
# 1. Vérifier backend
cd Back
python manage.py check
python manage.py test

# 2. Vérifier frontend
cd Front
npm run build

# 3. Lancer les serveurs
# Terminal 1
cd Back
python manage.py runserver

# Terminal 2
cd Front
npm run dev

# 4. Ouvrir navigateur
# http://localhost:5173
```

---

## 🎯 Tests Rapides Post-Correction

### Test BUG 5 (AdminDashboard)
1. Connexion : `admin@moov.tg / admin123`
2. Aller sur dashboard
3. Vérifier stats affichées sans erreur

### Test BUG 4 (Simulation)
1. Connexion : `99475555 / employe123`
2. Aller sur `/simulation`
3. Tester HYBRIDE et OPEN

### Test BUG 3 (Ajout ligne)
1. Connexion : `agent@moov.tg / agent123`
2. Aller sur un contrat
3. Cliquer "Nouvelle Ligne"
4. Ajouter MSISDN unique

### Test BUG 2 (Forfaits)
1. Connexion : `agent@moov.tg / agent123`
2. Aller sur `/agent/forfaits`
3. Vérifier liste forfaits affichée

---

## 💡 Raccourcis Utiles

### Nettoyer les caches
```bash
# Backend
cd Back
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete

# Frontend
cd Front
rm -rf node_modules/.vite
rm -rf dist
```

### Réinstaller proprement
```bash
# Backend
cd Back
pip install --upgrade pip
pip install -r requirements.txt

# Frontend
cd Front
rm -rf node_modules package-lock.json
npm install
```

---

**Dernière mise à jour :** 2 août 2026  
**Validé pour :** Django 5.1.5, React 18, Node 20+
