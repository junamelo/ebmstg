# 🔍 DIAGNOSTIC CONNEXION AGENT - REDIRECTION LOGIN

## 🎯 PROBLÈME
Tu te connectes en tant qu'agent, tu peux accéder au dashboard, mais quand tu vas sur `/agent/publication`, tu es redirigé vers login.

---

## ✅ CORRECTIONS APPLIQUÉES

### 1️⃣ **Authentification Frontend ↔ Backend**
- ✅ AuthService connecté au backend Django (`USE_MOCK = false`)
- ✅ Endpoints corrigés : `/auth/login/`, `/auth/logout/`
- ✅ Paramètres adaptés : `email/password` au lieu de `login/motDePasse`
- ✅ Réponse Django gérée : `data.access` → token, `data.user` → user

### 2️⃣ **Gestion des tokens JWT**
- ✅ Token correctement stocké dans localStorage
- ✅ Headers Authorization ajoutés automatiquement
- ✅ Interceptor 401 améliore (évite redirection infinie)
- ✅ Logs debug ajoutés pour diagnostic

### 3️⃣ **Protection des routes**
- ✅ ProtectedRoute vérifie le rôle AGENT_FACTURATION
- ✅ Redirection selon le rôle après connexion

---

## 🧪 PROCESSUS DE TEST DIAGNOSTIC

### Étape 1 : Test backend Django
```bash
cd Back
python debug_auth_tokens.py
```
**Résultat attendu :**
- ✅ Utilisateur agent@moov.tg trouvé
- ✅ Authentification réussie  
- ✅ Token généré et valide
- ✅ Permissions OK

### Étape 2 : Test connexion frontend
1. **Démarrer** : `cd Front && npm run dev`
2. **Ouvrir** : http://localhost:3000/login
3. **Se connecter** : `agent@moov.tg` / `agent123`
4. **Observer console** (F12) :
   - 🔑 Token envoyé : eyJ0eXAiOiJKV1Q...
   - ✅ Redirection vers `/agent/dashboard`

### Étape 3 : Test accès publication
1. **Depuis dashboard** → Cliquer "Publication PDF"
2. **Ou directement** → `/agent/publication`
3. **Observer console** :
   - Si 401 → Token expiré/invalide
   - Si redirection → Problème permissions

---

## 🔧 DIAGNOSTIC AVANCÉ

### Si redirection persiste, vérifier :

#### **1. Token dans localStorage**
```javascript
// Console browser (F12)
console.log('Token:', localStorage.getItem('token'))
console.log('User:', JSON.parse(localStorage.getItem('user')))
```

#### **2. Requête qui échoue**
- **Network tab** (F12) → Voir quelle requête retourne 401
- **Probable** : `/api/billing/publications/` (historique)

#### **3. Backend Django permissions**
```bash
# Vérifier permissions dans Django
cd Back
python manage.py shell

from accounts.models import User
agent = User.objects.get(email='agent@moov.tg')
print(f"Role: {agent.role}")
print(f"Active: {agent.is_active}")
print(f"Status: {agent.status}")
```

---

## 🚀 SOLUTIONS SELON DIAGNOSTIC

### **Cas 1 : Token expiré rapidement**
```javascript
// Dans Front/src/services/api.js - augmenter timeout
// Ou backend Django settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),  # Au lieu de 2h
}
```

### **Cas 2 : Requête spécifique qui échoue**
```javascript
// Temporairement mock cette requête
// Dans adminService.js
export const getHistoriquePublications = async () => {
  return []  // Mock temporaire
}
```

### **Cas 3 : Permissions manquantes**
```python
# Backend - ajouter permission
# Dans accounts/permissions.py vérifier CanUploadPDF
```

---

## 📊 ENDPOINTS ACTIFS À TESTER

### ✅ **Authentification**
```http
POST http://localhost:8000/api/auth/login/
{
  "email": "agent@moov.tg",
  "password": "agent123"  
}
```

### ✅ **Upload PDF (principal)**
```http
POST http://localhost:8000/api/billing/invoices/upload_bulk_pdf/
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

### ⚠️ **Historique (peut échouer)**
```http
GET http://localhost:8000/api/billing/publications/
Authorization: Bearer {token}
```

---

## 💡 SOLUTION TEMPORAIRE

Si le problème persiste, **désactiver temporairement** la requête historique :

```javascript
// Dans Front/src/pages/agent/PublicationPdf.jsx
useEffect(() => { 
  // chargerHistorique()  // Commenter temporairement
}, [])

const chargerHistorique = () => {
  // Mock temporaire
  setHistorique([])
}
```

---

## 🎯 PROCHAINES ÉTAPES

1. **Lancer le diagnostic** : `python debug_auth_tokens.py`
2. **Tester la connexion** avec console ouverte (F12)
3. **Identifier la requête** qui cause le 401
4. **Appliquer la solution** selon le cas

**L'objectif : Accéder à `/agent/publication` sans redirection !** 🚀