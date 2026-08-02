# 🚀 Démarrage Rapide - Phase 4 Backend

Guide pour tester immédiatement la Phase 4 (Facturation)

---

## ⚡ Lancement en 5 Minutes

### 1. Vérifier que le serveur est lancé

```bash
cd Back
python manage.py runserver
```

✅ Serveur disponible sur : http://localhost:8000

---

### 2. Accéder à la documentation API

Ouvrir dans le navigateur :
- **Swagger UI** : http://localhost:8000/api/docs/
- **ReDoc** : http://localhost:8000/api/redoc/

---

### 3. Se connecter (obtenir un token JWT)

**Dans Swagger UI** :
1. Aller à `/api/auth/login/` → `POST`
2. Cliquer sur "Try it out"
3. Entrer :
```json
{
  "email": "agent@moov.tg",
  "password": "agent123"
}
```
4. Cliquer "Execute"
5. **Copier le token `access`** de la réponse

**OU en ligne de commande** :
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"agent@moov.tg","password":"agent123"}'
```

---

### 4. Autoriser les requêtes dans Swagger

1. Cliquer sur le bouton "Authorize" (🔒) en haut de Swagger
2. Entrer : `Bearer YOUR_ACCESS_TOKEN`
3. Cliquer "Authorize"

✅ Toutes les requêtes utiliseront maintenant votre token !

---

## 🧪 Tester Phase 4 - Facturation

### Test 1 : Calculer la facture d'une ligne

**Endpoint** : `POST /api/billing/invoices/calculate_line/`

```json
{
  "line_id": 1,
  "periode_debut": "2026-07-01",
  "periode_fin": "2026-07-31",
  "conso_data_mo": 10240,
  "conso_duree_secondes": 3600,
  "conso_sms": 150,
  "services_supplementaires": [
    {
      "nom": "BlackBerry 1Go",
      "prix": "2000"
    }
  ]
}
```

**Résultat attendu** :
- Calcul DATA (palier 10 Go = 8000 FCFA)
- Calcul VOIX (60 min)
- Calcul SMS (150 unités)
- Services supplémentaires
- Total HT + TVA + TTC

---

### Test 2 : Générer des factures en masse

**Endpoint** : `POST /api/billing/invoices/generate/`

```json
{
  "cycle": "HYB",
  "periode_debut": "2026-07-01",
  "periode_fin": "2026-07-31"
}
```

**Résultat attendu** :
- Factures créées pour toutes les entreprises avec lignes actives cycle HYB
- Statut : BROUILLON
- Numéros de facture auto-générés

---

### Test 3 : Lister les factures

**Endpoint** : `GET /api/billing/invoices/`

**Avec filtres** :
- `GET /api/billing/invoices/?statut=BROUILLON`
- `GET /api/billing/invoices/?periode_debut=2026-07-01`
- `GET /api/billing/invoices/?search=FAC-`

---

### Test 4 : Valider une facture

**Endpoint** : `POST /api/billing/invoices/{id}/valider/`

```json
{
  "commentaire": "Validation après vérification manuelle"
}
```

**Résultat** :
- Statut passe de BROUILLON → EN_COURS
- Historique créé

---

### Test 5 : Créer une publication

**Endpoint** : `POST /api/billing/publications/`

```json
{
  "cycle_facturation": "HYB",
  "periode_debut": "2026-07-01",
  "periode_fin": "2026-07-31",
  "commentaire": "Publication test juillet 2026"
}
```

---

### Test 6 : Publier des factures en masse

**Endpoint** : `POST /api/billing/publications/{pub-id}/publish/`

```json
{
  "invoice_ids": [
    "uuid-facture-1",
    "uuid-facture-2"
  ],
  "commentaire": "Publication validée"
}
```

**Résultat** :
- Factures passent à statut PUBLIEE
- Publication mise à jour (nombre lignes, montant total)

---

### Test 7 : Statistiques factures

**Endpoint** : `GET /api/billing/invoices/stats/`

**Résultat** :
- Total factures
- Répartition par statut
- Montants totaux par statut

---

## 🧪 Lancer les Tests Automatisés

### Tests Phase 4 uniquement

```bash
cd Back

# Tests calcul tarification
python manage.py test billing.tests.CalculTarificationTests

# Tests API factures
python manage.py test billing.tests.InvoiceTests

