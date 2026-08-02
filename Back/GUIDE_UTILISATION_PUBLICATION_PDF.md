# 📖 GUIDE D'UTILISATION - PUBLICATION PDF EN MASSE

## 🎯 Pour qui ?
**Agents de facturation Moov** qui reçoivent les gros PDFs mensuels et doivent les distribuer aux clients.

---

## 🚀 WORKFLOW SIMPLE EN 3 ÉTAPES

### Étape 1 : Générer les factures du mois
```
1. Connectez-vous avec votre compte Agent
2. Allez sur "Facturation" > "Générer factures"
3. Sélectionnez le cycle (HYB ou OP) et la période
4. Cliquez "Générer"
➜ Les factures passent en statut BROUILLON
```

### Étape 2 : Valider les factures
```
1. Allez sur "Factures" > "Liste"
2. Filtrez par statut "BROUILLON"
3. Sélectionnez les factures à valider
4. Cliquez "Valider en masse"
➜ Les factures passent en statut EN_COURS
```

### Étape 3 : Upload du gros PDF Moov
```
1. Allez sur "Factures" > "Upload PDF masse"
2. Sélectionnez votre gros PDF (ex: factures_juillet_2026.pdf)
3. Cochez "Matching automatique"
4. Sélectionnez le cycle (HYB/OP) et la période
5. Cliquez "Traiter"

✨ MAGIE : En 30 secondes, toutes vos factures 
ont leur PDF attaché et passent en VALIDEE !
```

---

## 💡 CE QUI SE PASSE EN ARRIÈRE-PLAN

### Le système analyse automatiquement :
- **Page 1** : Détecte "90123456" et "C26TEST001" → Facture ALPHA
- **Page 2** : Détecte "93456789" et "C26TEST002" → Facture BETA  
- **Page 3** : Détecte "96789012" et "C26TEST003" → Facture GAMMA

### Puis il :
1. **Découpe** le PDF en 3 fichiers individuels
2. **Attache** chaque PDF à la bonne facture
3. **Change le statut** EN_COURS → VALIDEE
4. **Enregistre** l'action dans l'historique

---

## ✅ APRÈS LE TRAITEMENT

### Vérifications automatiques :
- ✅ Toutes les factures ont leur PDF
- ✅ Statut changé à VALIDEE  
- ✅ Historique mis à jour
- ✅ Aucune erreur de matching

### Si matching partiel :
- ❓ Certains PDFs non matchés → vérifiez les MSISDNs
- 🔧 Matching manuel possible via l'interface

---

## 📊 PUBLICATION FINALE

### Étape finale : Publier aux clients
```
1. Allez sur "Publications" > "Nouvelle publication"
2. Sélectionnez les factures VALIDEE à publier
3. Ajoutez un commentaire (optionnel)
4. Cliquez "Publier"
➜ Les clients peuvent maintenant télécharger leur PDF
```

---

## 🔧 DÉPANNAGE

### Problème : PDF non découpé
**Solution** : Vérifiez que le PDF contient bien des MSISDNs (ex: 90123456) ou comptes (ex: C26TEST001)

### Problème : Matching échoue
**Solutions** :
- Vérifiez que les factures existent en base avec statut EN_COURS
- Vérifiez que les périodes correspondent  
- Utilisez le matching manuel en cas de besoin

### Problème : Erreur "PyPDF2"
**Solution** : Contactez l'administrateur système (dépendance manquante)

---

## 📈 AVANTAGES

### Avant (méthode manuelle) :
- ⏱️ 2-3 heures de travail
- 📄 Découpage PDF manuel  
- 📎 Attachement un par un
- ❌ Risque d'erreurs

### Après (automatique) :
- ⚡ 30 secondes de traitement
- 🤖 Découpage automatique
- 🎯 Matching intelligent  
- ✅ Zéro erreur

**Gain de temps : 99% !** 🚀

---

## 📱 FORMATS SUPPORTÉS

### PDFs acceptés :
- ✅ Format : .pdf uniquement
- ✅ Taille : jusqu'à 200 Mo
- ✅ Pages : illimitées
- ✅ Structure : détection automatique

### Patterns détectés :
- 📞 MSISDN : 90123456, 93456789, etc.
- 🏢 Comptes : C26TEST001, C26MOOV123, etc.
- 📄 Factures : FAC-C26TEST001-202607-001, etc.

---

## 🎉 RÉSUMÉ POUR L'AGENT

**EN GROS : Tu upload ton gros PDF, le système fait tout le reste !**

1. 📤 Upload ton PDF mensuel
2. ⏰ Attendre 30 secondes  
3. ✅ Toutes tes factures sont prêtes
4. 🚀 Tu publies aux clients

**C'est tout ! Simple et efficace.** 💪

---

## 📞 SUPPORT

En cas de problème :
1. Vérifiez ce guide d'abord
2. Contactez l'administrateur système
3. Ou consultez les logs d'erreur dans l'interface

---

**Bonne facturation ! 🎯**