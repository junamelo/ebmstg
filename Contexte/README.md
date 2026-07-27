# Moov Africa Backend - Django REST Framework

Backend Django pour le portail de facturation Moov Africa Togo.

## 🚀 Démarrage rapide

### Prérequis
- Python 3.14+
- pip

### Installation

```bash
# Installer les dépendances
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers

# Créer la base de données
python manage.py migrate

# Créer un superuser
python create_superuser.py
# Email: admin@moov.tg
# Password: admin123

# Démarrer le serveur
python manage.py runserver
```

Le serveur sera accessible sur `http://localhost:8000`

## 📡 API Endpoints

### Authentification

#### POST `/api/auth/register/`
Inscription d'un nouvel utilisateur

```json
{
  "email": "user@example.com",
  "username": "user",
  "password": "password123",
  "password_confirm": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "EMPLOYE",
  "telephone": "90000001"
}
```

#### POST `/api/auth/login/`
Connexion d'un utilisateur

```json
{
  "email": "admin@moov.tg",
  "password": "admin123"
}
```

Retourne un token JWT et les informations de l'utilisateur.

#### GET `/api/auth/profile/`
Profil de l'utilisateur connecté (requiert authentification)

### Entreprises (Companies)

#### GET `/api/billing/companies/`
Liste de toutes les entreprises

#### POST `/api/billing/companies/`
Créer une nouvelle entreprise

```json
{
  "compte": "CT-000001",
  "raison_sociale": "Entreprise Exemple",
  "code_commercial": "7000",
  "nom_commercial": "Commercial Name",
  "categorie": "PE",
  "adresse": "123 Rue Example",
  "adresse2": "contact@example.com",
  "statut": "ACTIF"
}
```

#### GET `/api/billing/companies/{id}/`
Détails d'une entreprise

#### PUT `/api/billing/companies/{id}/`
Modifier une entreprise

#### DELETE `/api/billing/companies/{id}/`
Supprimer une entreprise

### Lignes (Lines)

#### GET `/api/billing/lines/`
Liste de toutes les lignes

#### POST `/api/billing/lines/`
Créer une nouvelle ligne

```json
{
  "company": 1,
  "msisdn": "79000000",
  "utilisateur": "Employé Name",
  "forfait": 15000.00,
  "cycle": "HYB",
  "option_blackberry": "BB15_6",
  "option_nolimit": "AI50",
  "est_incognito": false,
  "facture_detaillee": true,
  "est_non_revenu": false,
  "statut": "ACTIF"
}
```

#### GET `/api/billing/lines/{id}/`
Détails d'une ligne

#### PUT `/api/billing/lines/{id}/`
Modifier une ligne

#### DELETE `/api/billing/lines/{id}/`
Supprimer une ligne

## 🔐 Rôles utilisateurs

- **SUPER_ADMIN** : Administrateur système
- **AGENT_FACTURATION** : Agent de facturation
- **PAYEUR** : Payeur (entreprise)
- **EMPLOYE** : Employé (ligne individuelle)

## 📊 Modèles de données

### User
- email, username, first_name, last_name
- role (SUPER_ADMIN, AGENT_FACTURATION, PAYEUR, EMPLOYE)
- telephone
- est_actif

### Company
- compte (unique)
- raison_sociale
- code_commercial, nom_commercial
- categorie (GE, PE, P, OI, EP, A, NR)
- adresse, adresse2 (email)
- statut
- payeur (FK vers User)

### Line
- company (FK vers Company)
- msisdn (unique)
- utilisateur
- forfait (FCFA)
- cycle (HYB, OP)
- option_blackberry, option_nolimit
- est_incognito, facture_detaillee, est_non_revenu
- statut
- employe (FK vers User)

## 🔧 Configuration

### CORS
Le backend est configuré pour accepter les requêtes de :
- http://localhost:3000
- http://127.0.0.1:3000
- http://localhost:5173
- http://127.0.0.1:5173

### JWT
- Access token lifetime : 2 heures
- Refresh token lifetime : 7 jours

## 📝 Structure du projet

```
Back/
├── manage.py
├── moov_backend/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── models.py (User)
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── billing/
│   ├── models.py (Company, Line)
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
└── create_superuser.py
```

## 🧪 Tests

Pour tester les endpoints, vous pouvez utiliser :
- Postman
- curl
- Le frontend React (http://localhost:5173)

### Exemple de test avec curl

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@moov.tg","password":"admin123"}'

# Créer une entreprise (remplacer TOKEN par le token JWT)
curl -X POST http://localhost:8000/api/billing/companies/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"compte":"CT-000001","raison_sociale":"Test"}'
```

## 📚 Prochaines étapes

- [ ] Ajouter les modèles Package et Service
- [ ] Implémenter la simulation de facturation
- [ ] Ajouter le parsing PDF
- [ ] Créer les endpoints pour l'Agent Facturation
- [ ] Ajouter les permissions par rôle
- [ ] Implémenter les tests unitaires
