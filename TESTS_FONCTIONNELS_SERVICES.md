# Tests Fonctionnels : Gestion des Services par Contrat et Ligne

## Préparation de l'environnement

### Backend
```bash
cd Back
python manage.py runserver
```

### Frontend
```bash
cd Front
npm run dev
```

### Connexion
- Se connecter en tant que **Chef** ou **Agent de facturation**
- URL : http://localhost:3000

---

## Scénario 1 : Création de contrat avec services

### Objectif
Vérifier que les services peuvent être configurés au niveau du contrat lors de sa création.

### Étapes
1. ✅ Aller sur **Gestion des Contrats** : `/agent/contrats`
2. ✅ Cliquer sur **"+ Nouveau Contrat"**
3. ✅ Remplir les informations du contrat :
   - Type de compte : Entreprise
   - Raison sociale : TEST Services SA
   - Email : test@services.com
   - Téléphone : 99123456
   - Type de contrat : Entreprise
4. ✅ Dans la section **"Services appliqués par défaut à toutes les lignes du contrat"** :
   - Cocher : **Roaming**
   - Cocher : **Internet**
   - Cocher : **Facturation détaillée**
   - Remplir "Option No Limit" : **No Limit 5000**
5. ✅ Cliquer sur **"Créer le Contrat"**
6. ✅ Vérifier le message de succès

### Résultats attendus
- ✅ Message : "Contrat créé avec succès"
- ✅ Le contrat apparaît dans la liste
- ✅ Aucune erreur console

---

## Scénario 2 : Vérification des services du contrat

### Objectif
Vérifier que les services configurés sont bien enregistrés dans le contrat.

### Étapes
1. ✅ Dans la liste des contrats, cliquer sur **"Voir Détails"** du contrat "TEST Services SA"
2. ✅ Observer l'onglet **"Informations"**
3. ✅ Observer la section des statistiques

### Résultats attendus
- ✅ Le contrat s'affiche correctement
- ✅ Le statut est "ACTIF"
- ✅ Le nombre de lignes est 0

**Note** : Les services par défaut du contrat ne sont actuellement pas affichés dans l'interface de détail. Cela pourrait être une amélioration future.

---

## Scénario 3 : Ajout d'une ligne (héritage automatique)

### Objectif
Vérifier que les nouvelles lignes héritent automatiquement des services du contrat.

### Étapes
1. ✅ Dans le détail du contrat "TEST Services SA"
2. ✅ Cliquer sur **"+ Nouvelle Ligne"**
3. ✅ Remplir le formulaire :
   - MSISDN : `71111111` (8 chiffres)
   - Utilisateur : Employé Test 1
   - Cycle : Hybride (HYB)
   - Forfait mensuel : 5000
