# Fix : NameError CanPublishInvoices

**Date** : 1er août 2026  
**Statut** : ✅ **CORRIGÉ**

---

## 🐛 Problème

Erreur au démarrage du serveur Django :

```
NameError: name 'CanPublishInvoices' is not defined
```

**Fichier** : `Back/billing/views.py` ligne 835

---

## 🔍 Cause

La permission `CanPublishInvoices` était utilisée dans les décorateurs `@action` mais n'était pas importée depuis `accounts.permissions`.

---

## ✅ Solution

**Fichier modifié** : `Back/billing/views.py`

**Avant** :
```python
from accounts.permissions import IsAgentFacturation, CanManageUser, CanManageTarifs, CanManageServices
```

**Après** :
```python
from accounts.permissions import (
    IsAgentFacturation, CanManageUser, CanManageTarifs, CanManageServices,
    CanPublishInvoices, CanUploadPDF, CanValidateInvoices, CanGenerateInvoices
)
```

---

## 🧪 Vérification

```bash
python manage.py check
# System check identified no issues (0 silenced).
```

✅ **Aucun problème détecté**

---

## 📝 Permissions Ajoutées

1. **CanPublishInvoices** : Publication de factures (CHEF_FACTURATION, AGENT_FACTURATION)
2. **CanUploadPDF** : Upload de PDF (CHEF_FACTURATION, AGENT_FACTURATION)
3. **CanValidateInvoices** : Validation de factures (CHEF_FACTURATION, AGENT_FACTURATION)
4. **CanGenerateInvoices** : Génération de factures (CHEF_FACTURATION, AGENT_FACTURATION)

Ces permissions étaient définies dans `accounts/permissions.py` mais non importées.

---

## 🚀 Prochaine Étape

Le serveur peut maintenant démarrer :

```bash
cd Back
python manage.py runserver
```

Puis tester l'écran "Factures à publier" :
- Se connecter en tant qu'agent/chef
- Aller sur `/agent/factures-a-publier`
- Vérifier la liste des factures VALIDEE
