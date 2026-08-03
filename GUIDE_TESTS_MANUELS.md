# Guide de Tests Manuels - Validation Bugs Urgents

## Prérequis

1. **Backend Django lancé :**
   ```bash
   cd Back
   python manage.py runserver
   ```

2. **Frontend React lancé :**
   ```bash
   cd Front
   npm run dev
   ```

3. **Accéder à :** `http://localhost:5173`

---

## Test 1 : AdminDashboard (BUG 5)

### Compte à utiliser
- **Email :** `admin@moov.tg`
- **Mot de passe :** `admin123`

### Scénario 1 : Stats chargées avec succès
1. Se connecter avec le compte admin
2. Aller sur le tableau de bord admin
3. **Vérifier :**
   - ✅ 3 cartes KPI affichent des chiffres (Contrats actifs, Lignes postpayées, Utilisateurs)
   - ✅ Graphique "Publications de factures" s'affiche
   - ✅ Widget "Visiteurs actifs" montre la répartition Desktop/Mobile/Tablette
   - ✅ Tableau "Dernières connexions" affiche les connexions récentes
   - ✅ Aucune erreur dans la console navigateur

### Scénario 2 : API stats échoue (simulation)
1. **Arrêter temporairement le backend Django**
2. Rafraîchir la page AdminDashboard
3. **Vérifier :**
   - ✅ Message d'erreur s'affiche : "Erreur de chargement"
   - ✅ Texte explicatif : "Les statistiques ne sont pas disponibles"
   - ✅ Bouton "Réessayer" visible
4. **Relancer le backend**
5. Cliquer sur "Réessayer"
6. **Vérifier :**
   - ✅ Stats se rechargent correctement
   - ✅ Dashboard affiche normalement

### Résultat attendu
- ✅ Aucun écran blanc
- ✅ Gestion d'erreur propre avec possibilité de réessayer
- ✅ Valeurs par défaut (0) si certaines stats sont null

---

## Test 2 : Gestion Forfaits (BUG 2)

### Compte à utiliser
- **Email :** `agent@moov.tg`
- **Mot de passe :** `agent123`

### Scénario : Afficher et gérer les forfaits
1. Se connecter avec le compte agent
2. Aller sur `/agent/forfaits`
3. **Vérifier :**
   - ✅ Liste des forfaits (packages) s'affiche
   - ✅ Chaque forfait montre : nom, code, prix mensuel, quotas
   - ✅ Badges "Actif" / "Inactif" visibles
   - ✅ Boutons "Modifier" et toggle actif/inactif fonctionnent

4. **Créer un nouveau forfait :**
   - Cliquer "Nouveau Forfait"
   - Remplir : Nom "Test Forfait", Code "TEST01", Prix 5000
   - Soumettre
   - **Vérifier :** forfait apparaît dans la liste

5. **Désactiver un forfait :**
   - Cliquer sur le toggle d'un forfait actif
   - **Vérifier :** badge passe à "Inactif"

### Résultat attendu
- ✅ Page `/agent/forfaits` affiche bien les **forfaits** (pas les services)
- ✅ CRUD complet fonctionnel
- ✅ État vide géré si aucun forfait

---

## Test 3 : Ajout de Ligne dans Contrat (BUG 3)

### Compte à utiliser
- **Email :** `agent@moov.tg`
- **Mot de passe :** `agent123`

### Scénario 1 : Ajouter une ligne valide
1. Se connecter avec le compte agent
2. Aller sur `/agent/contrats`
3. Cliquer sur un contrat existant
4. Dans l'onglet "Lignes", cliquer "Nouvelle Ligne"
5. **Remplir le formulaire :**
   - MSISDN : `99123456` (nouveau numéro)
   - Utilisateur : `Test User`
   - Cycle : `HYB`
   - Forfait : `0`
6. Soumettre
7. **Vérifier :**
   - ✅ Message "Ligne ajoutée avec succès"
   - ✅ Modal se ferme
   - ✅ Nouvelle ligne apparaît dans la liste

### Scénario 2 : MSISDN déjà existant
1. Cliquer à nouveau sur "Nouvelle Ligne"
2. Entrer le même MSISDN que précédemment
3. Soumettre
4. **Vérifier :**
   - ✅ Message d'erreur clair : "Ce numéro de ligne existe déjà"
   - ✅ Modal reste ouverte pour correction

### Scénario 3 : Affectation employé
1. Sur une ligne sans employé, cliquer "Affecter un employé"
2. **Vérifier :**
   - ✅ Liste affiche uniquement les utilisateurs avec role=EMPLOYE
   - ✅ Pas de payeurs, agents ou admins dans la liste
3. Sélectionner un employé
4. **Vérifier :**
   - ✅ Message "Employé affecté avec succès"
   - ✅ Nom de l'employé apparaît sur la ligne

### Résultat attendu
- ✅ Formulaire ajout ligne envoie les bons champs au backend
- ✅ Validation MSISDN unique fonctionne
- ✅ Affectation limitée aux employés uniquement
- ✅ Messages d'erreur clairs et visibles

---

## Test 4 : Simulation Employé (BUG 4)

### Compte à utiliser
- **Email :** `99475555`
- **Mot de passe :** `employe123`

### Scénario 1 : Simulation HYBRIDE
1. Se connecter avec le compte employé
2. Aller sur `/simulation`
3. **Vérifier :**
   - ✅ Écran de sélection affiche 2 cartes : HYBRIDE et OPEN
