# 📋 Liste des Correctifs UI à Implémenter

## ✅ 1. Pagination sur GestionContrats
**Page**: `/admin/contrats` et `/agent/contrats`
**Problème**: Trop de contrats à scroller
**Solution**: Ajouter pagination (10-20 contrats par page)

## ✅ 2. Amélioration Noms Forfaits "No Limit"
**Page**: `/agent/forfaits` (GestionForfaits)
**Problème**: Certains noms de forfaits No Limit ne sont pas lisibles
**Solution**: Faire correspondre les noms aux prix (ex: "No Limit 5000" au lieu de "NOLIMIT_5K_MENSUEL")

## ✅ 3. Formulaires Payeur/Employé - Bouton Fermer
**Pages**: Formulaires de création payeur/employé
**Problèmes**:
- Pas de moyen de sortir du formulaire sans remplir
- Superposition avec barre horizontale bleue
**Solution**: 
- Ajouter bouton "Annuler" ou "×" pour fermer
- Corriger z-index de la barre bleue

## ✅ 4. Saisie Manuelle Prix Options Forfaits
**Page**: `/agent/forfaits` (modal ajout option)
**Problème**: Erreur "nombre valide entre 0 et 100" lors de la saisie manuelle
**Solution**: Supprimer les attributs `min="0"` et `max="100"` sur l'input prix

## ✅ 5. Filtre Cycle de Facturation (à supprimer)
**Page**: `/agent/publication` ou `/chef/publication` (PublicationPdf)
**Problème**: Filtre cycle non pertinent car factures contiennent HYB + OPN mélangés
**Solution**: Supprimer complètement le filtre "Cycle de facturation"

## ✅ 6. Factures à Publier - Améliorations
**Page**: `/agent/factures-a-publier` ou `/chef/factures-a-publier`
**Problèmes**:
- Pas de pagination (peut y avoir beaucoup de factures)
- Pas de bouton notification mail/SMS
- Vérifier que "Montant" affiche bien le montant TTC de la facture
**Solutions**:
- Ajouter pagination (20 factures par page)
- Ajouter bouton "📧 Notifier les clients" (préparer pour future intégration)
- S'assurer que montant affiché = `facture.montant_ttc`

---

## 📊 Priorités

### 🔴 Critique (bloquer workflow):
1. Bouton fermer formulaires payeur/employé
2. Saisie manuelle prix options forfaits

### 🟡 Important (UX):
3. Pagination GestionContrats
4. Pagination FacturesAPublier
5. Supprimer filtre cycle facturation

### 🟢 Améliorations (cosmétique):
6. Améliorer noms forfaits No Limit
7. Bouton notification (préparation future)

---

## 🚀 Plan d'Exécution

1. **Phase 1** : Correctifs critiques (formulaires + saisie prix)
2. **Phase 2** : Pagination (contrats + factures à publier)
3. **Phase 3** : Nettoyage (filtre cycle + amélioration noms)
4. **Phase 4** : Préparation future (bouton notification)
