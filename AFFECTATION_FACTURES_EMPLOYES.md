# ✅ AFFECTATION DES FACTURES AUX EMPLOYÉS

**Date de mise en œuvre** : 30 juillet 2026  
**Statut** : Implémenté et fonctionnel

---

## 🎯 OBJECTIF

Permettre aux employés de voir leurs factures individuelles (SOM) en se connectant avec leur numéro de ligne (MSISDN), tout en maintenant la visibilité des factures globales pour les payeurs.

---

## 🔄 ARCHITECTURE D'AFFECTATION

```
┌─────────────────────────────────────────────────────────────┐
│                      COMPANY (Entreprise)                    │
│                             │                                │
│                             ├── Payeur (User PAYEUR)         │
│                             │                                │
│                             ├── Facture GLOBALE              │
│                             │   └─> Visible par Payeur       │
│                             │                                │
│                             └── Lines (Lignes)               │
│                                  │                           │
│                                  ├── Line 1 (MSISDN)         │
│                                  │   ├── Employé (User)      │
│                                  │   └── Facture SOM         │
│                                  │       └─> Visible par:    │
│                                  │           • Payeur        │
│                                  │           • Cet Employé   │
│                                  │                           │
│                                  ├── Line 2 (MSISDN)         │
│                                  │   ├── Employé (User)      │
│                                  │   └── Facture SOM         │
│                                  └── ...                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 MODIFICATIONS APPORTÉES

### 1. **Backend - Modèle Invoice**

**Fichier** : `Back/billing/models.py`

```python
class Invoice(models.Model):
    # ... champs existants ...
    
    # NOUVEAU : Liaison optionnelle à une ligne téléphonique
    line = models.ForeignKey(
        Line,
        on_delete=models.SET_NULL,
        related_name='invoices',
        null=True,
        blank=True,
        verbose_name='Ligne concernée'
    )
```

**Logique** :
- `line = None` → Facture **GLOBALE** (visible par payeur uniquement)
- `line = Line(id=X)` → Facture **INDIVIDUELLE/SOM** (visible par payeur + employé de cette ligne)

---

### 2. **Backend - Filtrage des factures par rôle**

**Fichier** : `Back/billing/views.py`

```python
def get_queryset(self):
    user = self.request.user
    
    # Admin, Chef, Agent : voient TOUT
    if user.role in ['SUPER_ADMIN', 'CHEF_FACTURATION', 'AGENT_FACTURATION']:
        return Invoice.objects.all().select_related('company', 'line', 'line__employe')
    
    # Payeur : ses factures (globales + individuelles de son entreprise)
    if user.role == 'PAYEUR':
        return Invoice.objects.filter(
            company__payeur=user
        ).select_related('company', 'line', 'line__employe')
    
    # Employé : UNIQUEMENT les factures SOM de ses lignes
    if user.role == 'EMPLOYE':
        return Invoice.objects.filter(
            line__employe=user
        ).select_related('company', 'line', 'line__employe')
    
    return Invoice.objects.none()
```

---

### 3. **Backend - Matching automatique lors de l'upload PDF**

**Fichier** : `Back/billing/services/pdf_processor.py`

Lors de l'upload d'un PDF multi-factures :
1. Découpage en fichiers individuels par MSISDN
2. Recherche de la ligne correspondante via `Line.objects.filter(msisdn=...)`
3. Attachement du PDF à la facture
4. **NOUVEAU** : Affectation automatique de `invoice.line = ligne_trouvée`

```python
# Dans PDFMatcher.auto_attach_pdfs()
if line and invoice:
    invoice.line = line  # Affectation automatique
    invoice.fichier_pdf = pdf_path
    invoice.statut = 'VALIDEE'
    invoice.save()
```

---

### 4. **Backend - Migration automatique des factures existantes**

**Fichier** : `Back/billing/migrations/0004_invoice_line.py`

Migration intelligente qui :
1. Ajoute le champ `line` à Invoice
2. Parcourt les factures existantes
3. Si le MSISDN est dans le `numero_facture`, affecte automatiquement la ligne

```python
def link_existing_individual_invoices(apps, schema_editor):
    for invoice in Invoice.objects.filter(line__isnull=True):
        line = Line.objects.filter(
            company_id=invoice.company_id,
            msisdn__in=[... if value in invoice.numero_facture]
        ).first()
        if line:
            invoice.line_id = line.id
            invoice.save()
```

---

### 5. **Backend - Connexion par MSISDN pour les employés**

**Fichier** : `Back/accounts/views.py`

Les employés peuvent désormais se connecter avec leur **numéro de ligne** :

```python
# LoginView.post()
try:
    user = User.objects.get(Q(email=email) | Q(username=email))