# Tests publications
python manage.py test billing.tests.PublicationTests
```

### Tous les tests (Phases 1-4)

```bash
python manage.py test
```

**Résultat attendu** :
```
Ran 63 tests in X.XXXs

OK
```

---

## 📊 Vérifier les Données

### Via Swagger UI

1. Aller à http://localhost:8000/api/docs/
2. Tester les endpoints GET :
   - `/api/billing/companies/` - Liste contrats
   - `/api/billing/lines/` - Liste lignes
   - `/api/billing/invoices/` - Liste factures
   - `/api/billing/publications/` - Liste publications

### Via Django Admin

```bash
# Créer un superuser si pas déjà fait
python manage.py createsuperuser

# Accéder à l'admin
http://localhost:8000/admin/
```

---

## 🔍 Débuggage

### Vérifier les logs

```bash
# Logs généraux
tail -f Back/logs/app.log

# Logs sécurité
tail -f Back/logs/security.log
```

### Vérifier la base de données

```bash
cd Back
python manage.py dbshell

# Commandes SQLite
SELECT COUNT(*) FROM invoices;
SELECT * FROM invoices LIMIT 5;
SELECT * FROM publications;
```

---

## 🎯 Scénario Complet de Test

### Workflow facturation end-to-end

```bash
# 1. Se connecter
POST /api/auth/login/
→ Obtenir token

# 2. Créer un contrat avec lignes (si pas existant)
POST /api/billing/companies/
{
  "compte": "C26TEST999",
  "raison_sociale": "Test Company",
  "categorie": "PE",
  "lignes": [
    {
      "msisdn": "90999999",
      "utilisateur": "Test User",
      "cycle": "HYB",
      "forfait": "5000"
    }
  ]
}

# 3. Générer factures
POST /api/billing/invoices/generate/
{
  "cycle": "HYB",
  "periode_debut": "2026-07-01",
  "periode_fin": "2026-07-31"
}

# 4. Lister les factures brouillon
GET /api/billing/invoices/?statut=BROUILLON

# 5. Calculer une ligne (preview)
POST /api/billing/invoices/calculate_line/
{
  "line_id": {id-de-la-ligne},
  "periode_debut": "2026-07-01",
  "periode_fin": "2026-07-31",
  "conso_data_mo": 5120,
  "conso_duree_secondes": 1800,
  "conso_sms": 50
}

# 6. Valider une facture
POST /api/billing/invoices/{facture-id}/valider/
{
  "commentaire": "Facture vérifiée"
}

# 7. Créer une publication
POST /api/billing/publications/
{
  "cycle_facturation": "HYB",
  "periode_debut": "2026-07-01",
  "periode_fin": "2026-07-31"
}

# 8. Publier les factures
POST /api/billing/publications/{pub-id}/publish/
{
  "invoice_ids": ["{facture-uuid}"]
}

# 9. Vérifier statistiques
GET /api/billing/invoices/stats/
GET /api/billing/publications/{pub-id}/stats/
```

---

## ✅ Checklist Vérification

Après avoir testé, vérifier que :

- [ ] Je peux me connecter et obtenir un token JWT
- [ ] Je peux calculer la facture d'une ligne
- [ ] Je peux générer des factures en masse
- [ ] Je peux valider une facture (BROUILLON → EN_COURS)
- [ ] Je peux créer une publication
- [ ] Je peux publier des factures (→ PUBLIEE)
- [ ] Je peux voir les statistiques
- [ ] Les tests automatisés passent (63/63)
- [ ] La documentation Swagger affiche tous les endpoints

---

## 🎉 Tout Fonctionne ?

**Félicitations !** La Phase 4 est opérationnelle ! 🚀

### Prochaine étape

1. **Intégrer au Frontend** React
2. **Tests utilisateur** finaux
3. **Préparer le déploiement** production

---

## 🆘 Besoin d'Aide ?

### Documentation
- [PHASE4_README.md](Back/PHASE4_README.md) - Guide complet
- [BACKEND_PHASE4_COMPLET.md](Back/BACKEND_PHASE4_COMPLET.md) - Récapitulatif
- [BACKEND_FINAL_COMPLET.md](Back/BACKEND_FINAL_COMPLET.md) - Vue d'ensemble

### Swagger UI
- http://localhost:8000/api/docs/ - Interface interactive

### Tests
```bash
python manage.py test billing.tests.InvoiceTests -v 2
```

---

**Bon test !** 🎯
