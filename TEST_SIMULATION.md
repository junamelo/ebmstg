# 🧪 Guide de test - Simulation double type

## Prérequis

1. **Backend Django** doit tourner sur `http://localhost:8000`
   ```bash
   cd Back
   python manage.py runserver
   ```

2. **Frontend React** doit tourner sur `http://localhost:3000`
   ```bash
   cd Front
   npm start
   ```

---

## Test 1 : Écran de sélection du type de client

### Actions
1. Ouvrir `http://localhost:3000/simulation`
2. Observer l'écran de sélection

### Résultats attendus
- ✅ 2 grandes cartes visibles : "Client HYBRIDE" et "Client OPEN"
- ✅ Icônes distinctives (cube pour HYB, dollar pour OP)
- ✅ Au survol : carte s'élève + icône tourne légèrement
- ✅ Fond devient bleu pour HYB, orange pour OP
- ✅ Badge en bas de chaque carte indique le type de facturation

### Capture d'écran
```
┌──────────────────────────────────────────────────────────────┐
│  🎯 Simulation de facturation                                │
│  Choisissez d'abord votre type de client                     │
│                                                               │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │  📦  HYBRIDE     │      │  💰  OPEN        │            │
│  │                  │      │                  │            │
│  │  Basé sur        │      │  Prévisionnel    │            │
│  │  l'historique    │      │  Manuel          │            │
│  └──────────────────┘      └──────────────────┘            │
└──────────────────────────────────────────────────────────────┘
```

---

## Test 2 : Simulation HYBRIDE

### Actions
1. Cliquer sur "Client HYBRIDE"
2. Observer le formulaire
3. Ouvrir l'accordéon "Services"
4. Sélectionner "Moov Money" (500 FCFA/mois)
5. Sélectionner "Package Streaming" (2500 FCFA/mois)
6. Observer le badge "2 sélectionnés"
7. Cliquer sur "Calculer l'estimation"

### Résultats attendus
- ✅ En-tête affiche "Simulation de facturation - Client HYBRIDE"
- ✅ Bouton "← Changer de type" visible en haut à droite
- ✅ Accordéon "Services" s'ouvre/ferme au clic
- ✅ Badge affiche "2 sélectionnés"
- ✅ Résultat affiché :
  * Moov Money : 500 FCFA
  * Package Streaming : 2 500 FCFA
  * **Montant total estimé : 3 000 FCFA**
- ✅ Note : "Cette simulation est basée sur votre consommation réelle passée..."

### Test de réinitialisation
1. Cliquer sur "Réinitialiser"
2. Vérifier que tous les services sont désélectionnés
3. Vérifier que le résultat disparaît

### Test de changement de type
1. Cliquer sur "← Changer de type"
2. Vérifier le retour à l'écran de sélection
3. Vérifier que le formulaire est réinitialisé

---

## Test 3 : Simulation OPEN - Calcul temps réel

### Actions
1. Depuis l'écran de sélection, cliquer sur "Client OPEN (Postpayé)"
2. Observer le formulaire

### Résultats attendus
- ✅ En-tête affiche "Simulation de facturation - Client OPEN"
- ✅ Encadré "Tarifs unitaires en vigueur" visible :
  * Appel : 50 FCFA/min
  * SMS : 25 FCFA/SMS
  * Data : 1 000 FCFA/Go
- ✅ 3 champs de saisie visibles

### Test de l'aperçu temps réel
1. Entrer dans "Minutes d'appel prévues" : `120`
   - ✅ Aperçu orange s'affiche : `≈ 6 000 FCFA`

2. Entrer dans "Nombre de SMS prévus" : `50`
   - ✅ Aperçu orange s'affiche : `≈ 1 250 FCFA`

3. Entrer dans "Volume de data prévu" : `5`
   - ✅ Aperçu orange s'affiche : `≈ 5 000 FCFA`

4. Observer l'encadré "Montant estimé" en bas (orange)
   - ✅ Affiche : `12 250 FCFA`
   - ✅ Se met à jour instantanément quand on change les valeurs

### Test avec services optionnels
1. Ouvrir l'accordéon "Services optionnels"
2. Sélectionner "Moov Money" (500 FCFA/mois)
3. Observer l'encadré "Montant estimé"
   - ✅ Affiche maintenant : `12 750 FCFA` (12 250 + 500)

---

## Test 4 : Simulation OPEN - Résultat détaillé

### Actions
1. Avec les valeurs : 120 min, 50 SMS, 5 Go, + Moov Money
2. Cliquer sur "Calculer l'estimation"

### Résultats attendus
- ✅ Résultat affiché avec répartition :
  * Appels (120 min) : 6 000 FCFA
  * SMS (50 SMS) : 1 250 FCFA
  * Data (5 Go) : 5 000 FCFA
  * Moov Money : 500 FCFA
  * ─────────────────────────
  * **Montant total estimé : 12 750 FCFA**