except User.DoesNotExist:
    return Response({'error': 'Identifiant incorrect'})
```

**Exemple** :
- Identifiant : `99475555`
- Mot de passe : `5678`

---

### 6. **Frontend - Service factures adapté**

**Fichier** : `Front/src/services/factureService.js`

```javascript
const adapterFacture = (facture) => ({
  ...facture,
  type: facture.line ? 'SOMMAIRE' : 'GLOBALE',  // Détection automatique
  ligneOuFlotte: facture.line_msisdn || facture.company_name,
  pdfUrl: facture.fichier_pdf ? `${API_ORIGIN}${facture.fichier_pdf}` : null,
})
```

---

## 🧪 CAS DE TEST - TOTSOVI Eyram

### Données configurées

**Employé** :
- Nom : `TOTSOVI Eyram`
- Email : `e.totsovi@biospartners.com`
- Username : `99475555` (= MSISDN)
- Password : `5678`
- Rôle : `EMPLOYE`
- Téléphone : `99475555`

**Ligne** :
- MSISDN : `99475555`
- Entreprise : `CAFE INFORMATIQUE ET TEL`
- Statut : `ACTIF`
- Cycle : `OP` (Postpayé)
- **Employé affecté** : TOTSOVI Eyram ✅

**Facture individuelle** :
- Numéro : `SOM-99475555-202606`
- Company : CAFE INFORMATIQUE ET TEL
- **Line** : 99475555 ✅
- PDF : `factures/PHYS.OPN.202606.SOM_page_17.pdf`
- Montant TTC : 5 290 000 FCFA
- Statut : `VALIDEE`

---

## 🚀 PROCESSUS DE TEST

### Étape 1 : Vérifier la migration

```bash
cd Back
python manage.py migrate
```

**Résultat attendu** :
```
Running migrations:
  Applying billing.0004_invoice_line... OK
```

### Étape 2 : Vérifier l'affectation en base

```bash
python manage.py shell
```

```python
from billing.models import Line, Invoice
from accounts.models import User

# Vérifier l'employé
employe = User.objects.get(username='99475555')
print(f"Employé : {employe.first_name} {employe.last_name}")
print(f"Email : {employe.email}")
print(f"Rôle : {employe.role}")

# Vérifier la ligne
ligne = Line.objects.get(msisdn='99475555')
print(f"\nLigne : {ligne.msisdn}")
print(f"Entreprise : {ligne.company.raison_sociale}")
print(f"Employé affecté : {ligne.employe}")

# Vérifier la facture
factures = Invoice.objects.filter(line=ligne)
for f in factures:
    print(f"\nFacture : {f.numero_facture}")
    print(f"Ligne associée : {f.line}")
    print(f"PDF : {f.fichier_pdf}")
    print(f"Visible par employé : {f.line.employe == employe}")
```

### Étape 3 : Tester la connexion employé

**Frontend** :
1. Aller sur `http://localhost:3000/login`
2. Entrer :
   - **Identifiant** : `99475555`
   - **Mot de passe** : `5678`
3. Cliquer sur "Se connecter"

**Résultat attendu** :
- Connexion réussie ✅
- Redirection vers `/dashboard`
- Rôle affiché : "Employé"

### Étape 4 : Consulter les factures

1. Cliquer sur "Mes factures" dans la sidebar
2. Observer la liste

**Résultat attendu** :
- **1 facture** visible : `SOM-99475555-202606`
- Type : `SOMMAIRE`
- Ligne : `99475555`
- Montant : `5 290 000 FCFA`
- Bouton "Télécharger" disponible si PDF présent

### Étape 5 : Tester avec un payeur

**Se reconnecter en tant que payeur** de l'entreprise CAFE INFORMATIQUE ET TEL :
- Identifiant : (email du payeur)
- Vérifier que le payeur voit :
  - Les factures globales de son entreprise
  - **ET** toutes les factures SOM de ses employés (dont celle de TOTSOVI)

---

## 📊 MATRICE DE VISIBILITÉ

| Rôle | Factures GLOBALES | Factures SOM (individuelle) |
|------|-------------------|------------------------------|
| **SUPER_ADMIN** | Toutes | Toutes |
| **CHEF_FACTURATION** | Toutes | Toutes |
| **AGENT_FACTURATION** | Toutes | Toutes |
| **PAYEUR** | Ses entreprises | Ses entreprises (toutes lignes) |
| **EMPLOYE** | ❌ Aucune | ✅ Ses lignes uniquement |

---

## ⚠️ PRÉREQUIS POUR L'AFFECTATION

