# 🧹 GUIDE - Réinitialisation des Factures pour Tests

**Date** : 6 août 2026  
**Objectif** : Vider la base de données des factures pour refaire des tests de publication

---

## 🎯 PROBLÈME

Quand vous testez la publication de PDF, le système empêche de publier le même PDF deux fois (pour éviter les doublons).

Pour refaire des tests, vous devez **vider la base de données des factures**.

---

## ✅ SOLUTION : 2 Scripts Créés

### Script 1 : `reset_factures.py` (avec menu)

**Utilisation** :
```bash
cd Back
python reset_factures.py
```

**Fonctionnalités** :
- ✅ Menu interactif
- ✅ Affiche les statistiques avant/après
- ✅ Demande confirmation (tape "OUI")
- ✅ Supprime tout proprement

**Avantages** :
- Sécurisé (confirmation requise)
- Informatif (stats complètes)
- Recommandé pour la première fois

---

### Script 2 : `reset_factures_rapide.py` (sans confirmation)

**Utilisation** :
```bash
cd Back
python reset_factures_rapide.py
```

**Fonctionnalités** :
- ⚡ Suppression immédiate (sans confirmation !)
- ⚡ Très rapide
- ⚡ Parfait pour tests répétés

**Avantages** :
- Ultra rapide
- Pas de questions
- Pour utilisateurs avertis

---

## 🗑️ CE QUI EST SUPPRIMÉ

### ❌ Supprimé

1. **Toutes les factures** (`Invoice`)
2. **Toutes les notifications** (`NotificationFacture`)
3. **Tout l'historique de facturation** (`HistoriqueFacturation`)
4. **Toutes les publications** (`Publication`)
5. **Tous les fichiers PDF** (dossiers `media/factures/` et `media/publications/`)

### ✅ Préservé

1. **Utilisateurs** (`User`)
2. **Contrats** (`Company`)
3. **Lignes téléphoniques** (`Line`)
4. **Commerciaux** (`Commercial`)
5. **Forfaits et services** (`Package`, `Service`)
6. **Audit des contrats** (`AuditContrat`)

---

## 📝 ÉTAPES D'UTILISATION

### Méthode 1 : Avec menu (recommandé)

```bash
# 1. Aller dans le dossier Back
cd "c:\Users\Benoit\Documents\BURRO\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026\Back"

# 2. Lancer le script
python reset_factures.py

# 3. Choisir l'action
# Taper "1" puis Entrée

# 4. Confirmer
# Taper "OUI" en majuscules puis Entrée

# 5. Résultat affiché
```

**Sortie attendue** :
```
======================================================================
🧹 NETTOYAGE DE LA BASE DE DONNÉES - FACTURES
======================================================================

📊 Éléments à supprimer :
   - Factures : 145
   - Notifications : 23
   - Historique facturation : 98
   - Publications : 12

⚠️  ATTENTION : Cette action est IRRÉVERSIBLE !

Taper 'OUI' en majuscules pour confirmer : OUI

🗑️  Suppression en cours...

1️⃣  Suppression des fichiers PDF...
   ✅ 145 fichier(s) PDF supprimé(s)
   ✅ 12 fichier(s) de publication supprimé(s)

2️⃣  Suppression des notifications...
   ✅ 23 notification(s) supprimée(s)

3️⃣  Suppression de l'historique de facturation...
   ✅ 98 entrée(s) d'historique supprimée(s)

4️⃣  Suppression des publications...
   ✅ 12 publication(s) supprimée(s)

5️⃣  Suppression des factures...
   ✅ 145 facture(s) supprimée(s)

======================================================================
✅ NETTOYAGE TERMINÉ
======================================================================

📋 Résumé :
   ✅ 145 facture(s) supprimée(s)
   ✅ 23 notification(s) supprimée(s)
   ✅ 98 historique(s) supprimé(s)
   ✅ 12 publication(s) supprimée(s)
   ✅ Fichiers PDF supprimés

✨ Vous pouvez maintenant refaire vos tests de publication !
```

---

### Méthode 2 : Rapide (sans confirmation)

```bash
# 1. Aller dans le dossier Back
cd "c:\Users\Benoit\Documents\BURRO\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026\Back"

# 2. Lancer le script rapide
python reset_factures_rapide.py
```

**Sortie attendue** :
```
🗑️  Suppression rapide des factures...
✅ Supprimé : 145 factures, 23 notifications
✅ Prêt pour de nouveaux tests !
```

---

## 🔄 WORKFLOW COMPLET DE TEST

### 1. Vider la base

```bash
cd Back
python reset_factures_rapide.py
```

### 2. Uploader des PDFs

- Aller sur l'interface web
- Se connecter en tant qu'agent
- Aller dans "Factures à publier"
- Uploader vos PDFs de test

