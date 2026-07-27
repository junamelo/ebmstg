# 🚀 Démarrage rapide - Simulation double type

## ⚡ Lancer le projet en 3 étapes

### Étape 1 : Backend Django
```bash
cd "c:\Users\Benoit\Documents\BURRO\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026\Back"
python manage.py runserver
```

**Résultat attendu :**
```
Django version X.X.X, using settings 'moov_backend.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

---

### Étape 2 : Frontend React
```bash
cd "c:\Users\Benoit\Documents\BURRO\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026\Front"
npm start
```

**Résultat attendu :**
```
Compiled successfully!

You can now view portail-moov-factures in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.X.X:3000
```

---

### Étape 3 : Tester la simulation

1. **Ouvrir le navigateur** : `http://localhost:3000`

2. **Se connecter** (si nécessaire) :
   - Username : `admin` (ou votre compte)
   - Password : votre mot de passe

3. **Accéder à la simulation** :
   - Dans la sidebar, cliquer sur "Simulation"
   - Ou directement : `http://localhost:3000/simulation`

4. **Tester les 2 modes** :
   
   **Mode HYBRIDE :**
   - Cliquer sur "Client HYBRIDE"
   - Ouvrir l'accordéon "Services"
   - Sélectionner 2-3 services
   - Cliquer sur "Calculer l'estimation"
   - Observer le résultat
   
   **Mode OPEN :**
   - Cliquer sur "← Changer de type"
   - Cliquer sur "Client OPEN (Postpayé)"
   - Entrer : `120` minutes, `50` SMS, `5` Go
   - Observer les aperçus en temps réel (orange)
   - Optionnel : ajouter des services
   - Cliquer sur "Calculer l'estimation"
   - Observer la répartition détaillée

---

## 🎯 Points clés à vérifier

### ✅ Écran de sélection
- [ ] 2 cartes visibles (HYBRIDE et OPEN)
- [ ] Animation au survol (élévation + rotation icône)
- [ ] Fond devient bleu pour HYB, orange pour OP

### ✅ Simulation HYBRIDE
- [ ] Accordéon des services fonctionne
- [ ] Badge "X sélectionné(s)" s'affiche
- [ ] Résultat liste les services + total
- [ ] Note explicative affichée

### ✅ Simulation OPEN
- [ ] Tarifs unitaires affichés en haut (50, 25, 1000 FCFA)
- [ ] Aperçu orange sous chaque champ de saisie
- [ ] Total global (orange) se met à jour en temps réel
- [ ] Résultat détaille : Appels + SMS + Data + Services
- [ ] Note explicative différente de HYBRIDE

### ✅ Navigation
- [ ] Bouton "← Changer de type" retourne à la sélection
- [ ] Bouton "Historique" redirige vers `/simulation/historique`
- [ ] Formulaire se réinitialise au changement de type

### ✅ Validation
- [ ] Erreur si HYBRIDE sans service sélectionné
- [ ] Erreur si OPEN sans consommation ni service
- [ ] Bouton "Réinitialiser" vide tout

---

## 📊 Données de test

### Tarifs actuels (mock)
```
Voix :  25 FCFA/minute
SMS  :  10 FCFA/SMS
Data : 2000 FCFA/Go
```

### Services optionnels disponibles
```
Moov Money         :   500 FCFA/mois
Assistance 24/7    : 1 000 FCFA/mois
Package Streaming  : 2 500 FCFA/mois
```

### Exemples de calculs

**HYBRIDE** (uniquement services) :
```
Moov Money + Package Streaming = 500 + 2500 = 3 000 FCFA
```

**OPEN** (consommation + services) :
```
120 min × 25    =  3 000 FCFA
50 SMS × 10     =    500 FCFA
5 Go × 2000     = 10 000 FCFA
Moov Money      =    500 FCFA
                  ──────────
Total           = 14 000 FCFA
```

---

## 🐛 En cas de problème

### Le frontend ne démarre pas
```bash
cd Front
npm install
npm start
```

### Le backend ne démarre pas
```bash
cd Back
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### CORS Error dans la console
Vérifier que `Back/moov_backend/settings.py` contient :
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]
```

### La page Simulation est blanche
1. Ouvrir la console (F12)
2. Vérifier les erreurs JavaScript
3. Vérifier que les tarifs se chargent :
   - Aller dans l'onglet "Network"
   - Recharger la page
   - Chercher un appel à `/tarifs/actifs` ou `/services`

### Les aperçus temps réel ne fonctionnent pas
1. Vérifier que les tarifs sont bien chargés (voir ci-dessus)
2. Ouvrir la console et vérifier qu'il n'y a pas d'erreur JavaScript
3. Vérifier que `tarifs.tarif_minute`, `tarifs.tarif_sms`, `tarifs.tarif_go` existent

---

## 📚 Documentation complète

Pour plus de détails, consulter :
- **`SIMULATION_DOUBLE_TYPE.md`** : Documentation technique complète
- **`TEST_SIMULATION.md`** : Guide de test détaillé avec tous les scénarios
- **`Contexte/CHANGELOG.md`** : Historique des modifications

---

## 🎉 Profitez de la nouvelle simulation !

Vous pouvez maintenant simuler vos factures selon votre type de client :
- **HYBRIDE** : simple et basé sur l'historique
- **OPEN** : détaillé et prévisionnel

Les 2 modes partagent un design moderne et intuitif avec les couleurs Moov. 🔵🟠
