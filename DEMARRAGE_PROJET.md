# 🚀 Comment Démarrer le Projet Moov e-Billings

**Date** : 30 juillet 2026  
**Mis à jour** : Correction problème Network Error

---

## ⚠️ PROBLÈME RENCONTRÉ

### Erreur : `❌ Network Error`

```
GET http://localhost:8000/api/billing/publications/ net::ERR_CONNECTION_REFUSED
POST http://localhost:8000/api/billing/invoices/upload_bulk_pdf/ net::ERR_CONNECTION_REFUSED
```

**Cause** : Le serveur backend Django n'était pas démarré.

---

## ✅ SOLUTION - Démarrage en 2 Étapes

### **Étape 1 : Démarrer le Backend Django**

Ouvrir un terminal (PowerShell ou CMD) :

```bash
cd "C:\Users\Benoit\Documents\BURRO\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026\Back"
python manage.py runserver
```

**Résultat attendu** :
```
Django version 6.0.3, using settings 'moov_backend.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

✅ Le backend est maintenant accessible sur : **http://localhost:8000**

---

### **Étape 2 : Démarrer le Frontend React (Vite)**

Ouvrir un **NOUVEAU** terminal (ne pas fermer le premier) :

```bash
cd "C:\Users\Benoit\Documents\BURRO\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026\Front"
npm run dev
```

**Résultat attendu** :
```
VITE v5.4.21  ready in 527 ms
➜  Local:   http://localhost:3001/
➜  Network: use --host to expose
```

✅ Le frontend est maintenant accessible sur : **http://localhost:3001**

---

## 🌐 Accéder à l'Application

Une fois les 2 serveurs démarrés, ouvrir votre navigateur :

```
http://localhost:3001
```

**Note** : Le port peut changer si 3001 est occupé (Vite choisira automatiquement 3002, 3003, etc.)

---

## 📊 Vérification de l'État

### Vérifier que le Backend fonctionne

Ouvrir dans le navigateur :
```
http://localhost:8000/admin/
```

Vous devriez voir la page d'administration Django.

### Vérifier les APIs

```
http://localhost:8000/api/accounts/users/
http://localhost:8000/api/billing/companies/
http://localhost:8000/api/billing/publications/
```

Si vous n'êtes pas connecté, vous verrez une erreur d'authentification (normal).

---

## ⚠️ Erreurs Courantes et Solutions

### Erreur 1 : `Port 8000 is already in use`

**Cause** : Le backend est déjà démarré ailleurs.

**Solution** :
1. Fermer tous les terminaux
2. Ouvrir le Gestionnaire des tâches (Ctrl+Shift+Échap)
3. Chercher `python.exe` et terminer le processus
4. Relancer `python manage.py runserver`

### Erreur 2 : `npm run dev` ne fonctionne pas

**Cause** : Node modules non installés.

**Solution** :
```bash
cd Front
npm install
npm run dev
```

### Erreur 3 : `ModuleNotFoundError: No module named 'django'`

**Cause** : Environnement virtuel non activé ou dépendances non installées.

**Solution** :
```bash
cd Back
pip install -r requirements.txt
python manage.py runserver
```

### Erreur 4 : `CORS Error` dans la console

**Cause** : Le backend n'autorise pas les requêtes du frontend.

**Solution** : Vérifier `Back/moov_backend/settings.py` :
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:3001',  # Ajouter si Vite utilise 3001
    'http://127.0.0.1:3001',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]
```

---

## 🛠️ Scripts Utiles

### Démarrage Rapide (Windows)

Créer un fichier `start_project.bat` :

```batch
@echo off
echo 🚀 Démarrage du projet Moov e-Billings...

echo.
echo 📦 Démarrage du backend Django...
start cmd /k "cd /d C:\Users\Benoit\Documents\BURRO\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026\Back && python manage.py runserver"

timeout /t 3 /nobreak >nul

echo.
echo 🎨 Démarrage du frontend React...
start cmd /k "cd /d C:\Users\Benoit\Documents\BURRO\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026\Front && npm run dev"

echo.
echo ✅ Projet démarré !
echo 🌐 Backend : http://localhost:8000
echo 🎨 Frontend : http://localhost:3001
pause
```

Double-cliquer sur ce fichier pour démarrer les 2 serveurs automatiquement.

---

## 📝 Checklist avant de Travailler

Avant chaque session de développement :

- [ ] Ouvrir **2 terminaux**
- [ ] Terminal 1 : `cd Back && python manage.py runserver`
- [ ] Terminal 2 : `cd Front && npm run dev`
- [ ] Vérifier que les 2 serveurs sont démarrés
- [ ] Ouvrir `http://localhost:3001` dans le navigateur
- [ ] Se connecter avec vos identifiants

---

## 🎯 Ports Utilisés

| Service | Port | URL |
|---------|------|-----|
| **Backend Django** | 8000 | http://localhost:8000 |
| **Frontend Vite** | 3001 | http://localhost:3001 |
| **Frontend Vite (alt)** | 5173 | http://localhost:5173 |

---

## 📞 En Cas de Problème

Si le problème persiste :

1. **Fermer tous les terminaux**
2. **Redémarrer VS Code** (si vous l'utilisez)
3. **Vérifier les processus** :
   ```bash
   # Windows
   tasklist | findstr python
   tasklist | findstr node
   ```
4. **Tuer les processus si nécessaire** :
   ```bash
   taskkill /F /IM python.exe
   taskkill /F /IM node.exe
   ```
5. **Relancer** les 2 serveurs

---

## ✅ Projet Opérationnel

Une fois les 2 serveurs démarrés, vous devriez pouvoir :

- ✅ Accéder au dashboard
- ✅ Voir la liste des publications
- ✅ Uploader des PDF
- ✅ Créer des factures
- ✅ Gérer les utilisateurs

**Bon développement ! 🚀**

---

**Dernière mise à jour** : 30 juillet 2026  
**Problème résolu** : Network Error (backend non démarré)