Pour qu'un employé voie ses factures, il faut **obligatoirement** :

1. ✅ Un compte User avec `role='EMPLOYE'`
2. ✅ Une ligne Line avec le MSISDN de l'employé
3. ✅ L'affectation `line.employe = user_employe`
4. ✅ Une facture Invoice avec `invoice.line = ligne`

**Sans affectation de la ligne à l'employé**, la facture reste visible uniquement au payeur.

---

## 🔧 COMMANDES UTILES

### Créer un employé de test

```python
from accounts.models import User
from billing.models import Line

# Créer l'employé
employe = User.objects.create_user(
    username='90123456',
    email='employe@test.tg',
    password='test123',
    first_name='Jean',
    last_name='DUPONT',
    role='EMPLOYE',
    telephone='90123456'
)

# Trouver sa ligne
ligne = Line.objects.get(msisdn='90123456')

# Affecter
ligne.employe = employe
ligne.save()

print(f"✅ Employé {employe.first_name} affecté à la ligne {ligne.msisdn}")
```

### Vérifier les affectations

```python
from billing.models import Line

# Lignes avec employés
lignes_affectees = Line.objects.exclude(employe__isnull=True)
for ligne in lignes_affectees:
    print(f"{ligne.msisdn} → {ligne.employe.first_name} {ligne.employe.last_name}")

# Lignes sans employés
lignes_non_affectees = Line.objects.filter(employe__isnull=True)
print(f"\n{lignes_non_affectees.count()} lignes sans employé affecté")
```

### Lister les factures d'un employé

```python
from accounts.models import User
from billing.models import Invoice

employe = User.objects.get(username='99475555')
factures = Invoice.objects.filter(line__employe=employe)

for f in factures:
    print(f"{f.numero_facture} - {f.montant_ttc} FCFA - {f.statut}")
```

---

## 🎯 WORKFLOW COMPLET

### Upload PDF → Affectation automatique

```
1. Agent uploade PHYS.OPN.202606.SOM-1-20.pdf
              ↓
2. PDFProcessor découpe en 20 fichiers individuels
              ↓
3. Pour chaque fichier :
   - Détecte MSISDN (ex: 99475555)
   - Recherche Line avec ce MSISDN
   - Recherche Invoice correspondante
   - Affecte invoice.line = ligne_trouvée ✅
   - Attache le PDF
   - Change statut → VALIDEE
              ↓
4. Employé TOTSOVI (username=99475555) se connecte
              ↓
5. GET /api/billing/invoices/
   → Filtre automatique : line__employe=user
              ↓
6. Affichage de SA facture individuelle uniquement
```

---

## ✅ CHECKLIST DE VALIDATION

- [x] Migration 0004 appliquée
- [x] Champ `line` ajouté au modèle Invoice
- [x] Filtrage des factures par rôle implémenté
- [x] Connexion par MSISDN pour employés
- [x] Matching automatique ligne ↔ facture lors de l'upload PDF
- [x] Migration automatique des factures existantes
- [x] Service frontend adapté (type GLOBALE/SOMMAIRE)
- [x] Compte test TOTSOVI créé et affecté
- [ ] Test de connexion employé validé
- [ ] Consultation factures employé validée
- [ ] Consultation factures payeur validée

---

## 📚 FICHIERS MODIFIÉS

```
Back/
├── billing/
│   ├── models.py                    [+16-6]   ← Ajout champ line
│   ├── views.py                     [+15-5]   ← Filtrage par rôle
│   ├── services/pdf_processor.py    [+5-2]    ← Affectation automatique
│   └── migrations/
│       └── 0004_invoice_line.py     [NEW]     ← Migration intelligente
│
├── accounts/
│   ├── views.py                     [+6-4]    ← Connexion MSISDN
│   ├── serializers.py               [+3-1]    ← Support MSISDN
│   └── permissions.py               [+1-1]    ← Ajustement CanViewInvoices
│
Front/
└── src/services/
    └── factureService.js            [+3-2]    ← Type GLOBALE/SOMMAIRE
```

---

## 🚀 PROCHAINES ÉTAPES

1. **Tester** : Connexion employé + consultation factures
2. **Valider** : Affichage correct selon le rôle
3. **Documenter** : Créer guide utilisateur pour les employés
4. **Former** : Expliquer aux agents comment affecter les lignes
5. **Déployer** : Mettre en production si tests OK

---

**Date de documentation** : 30 juillet 2026  
**Statut** : ✅ IMPLÉMENTÉ - EN PHASE DE TEST  
**Développeur** : BANLEPO Mintre Benoit (avec Codex)  
**Projet** : Portail e-Billings - Moov Africa Togo