- ✅ Note : "Cette simulation est basée sur vos prévisions de consommation..."

---

## Test 5 : Validation des formulaires

### Test HYBRIDE - Sans sélection
1. Aller sur simulation HYBRIDE
2. Ne rien sélectionner
3. Cliquer sur "Calculer l'estimation"
4. ✅ Erreur rouge : "Veuillez sélectionner au moins un service."

### Test OPEN - Formulaire vide
1. Aller sur simulation OPEN
2. Ne rien remplir
3. Cliquer sur "Calculer l'estimation"
4. ✅ Erreur rouge : "Veuillez entrer au moins une consommation prévue ou sélectionner un service."

### Test OPEN - Uniquement services
1. Ne rien remplir dans les champs de consommation
2. Sélectionner uniquement "Moov Money"
3. Cliquer sur "Calculer l'estimation"
4. ✅ Résultat affiché avec uniquement Moov Money : 500 FCFA

---

## Test 6 : Responsive mobile

### Actions
1. Ouvrir les outils de développement (F12)
2. Activer le mode responsive
3. Choisir "iPhone 12 Pro" ou largeur 375px

### Résultats attendus
- ✅ Écran de sélection : 2 cartes passent en 1 colonne
- ✅ Illustration disparaît (affichage simplifié)
- ✅ Formulaire prend toute la largeur
- ✅ Boutons "Changer de type" et "Historique" passent en colonne
- ✅ Accordéons restent fonctionnels
- ✅ Texte reste lisible

---

## Test 7 : Navigation et persistance

### Test du bouton "Changer de type"
1. Aller sur simulation HYBRIDE
2. Sélectionner 2 services
3. Cliquer sur "← Changer de type"
4. ✅ Retour à l'écran de sélection
5. Recliquer sur "Client HYBRIDE"
6. ✅ Formulaire est réinitialisé (services désélectionnés)

### Test du bouton "Historique"
1. Cliquer sur le bouton "Historique"
2. ✅ Redirection vers `/simulation/historique`

---

## Test 8 : Performance et fluidité

### Actions
1. Aller sur simulation OPEN
2. Taper rapidement des valeurs dans les 3 champs

### Résultats attendus
- ✅ Aperçus se mettent à jour sans lag
- ✅ Total global se met à jour instantanément
- ✅ Pas de scintillement
- ✅ Pas de recalcul visible

---

## Test 9 : Accessibilité

### Test clavier
1. Utiliser uniquement la touche `Tab` pour naviguer
2. ✅ Focus visible sur chaque élément interactif
3. ✅ Ordre de tabulation logique
4. Appuyer sur `Entrée` sur une carte de sélection
5. ✅ Sélection du type fonctionne

### Test contraste
1. Vérifier les textes sur fond clair
2. ✅ Contraste suffisant (ratio > 4.5:1)
3. Vérifier les boutons
4. ✅ Texte blanc sur bleu/orange lisible

---

## Checklist complète

### Fonctionnel
- [ ] Écran de sélection s'affiche correctement
- [ ] Animations de survol fluides
- [ ] Simulation HYBRIDE : sélection de services
- [ ] Simulation HYBRIDE : calcul et affichage du résultat
- [ ] Simulation OPEN : affichage des tarifs unitaires
- [ ] Simulation OPEN : aperçu temps réel sous chaque champ
- [ ] Simulation OPEN : total global temps réel (orange)
- [ ] Simulation OPEN : calcul détaillé et répartition
- [ ] Validation : erreurs affichées si formulaire vide
- [ ] Réinitialisation fonctionne
- [ ] Changement de type réinitialise le formulaire
- [ ] Bouton "Historique" redirige correctement

### Design
- [ ] Couleurs Moov respectées (bleu #002a7a, orange #e05500)
- [ ] Typographie cohérente
- [ ] Espacements harmonieux
- [ ] Icônes claires et significatives
- [ ] Badges visibles et informatifs

### Responsive
- [ ] Desktop : 2 colonnes (illustration + formulaire)
- [ ] Mobile : 1 colonne (illustration masquée)
- [ ] Cartes de sélection : 2 colonnes → 1 colonne
- [ ] Texte reste lisible sur petits écrans

### Performance
- [ ] Pas de lag lors de la saisie
- [ ] Calculs temps réel instantanés
- [ ] Transitions fluides (< 300ms)
- [ ] Pas de re-render inutile

### Accessibilité
- [ ] Navigation clavier complète
- [ ] Focus visible
- [ ] Contraste suffisant
- [ ] Labels présents sur tous les champs

---

## 🐛 Bugs connus

Aucun bug connu pour le moment.

---

## 📞 Contact

En cas de problème, contacter l'équipe de développement.
