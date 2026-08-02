# 🔗 TEST CONNEXION FRONTEND ↔ BACKEND

## ✅ CORRECTIONS APPLIQUÉES

### 1. **AdminService** mis à jour
- ✅ `USE_MOCK = false`
- ✅ Endpoint correct : `/billing/invoices/upload_bulk_pdf/`
- ✅ Paramètres Django : `auto_match`, `cycle`, `periode_debut`, `periode_fin`

### 2. **PublicationPdf Component** mis à jour
- ✅ Interface adaptée aux paramètres Django
- ✅ Gestion des réponses backend réelles
- ✅ Messages d'erreur améliorés
- ✅ Historique compatible avec l'API Publications

### 3. **API Configuration** mise à jour
- ✅ URL : `http://localhost:8000/api`
- ✅ CORS configuré pour React (port 3000)
- ✅ Headers JWT automatiques

---

## 🚀 TEST ÉTAPE PAR ÉTAPE

### Étape 1 : Démarrer le backend Django
```bash
cd Back
python manage.py runserver 8000
```
**Résultat attendu :** Serveur sur http://localhost:8000

### Étape 2 : Démarrer le frontend React
```bash
cd Front
npm run dev
```
**Résultat attendu :** Interface sur http://localhost:3000

### Étape 3 : Créer les données de test
```bash
cd Back
python create_test_data.py
```
**Résultat attendu :** 3 entreprises + 3 factures EN_COURS

### Étape 4 : Créer le PDF de test
```bash
cd Back
python test_pdf_creation.py
```
**Résultat attendu :** `media/test_bulk_moov.pdf`

### Étape 5 : Tester la connexion complète
1. **Se connecter** : `agent@moov.tg` / `agent123`
2. **Aller** à `/agent/publication` 
3. **Upload** le fichier `Back/media/test_bulk_moov.pdf`
4. **Vérifier** : 3 PDF créés, 3 factures mises à jour

---

## 🔍 ENDPOINTS TESTÉS

### ✅ Publications
```http
POST http://localhost:8000/api/billing/invoices/upload_bulk_pdf/
GET  http://localhost:8000/api/billing/publications/
```

### ✅ Authentification  
```http
POST http://localhost:8000/api/auth/login/
POST http://localhost:8000/api/auth/refresh/
```

### ✅ Factures
```http
GET http://localhost:8000/api/billing/invoices/?statut=VALIDEE
```

---

## 📊 RÉSULTAT ATTENDU

### Upload PDF réussi :
```json
{
  "message": "PDF traité avec succès : 3 fichier(s) créé(s)",
  "total_blocks": 3,
  "files_created": 3,
  "auto_match": {
    "matched": 3,
    "not_matched": 0,
    "attached": [
      {
        "invoice_id": "uuid",
        "numero_facture": "FAC-C26TEST001-202607-001",
        "filename": "FAC-C26TEST001-202607-001.pdf"
      }
    ]
  }
}
```

### Interface React :
- ✅ Message : "✅ Traitement terminé ! 3 PDF créés, 3 factures mises à jour"
- ✅ Historique mis à jour
- ✅ Pas d'erreurs CORS
- ✅ Pas d'erreurs 404

---

## ⚠️ EN CAS DE PROBLÈME

### Erreur CORS
**Symptôme :** "Access-Control-Allow-Origin"
**Solution :** Vérifier que Django tourne sur port 8000

### Erreur 404
**Symptôme :** "Not Found /api/billing/..."  
**Solution :** Vérifier l'URL dans `api.js`

### Erreur Auth
**Symptôme :** "401 Unauthorized"
**Solution :** Créer un token avec `python create_test_data.py`

### PyPDF2 manquant
**Symptôme :** "PyPDF2 non installé"
**Solution :** `pip install PyPDF2==3.0.1`

---

## 🎯 VALIDATION FINALE

**Quand c'est bon :**
- [ ] Frontend se connecte sans erreur
- [ ] Upload PDF fonctionne
- [ ] 3/3 PDFs matchés automatiquement  
- [ ] Historique affiché correctement
- [ ] Pas d'erreurs console

**→ Publication PDF 100% fonctionnelle ! 🚀**