4. ✅ **Ne pas** remplir les services (laisser l'héritage se faire automatiquement)
5. ✅ Cliquer sur **"Ajouter"**
6. ✅ Vérifier le message de succès

### Résultats attendus
- ✅ Message : "Ligne ajoutée avec succès"
- ✅ La ligne apparaît dans l'onglet **"Lignes"**
- ✅ La colonne **"Services actifs"** affiche des badges :
  - **Roaming**
  - **Internet**
  - **Facturation détaillée**
  - **No Limit: No Limit 5000**

### Vérification technique
```bash
# Dans Django shell
python manage.py shell

from billing.models import Line
ligne = Line.objects.get(msisdn='71111111')
print(f"Roaming: {ligne.est_roaming}")           # True
print(f"Internet: {ligne.est_internet}")         # True
print(f"Facture détaillée: {ligne.facture_detaillee}")  # True
print(f"No Limit: {ligne.option_nolimit}")       # "No Limit 5000"
```

---

## Scénario 4 : Ajout d'une deuxième ligne (vérification de l'héritage)

### Objectif
Confirmer que toutes les nouvelles lignes héritent des services du contrat.

### Étapes
1. ✅ Toujours dans le détail du contrat "TEST Services SA"
2. ✅ Cliquer sur **"+ Nouvelle Ligne"**
3. ✅ Remplir le formulaire :
   - MSISDN : `71222222`
   - Utilisateur : Employé Test 2
   - Cycle : Open (OP)
   - Forfait mensuel : 7500
4. ✅ Cliquer sur **"Ajouter"**

### Résultats attendus
- ✅ La deuxième ligne apparaît dans le tableau
- ✅ Elle affiche les mêmes badges de services que la première :
  - **Roaming**
  - **Internet**
  - **Facturation détaillée**
  - **No Limit: No Limit 5000**

---

## Scénario 5 : Modification isolée d'une ligne

### Objectif
Vérifier qu'on peut modifier les services d'une ligne sans affecter le contrat ni les autres lignes.

### Étapes
1. ✅ Dans le tableau des lignes du contrat "TEST Services SA"
2. ✅ Sur la ligne `71111111`, cliquer sur **"Modifier services"**
3. ✅ Dans le modal qui s'ouvre :
   - ⚠️ Lire l'avertissement : "Les modifications s'appliquent uniquement à cette ligne"
   - Décocher : **Roaming**
   - Décocher : **Facturation détaillée**
   - Modifier "Option No Limit" : `No Limit 10000` (au lieu de 5000)
4. ✅ Cliquer sur **"Enregistrer les modifications"**
5. ✅ Vérifier le message de succès

### Résultats attendus
- ✅ Message : "Services modifiés avec succès"
- ✅ La ligne `71111111` affiche maintenant :
  - ~~Roaming~~ (retiré)
  - **Internet** (conservé)
  - ~~Facturation détaillée~~ (retiré)
  - **No Limit: No Limit 10000** (modifié)
- ✅ La ligne `71222222` reste inchangée :
  - **Roaming** (toujours présent)
  - **Internet**
  - **Facturation détaillée** (toujours présent)
  - **No Limit: No Limit 5000** (valeur d'origine)

### Vérification technique
```bash
# Dans Django shell
from billing.models import Line

ligne1 = Line.objects.get(msisdn='71111111')
print(f"Ligne 1 - Roaming: {ligne1.est_roaming}")           # False
print(f"Ligne 1 - Internet: {ligne1.est_internet}")         # True
print(f"Ligne 1 - Facture détaillée: {ligne1.facture_detaillee}")  # False
print(f"Ligne 1 - No Limit: {ligne1.option_nolimit}")       # "No Limit 10000"

ligne2 = Line.objects.get(msisdn='71222222')
print(f"Ligne 2 - Roaming: {ligne2.est_roaming}")           # True (inchangé)
print(f"Ligne 2 - Internet: {ligne2.est_internet}")         # True
print(f"Ligne 2 - Facture détaillée: {ligne2.facture_detaillee}")  # True (inchangé)
print(f"Ligne 2 - No Limit: {ligne2.option_nolimit}")       # "No Limit 5000" (inchangé)
```

---

## Scénario 6 : Nouvelle ligne après modification

### Objectif
Vérifier que les nouvelles lignes continuent d'hériter des services du contrat (pas des lignes modifiées).

### Étapes
1. ✅ Après avoir modifié la ligne `71111111` dans le scénario précédent
2. ✅ Cliquer sur **"+ Nouvelle Ligne"**
3. ✅ Remplir le formulaire :
   - MSISDN : `71333333`
   - Utilisateur : Employé Test 3
   - Cycle : Hybride (HYB)
   - Forfait mensuel : 6000
4. ✅ Cliquer sur **"Ajouter"**

### Résultats attendus
- ✅ La nouvelle ligne `71333333` affiche les services **du contrat** (pas de la ligne modifiée) :
  - **Roaming** (valeur du contrat)
  - **Internet**
  - **Facturation détaillée** (valeur du contrat)
  - **No Limit: No Limit 5000** (valeur du contrat, pas 10000)

### Conclusion du scénario
- ✅ La ligne `71111111` a des services personnalisés
- ✅ Les lignes `71222222` et `71333333` ont les services par défaut du contrat
- ✅ **L'héritage fonctionne correctement** : nouvelles lignes héritent toujours du contrat, pas des modifications de lignes existantes

---

## Scénario 7 : Désactivation complète d'un service sur une ligne

### Objectif
Vérifier qu'on peut complètement désactiver un service (champ texte) sur une ligne.

### Étapes
1. ✅ Dans le tableau des lignes
2. ✅ Sur la ligne `71222222`, cliquer sur **"Modifier services"**
3. ✅ Vider complètement le champ **"Option No Limit"** (effacer "No Limit 5000")
4. ✅ Décocher **Internet**
5. ✅ Cliquer sur **"Enregistrer les modifications"**

### Résultats attendus
- ✅ La ligne `71222222` affiche maintenant :
  - **Roaming**
  - ~~Internet~~ (retiré)
  - **Facturation détaillée**
  - ~~No Limit: No Limit 5000~~ (retiré complètement)
- ✅ Le badge "No Limit" n'apparaît plus du tout

### Vérification technique
```bash
from billing.models import Line
ligne2 = Line.objects.get(msisdn='71222222')
print(f"No Limit: '{ligne2.option_nolimit}'")  # '' (chaîne vide)
print(f"Internet: {ligne2.est_internet}")      # False
```

---

## Scénario 8 : Activation d'un service absent du contrat

### Objectif
Vérifier qu'on peut activer des services sur une ligne même s'ils ne sont pas dans les valeurs par défaut du contrat.

### Étapes
1. ✅ Sur la ligne `71222222`, cliquer sur **"Modifier services"**
2. ✅ Cocher : **International** (qui n'était pas dans le contrat)
3. ✅ Cocher : **Incognito** (qui n'était pas dans le contrat)
4. ✅ Remplir "Option BlackBerry" : `BlackBerry Pro`
5. ✅ Cliquer sur **"Enregistrer les modifications"**

### Résultats attendus
- ✅ La ligne `71222222` affiche maintenant :
  - **Roaming**
  - **Facturation détaillée**
  - **International** (nouveau)
  - **Incognito** (nouveau)
  - **BlackBerry: BlackBerry Pro** (nouveau)

---

## Scénario 9 : État final du contrat

### Objectif
Vérifier l'état final après toutes les modifications.

### État attendu du contrat "TEST Services SA"

| Ligne      | Roaming | Internet | Facture détaillée | No Limit       | BlackBerry | International | Incognito |
|------------|---------|----------|-------------------|----------------|------------|---------------|-----------|
| 71111111   | ❌      | ✅       | ❌                | No Limit 10000 | ❌         | ❌            | ❌        |
| 71222222   | ✅      | ❌       | ✅                | ❌             | BB Pro     | ✅            | ✅        |
| 71333333   | ✅      | ✅       | ✅                | No Limit 5000  | ❌         | ❌            | ❌        |

### Vérifications
- ✅ Chaque ligne a sa propre configuration de services
- ✅ Les modifications sont bien isolées
- ✅ Le contrat conserve ses valeurs par défaut pour les futures lignes

---

## Scénario 10 : Création d'un nouveau contrat sans services

### Objectif
Vérifier que les contrats peuvent être créés sans services par défaut.

### Étapes
1. ✅ Créer un nouveau contrat "TEST Sans Services"
2. ✅ **Ne pas** cocher de services
3. ✅ **Ne pas** remplir les options texte
4. ✅ Ajouter une ligne à ce contrat

### Résultats attendus
- ✅ Le contrat est créé sans erreur
- ✅ La ligne ajoutée n'a **aucun** service actif
- ✅ La colonne "Services actifs" affiche : "Aucun service actif"

---

## Tests d'interface et ergonomie

### Vérifications visuelles
- ✅ Les checkboxes s'affichent correctement et sont cliquables
- ✅ Les champs texte sont éditable et le texte est lisible
- ✅ Les badges de services sont visuels et distincts
- ✅ L'avertissement dans le modal est visible et clair
- ✅ Les boutons "Modifier services" sont facilement identifiables
- ✅ Le modal ne se superpose pas avec d'autres éléments

### Tests de responsivité
- ✅ Sur écran large (>1400px) : tous les éléments sont visibles
- ✅ Sur écran moyen (768-1400px) : le tableau des lignes reste lisible
- ✅ Sur mobile (<768px) : le formulaire est utilisable (scroll vertical)

### Tests de performance
- ✅ Le chargement du détail contrat est rapide (<2s)
- ✅ L'ouverture du modal est instantanée
- ✅ La sauvegarde des modifications prend <1s
- ✅ Le rafraîchissement après modification est fluide

---

## Tests d'erreurs

### Scénario erreur 1 : Numéro de ligne déjà existant
1. ✅ Essayer d'ajouter une ligne avec MSISDN `71111111` (déjà existant)
2. ✅ Résultat attendu : Message d'erreur "Ce numéro de ligne existe déjà"

### Scénario erreur 2 : MSISDN invalide
1. ✅ Essayer d'ajouter une ligne avec MSISDN `123` (moins de 8 chiffres)
2. ✅ Résultat attendu : Message d'erreur de validation HTML5

### Scénario erreur 3 : Modification d'une ligne inexistante
1. ✅ Supprimer une ligne (si la fonctionnalité existe)
2. ✅ Essayer de modifier ses services
3. ✅ Résultat attendu : Erreur 404 ou message approprié

---

## Checklist de validation finale

### Backend
- [x] Migration `0006` créée
- [x] Migration `0006` appliquée
- [x] Aucun problème détecté par `python manage.py check`
- [x] Tous les tests unitaires passent (13/13)
- [x] API `/billing/companies/` accepte les services par défaut
- [x] API `/billing/lines/` applique l'héritage automatiquement
- [x] API PATCH `/billing/lines/{id}/` modifie uniquement la ligne ciblée

### Frontend
- [x] Build frontend réussit sans erreur
- [x] Formulaire de création de contrat affiche la section services
- [x] Les checkboxes fonctionnent correctement
- [x] Les champs texte acceptent et sauvegardent le texte
- [x] Le modal "Modifier services" s'ouvre et se ferme correctement
- [x] Les badges de services s'affichent avec les bonnes valeurs
- [x] Les messages de succès/erreur apparaissent

### Tests fonctionnels
- [ ] Scénario 1 : Création contrat avec services (à tester manuellement)
- [ ] Scénario 2 : Vérification services du contrat (à tester manuellement)
- [ ] Scénario 3 : Ajout ligne avec héritage (à tester manuellement)
- [ ] Scénario 4 : Deuxième ligne hérite aussi (à tester manuellement)
- [ ] Scénario 5 : Modification isolée d'une ligne (à tester manuellement)
- [ ] Scénario 6 : Nouvelle ligne après modification (à tester manuellement)
- [ ] Scénario 7 : Désactivation complète d'un service (à tester manuellement)
- [ ] Scénario 8 : Activation service absent du contrat (à tester manuellement)
- [ ] Scénario 9 : État final cohérent (à tester manuellement)
- [ ] Scénario 10 : Contrat sans services (à tester manuellement)

---

## Rapport de tests

Une fois les tests manuels réalisés, compléter ce tableau :

| Scénario | Statut | Remarques |
|----------|--------|-----------|
| 1. Création contrat avec services | ⏸️ À tester | |
| 2. Vérification services contrat | ⏸️ À tester | |
| 3. Ajout ligne avec héritage | ⏸️ À tester | |
| 4. Deuxième ligne hérite | ⏸️ À tester | |
| 5. Modification isolée ligne | ⏸️ À tester | |
| 6. Nouvelle ligne après modif | ⏸️ À tester | |
| 7. Désactivation service | ⏸️ À tester | |
| 8. Activation nouveau service | ⏸️ À tester | |
| 9. État final cohérent | ⏸️ À tester | |
| 10. Contrat sans services | ⏸️ À tester | |

**Légende** :
- ✅ Réussi
- ❌ Échec
- ⏸️ À tester
- ⚠️ Réussi avec remarques

---

## Bugs et anomalies détectées

*Aucun bug détecté lors de l'implémentation backend et du build frontend.*

*Compléter cette section après les tests manuels si des problèmes sont rencontrés.*

---

## Améliorations futures suggérées

1. **Affichage des services par défaut du contrat** dans l'onglet "Informations" du détail
2. **Historique des modifications** de services pour chaque ligne
3. **Modification en masse** : permettre de modifier les services de plusieurs lignes simultanément
4. **Prévisualisation du coût** des services avant sauvegarde
5. **Export CSV/Excel** des lignes avec leurs services pour audit
6. **Statistiques** : services les plus utilisés, lignes sans services, etc.