4. Cliquer sur "Client HYBRIDE"
5. **Vérifier :**
   - ✅ Page affiche "Simulation de facturation - Client HYBRIDE"
   - ✅ Section "Services optionnels" s'affiche
   - ✅ Si services existent : accordéon avec liste de services
   - ✅ Si aucun service : message "Aucun service optionnel disponible pour le moment"

6. **Si services disponibles :**
   - Ouvrir l'accordéon "Services"
   - Sélectionner un service et une option
   - **Vérifier :**
     - ✅ Badge "X sélectionné(s)" apparaît
     - ✅ Prix s'affiche à côté de l'option
   - Cliquer "Calculer l'estimation"
   - **Vérifier :**
     - ✅ Carte "Résultat" affiche le montant total
     - ✅ Détail des services choisis visible

### Scénario 2 : Simulation OPEN
1. Depuis la page simulation, cliquer "Changer de type"
2. Sélectionner "Client OPEN"
3. **Remplir les champs :**
   - Minutes d'appel : `120`
   - Nombre de SMS : `50`
   - Volume data (Go) : `5`
4. **Vérifier :**
   - ✅ Montants estimés s'affichent sous chaque champ en temps réel
5. Ajouter un service optionnel (si disponible)
6. Cliquer "Calculer l'estimation"
7. **Vérifier :**
   - ✅ Résultat détaille : Appels, SMS, Data, Services
   - ✅ Montant total calculé = somme des 4 composantes
   - ✅ Note explicative en bas du résultat

### Résultat attendu
- ✅ Services chargés depuis l'API réelle
- ✅ Format des données correctement adapté (tarifs → options)
- ✅ État vide géré si aucun service
- ✅ Calcul simulation fonctionnel pour HYBRIDE et OPEN
- ✅ Pas d'erreur console liée aux données mock

---

## Test 5 : Connexion et Rôles (BUG 1)

### Scénario : Tester tous les comptes

#### 5.1 Compte Chef
- **Identifiant :** `chef@moov.tg`
- **Mot de passe :** `chef123`
- **Vérifier :**
  - ✅ Connexion réussie
  - ✅ Accès au menu chef de facturation
  - ✅ Peut publier des factures

#### 5.2 Compte Payeur
- **Identifiant :** `A26TEST001`
- **Mot de passe :** `payeur123`
- **Vérifier :**
  - ✅ Connexion réussie
  - ✅ Voit uniquement son entreprise
  - ✅ Voit uniquement les factures PUBLIEE de son entreprise

#### 5.3 Compte Employé
- **Identifiant :** `99475555`
- **Mot de passe :** `employe123`
- **Vérifier :**
  - ✅ Connexion réussie
  - ✅ Voit uniquement ses lignes affectées
  - ✅ Voit uniquement ses factures PUBLIEE
  - ✅ Accès à la simulation

### Résultat attendu
- ✅ Tous les comptes de test fonctionnent
- ✅ Filtrages par rôle opérationnels
- ✅ Pas de faux identifiants affichés

---

## Checklist Globale

### Backend
- [x] `python manage.py check` : 0 erreur
- [x] `python manage.py test` : 97 tests OK
- [ ] Serveur Django lancé sans erreur

### Frontend
- [x] `npm run build` : Build réussi
- [ ] Serveur dev lancé sans erreur
- [ ] Aucune erreur console au chargement

### Tests Manuels
- [ ] BUG 1 : Connexion avec les 5 rôles fonctionne
- [ ] BUG 2 : Page forfaits affiche les données API
- [ ] BUG 3 : Ajout ligne et affectation employé fonctionnent
- [ ] BUG 4 : Simulation charge services API (HYBRIDE + OPEN)
- [ ] BUG 5 : AdminDashboard gère stats null proprement

---

## En Cas d'Erreur

### Erreur "Network Error" ou "500"
- Vérifier que le backend Django est lancé (`python manage.py runserver`)
- Vérifier l'URL de l'API dans `Front/src/services/api.js`
- Vérifier les logs Django dans le terminal

### Erreur "401 Unauthorized"
- Vérifier que le token est bien stocké dans localStorage
- Se déconnecter et se reconnecter
- Vérifier les permissions dans `Back/billing/views.py`

### Services/Forfaits vides
- Vérifier qu'il existe des données en base :
  ```bash
  python manage.py shell
  >>> from billing.models import Service, Package
  >>> Service.objects.filter(est_actif=True).count()
  >>> Package.objects.filter(est_actif=True).count()
  ```
- Si vide, créer des données de test via l'interface admin Django

### Stats admin null
- Vérifier l'endpoint `/api/billing/stats/admin/` dans le navigateur
- Vérifier les logs backend pour voir les erreurs
- Vérifier que des données existent (Company, Line, User)

---

## Validation Finale

**Tous les bugs sont considérés résolus si :**
1. ✅ Aucune erreur dans les tests Django (97/97)
2. ✅ Build frontend réussi sans erreur
3. ✅ Les 5 scénarios de tests manuels passent
4. ✅ Aucune régression constatée sur les fonctionnalités existantes

**Si un test manuel échoue :**
- Noter précisément l'erreur (message, console, network)
- Vérifier les logs backend
- Rapporter le problème avec les étapes de reproduction