### 3. Tester la publication

- Vérifier le traitement
- Vérifier les factures créées
- Vérifier les notifications

### 4. Répéter si nécessaire

Si vous voulez refaire un test :
```bash
python reset_factures_rapide.py
```

---

## 💡 CONSEILS

### Quand utiliser le script ?

✅ **À utiliser** :
- Avant de refaire des tests de publication
- Quand vous avez des doublons de PDFs
- Pour repartir sur une base propre
- En développement/test uniquement

❌ **Ne PAS utiliser** :
- En production (données réelles !)
- Si vous voulez garder l'historique
- Sans backup si données importantes

---

### Backup avant suppression (optionnel)

Si vous voulez sauvegarder les factures avant :

```bash
# Exporter les factures en JSON
python manage.py dumpdata billing.Invoice > backup_invoices.json

# Pour restaurer plus tard
python manage.py loaddata backup_invoices.json
```

---

## 🐛 DÉPANNAGE

### Erreur "Module not found"

**Problème** : Django n'est pas configuré

**Solution** :
```bash
# S'assurer d'être dans le dossier Back
cd Back
python reset_factures.py
```

---

### Erreur "Permission denied" sur les fichiers

**Problème** : Fichiers PDF verrouillés

**Solution** :
1. Fermer tous les PDF ouverts
2. Fermer l'explorateur de fichiers
3. Relancer le script

---

### La base ne se vide pas complètement

**Problème** : Contraintes de clés étrangères

**Solution** : Le script supprime dans le bon ordre. Si ça persiste :
```bash
# Option nucléaire : Supprimer toute la base et recréer
python manage.py flush --no-input
python manage.py migrate
python manage.py createsuperuser
```

⚠️ Attention : Cela supprime TOUT (utilisateurs inclus)

---

## 📊 VÉRIFIER LE RÉSULTAT

### Après le script

```bash
# Vérifier que tout est vide
python manage.py shell
```

```python
from billing.models import Invoice, NotificationFacture, Publication

# Doit afficher 0
print(f"Factures : {Invoice.objects.count()}")
print(f"Notifications : {NotificationFacture.objects.count()}")
print(f"Publications : {Publication.objects.count()}")

# Vérifier que les contrats sont toujours là
from billing.models import Company, Line
print(f"Contrats : {Company.objects.count()}")  # Doit être > 0
print(f"Lignes : {Line.objects.count()}")       # Doit être > 0
```

---

## 🎯 CAS D'USAGE TYPIQUES

### Cas 1 : Test de publication GLO

```bash
# 1. Vider
python reset_factures_rapide.py

# 2. Uploader un PDF GLO dans l'interface
# 3. Publier
# 4. Vérifier le résultat
```

---

### Cas 2 : Test de publication SOM

```bash
# 1. Vider
python reset_factures_rapide.py

# 2. Uploader des PDFs SOM
# 3. Publier
# 4. Vérifier les lignes affectées
```

---

### Cas 3 : Test de notifications

```bash
# 1. Vider
python reset_factures_rapide.py

# 2. Publier une facture
# 3. Déclencher une notification
# 4. Vérifier l'envoi
```

---

### Cas 4 : Tests répétés

```bash
# Boucle de test rapide
while true; do
    python reset_factures_rapide.py
    # Faire vos tests manuels
    read -p "Appuyez sur Entrée pour recommencer..."
done
```

---

## 🚀 COMMANDES RAPIDES

### Créer un alias (optionnel)

**Windows (PowerShell)** :
```powershell
# Ajouter à votre profil PowerShell
function Reset-Factures {
    cd "c:\Users\Benoit\Documents\BURRO\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026\Back"
    python reset_factures_rapide.py
}

# Utilisation
Reset-Factures
```

**Linux/Mac (Bash)** :
```bash
# Ajouter à ~/.bashrc ou ~/.zshrc
alias reset-factures='cd ~/path/to/Back && python reset_factures_rapide.py'

# Utilisation
reset-factures
```

---

## 📁 FICHIERS CRÉÉS

| Fichier | Description | Utilisation |
|---------|-------------|-------------|
| `reset_factures.py` | Script avec menu | Tests occasionnels |
| `reset_factures_rapide.py` | Script rapide | Tests fréquents |
| `GUIDE_RESET_FACTURES.md` | Ce guide | Documentation |

---

## 🏁 RÉSUMÉ ULTRA-COURT

**Pour vider les factures rapidement** :

```bash
cd Back
python reset_factures_rapide.py
```

**C'est tout !** ✨

Vous pouvez maintenant refaire vos tests de publication de PDFs.

---

**Date** : 6 août 2026  
**Version** : 1.0  
**Auteur** : Système Kiro
