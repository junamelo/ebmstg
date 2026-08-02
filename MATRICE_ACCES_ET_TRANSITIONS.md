# MATRICE D'ACCÈS ET TRANSITIONS
## Portail Web de Publication de Factures - Moov Africa

**Version** : 1.0  
**Date** : 30 juillet 2026

---

## A. MATRICE RÔLE × ACTION

| Action | SUPER_ADMIN | CHEF_FACTURATION | AGENT_FACTURATION | PAYEUR | EMPLOYE |
|--------|-------------|------------------|-------------------|--------|---------|
| **Gestion utilisateurs** |
| Créer Admin | ✅ | ❌ | ❌ | ❌ | ❌ |
| Créer Chef | ✅ | ❌ | ❌ | ❌ | ❌ |
| Créer Agent | ✅ | ✅ | ❌ | ❌ | ❌ |
| Créer Payeur | ✅ | ✅ | ✅ | ❌ | ❌ |
| Créer Employé | ✅ | ✅ | ✅ | ❌ | ❌ |
| Modifier tout utilisateur | ✅ | ❌ | ❌ | ❌ | ❌ |
| Modifier ses agents | ❌ | ✅ | ❌ | ❌ | ❌ |
| Modifier son profil | ✅ | ✅ | ✅ | ✅ | ✅ |
| Supprimer utilisateur | ✅ | ❌ | ❌ | ❌ | ❌ |
| Suspendre utilisateur | ✅ | ✅ (agents) | ❌ | ❌ | ❌ |
| Réinitialiser mot de passe | ✅ | ✅ (agents) | ❌ | ❌ | ❌ |
| **Gestion entreprises** |
| Créer entreprise | ✅ | ✅ | ✅ | ❌ | ❌ |
| Modifier entreprise | ✅ | ✅ | ✅ | ❌ | ❌ |
| Supprimer entreprise | ✅ | ✅ | ❌ | ❌ | ❌ |
| Affecter payeur | ✅ | ✅ | ✅ | ❌ | ❌ |
| Consulter toutes entreprises | ✅ | ✅ | ✅ | ❌ | ❌ |
| Consulter ses entreprises | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Gestion lignes** |
| Créer ligne | ✅ | ✅ | ✅ | ❌ | ❌ |
| Modifier ligne | ✅ | ✅ | ✅ | ❌ | ❌ |
| Supprimer ligne | ✅ | ✅ | ❌ | ❌ | ❌ |
| Affecter employé | ✅ | ✅ | ✅ | ❌ | ❌ |
| Retirer employé | ✅ | ✅ | ✅ | ❌ | ❌ |
| Changer cycle | ✅ | ✅ | ✅ | ❌ | ❌ |
| Changer statut ligne | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Gestion factures** |
| Créer facture | ✅ | ✅ | ✅ | ❌ | ❌ |
| Modifier facture (BROUILLON) | ✅ | ✅ | ✅ | ❌ | ❌ |
| Valider facture (BROUILLON → EN_COURS) | ✅ | ✅ | ✅ | ❌ | ❌ |
| Upload PDF | ✅ | ✅ | ✅ | ❌ | ❌ |
| Attacher PDF | ✅ | ✅ | ✅ | ❌ | ❌ |
| Publier facture (VALIDEE → PUBLIEE) | ✅ | ✅ | ✅ | ❌ | ❌ |
| Annuler facture | ✅ | ✅ | ❌ | ❌ | ❌ |
| Marquer payée | ✅ | ✅ | ❌ | ❌ | ❌ |
| Consulter toutes factures | ✅ | ✅ | ✅ | ❌ | ❌ |
| Consulter factures entreprise | ✅ | ✅ | ✅ | ✅ (publiées) | ❌ |
| Consulter factures ligne | ✅ | ✅ | ✅ | ✅ (publiées) | ✅ (publiées) |
| Télécharger PDF | ✅ | ✅ | ✅ | ✅ (ses factures) | ✅ (ses factures) |
| Voir factures non publiées | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Gestion services/forfaits** |
| Créer forfait | ✅ | ✅ | ✅ | ❌ | ❌ |
| Modifier forfait | ✅ | ✅ | ❌ | ❌ | ❌ |
| Activer/désactiver forfait | ✅ | ✅ | ❌ | ❌ | ❌ |
| Créer service | ✅ | ✅ | ✅ | ❌ | ❌ |
| Modifier service | ✅ | ✅ | ❌ | ❌ | ❌ |
| Activer/désactiver service | ✅ | ✅ | ❌ | ❌ | ❌ |
| Consulter forfaits/services | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Rapports et statistiques** |
| Voir dashboard global | ✅ | ✅ | ✅ | ❌ | ❌ |
| Voir dashboard entreprise | ✅ | ✅ | ✅ | ✅ | ❌ |
| Voir dashboard personnel | ✅ | ✅ | ✅ | ✅ | ✅ |
| Exporter données | ✅ | ✅ | ✅ | ✅ (ses données) | ✅ (ses données) |
| Voir logs système | ✅ | ✅ | ❌ | ❌ | ❌ |
| Voir historique factures | ✅ | ✅ | ✅ | ✅ (ses factures) | ✅ (ses factures) |
| Voir historique publications | ✅ | ✅ | ✅ | ❌ | ❌ |

---

## B. MATRICE STATUT × TRANSITION AUTORISÉE

### B.1 Tableau des transitions

| Depuis ↓ / Vers → | BROUILLON | EN_COURS | VALIDEE | PUBLIEE | PAYEE | ANNULEE |
|-------------------|-----------|----------|---------|---------|-------|---------|
| **BROUILLON** | - | ✅ Valider | ❌ | ❌ | ❌ | ✅ Annuler |
| **EN_COURS** | ❌ | - | ✅ PDF match | ❌ | ❌ | ✅ Annuler |
| **VALIDEE** | ❌ | ❌ | - | ✅ Publier | ❌ | ✅ Annuler |
| **PUBLIEE** | ❌ | ❌ | ❌ | - | ✅ Payer | ⚠️ À valider |
| **PAYEE** | ❌ | ❌ | ❌ | ❌ | - | ❌ |
| **ANNULEE** | ❌ | ❌ | ❌ | ❌ | ❌ | - |

**Légende** :
- ✅ : Transition autorisée
- ❌ : Transition interdite
- ⚠️ : À valider avec règles métier Moov
- `-` : Même statut (pas de transition)

### B.2 Détail des transitions autorisées

#### 1. BROUILLON → EN_COURS
- **Action** : Validation de la facture par l'agent
- **Déclencheur** : Bouton "Valider" ou API `POST /invoices/{id}/valider/`
- **Conditions** : Aucune (toujours possible)
- **Rôles autorisés** : ADMIN, CHEF, AGENT
- **Effet** : Facture devient prête pour matching PDF

#### 2. EN_COURS → VALIDEE
- **Action** : Attachement automatique du PDF
- **Déclencheur** : Upload PDF + matching réussi
- **Conditions** : PDF correctement associé à la facture
- **Rôles autorisés** : ADMIN, CHEF, AGENT (via upload)
- **Effet** : PDF attaché, facture contrôlée

#### 3. VALIDEE → PUBLIEE
- **Action** : Publication de la facture
- **Déclencheur** : Action "Publier" par agent/chef
- **Conditions** : PDF présent, contrôles métier OK
- **Rôles autorisés** : ADMIN, CHEF, AGENT
- **Effet** : Facture visible aux clients (payeur/employé)

#### 4. PUBLIEE → PAYEE
- **Action** : Enregistrement du paiement
- **Déclencheur** : Action manuelle ou automatique
- **Conditions** : Paiement reçu et enregistré
- **Rôles autorisés** : ADMIN, CHEF
- **Effet** : Facture marquée comme réglée

#### 5. BROUILLON/EN_COURS/VALIDEE → ANNULEE
- **Action** : Annulation de la facture
- **Déclencheur** : Action "Annuler" avec raison
- **Conditions** : Raison obligatoire
- **Rôles autorisés** : ADMIN, CHEF
- **Effet** : Facture n'est plus active

#### 6. PUBLIEE → ANNULEE
- **Statut** : ⚠️ **À VALIDER** avec Moov Africa
- **Question** : Peut-on annuler une facture déjà consultée par le client ?
- **Impact** : Si oui, nécessite notification client + procédure métier

### B.3 Détail des transitions interdites

#### 1. ANNULEE → {tout statut actif}
- **Raison** : Une facture annulée ne peut pas être réactivée
- **Alternative** : Créer une nouvelle facture
- **Code erreur** : `ERR_INVALID_TRANSITION`
- **Message** : "Une facture annulée ne peut pas être réactivée. Créez une nouvelle facture."

#### 2. PAYEE → {BROUILLON, EN_COURS, VALIDEE}
- **Raison** : Une facture payée ne peut pas revenir en arrière
- **Alternative** : Avoir payé (remboursement = processus séparé)
- **Code erreur** : `ERR_ALREADY_PAID`
- **Message** : "Une facture payée ne peut pas être modifiée."

#### 3. PUBLIEE → {BROUILLON, EN_COURS}
- **Raison** : Éviter le remplacement silencieux d'une facture consultée
- **Alternative** : Annuler puis créer nouvelle facture
- **Code erreur** : `ERR_ALREADY_PUBLISHED`
- **Message** : "Une facture publiée ne peut pas être remplacée. Annulez-la d'abord si nécessaire."

#### 4. EN_COURS → BROUILLON
- **Raison** : Pas de retour en arrière après validation
- **Alternative** : Annuler la facture
- **Code erreur** : `ERR_INVALID_TRANSITION`
- **Message** : "Impossible de revenir au statut brouillon. Annulez la facture si nécessaire."

#### 5. VALIDEE → EN_COURS
- **Raison** : PDF déjà attaché, pas de détachement automatique
- **Alternative** : Annuler puis créer nouvelle facture
- **Code erreur** : `ERR_INVALID_TRANSITION`
- **Message** : "Impossible de détacher un PDF validé. Annulez la facture si nécessaire."

#### 6. Toute transition depuis PAYEE
- **Raison** : Facture archivée, immuable
- **Alternative** : Processus de remboursement séparé
- **Code erreur** : `ERR_INVOICE_PAID`
- **Message** : "Une facture payée ne peut plus être modifiée."

### B.4 Conditions techniques par transition

```python
# Pseudo-code des validations

def transition_to_en_cours(facture):
    if facture.statut != 'BROUILLON':
        raise ValidationError("Seules les factures BROUILLON peuvent être validées")
    if not facture.montant_ttc or facture.montant_ttc <= 0:
        raise ValidationError("Le montant doit être défini")
    # OK

def transition_to_validee(facture, pdf_file):
    if facture.statut != 'EN_COURS':
        raise ValidationError("Seules les factures EN_COURS peuvent recevoir un PDF")
    if not pdf_file:
        raise ValidationError("Fichier PDF obligatoire")
    # OK

def transition_to_publiee(facture):
    if facture.statut != 'VALIDEE':
        raise ValidationError("Seules les factures VALIDEE peuvent être publiées")
    if not facture.fichier_pdf:
        raise ValidationError("PDF obligatoire pour publication")
    # OK

def transition_to_payee(facture):
    if facture.statut != 'PUBLIEE':
        raise ValidationError("Seules les factures PUBLIEE peuvent être marquées payées")
    # OK

def transition_to_annulee(facture, raison):
    if facture.statut == 'PAYEE':
        raise ValidationError("Une facture payée ne peut pas être annulée")
    if facture.statut == 'ANNULEE':
        raise ValidationError("Facture déjà annulée")
    if not raison:
        raise ValidationError("Raison d'annulation obligatoire")
    # OK

def prevent_invalid_transitions(facture, nouveau_statut):
    FORBIDDEN = {
        'ANNULEE': ['BROUILLON', 'EN_COURS', 'VALIDEE', 'PUBLIEE', 'PAYEE'],
        'PAYEE': ['BROUILLON', 'EN_COURS', 'VALIDEE'],
        'PUBLIEE': ['BROUILLON', 'EN_COURS'],
        'VALIDEE': ['BROUILLON', 'EN_COURS'],
        'EN_COURS': ['BROUILLON'],
    }
    
    if nouveau_statut in FORBIDDEN.get(facture.statut, []):
        raise ValidationError(f"Transition {facture.statut} → {nouveau_statut} interdite")
```

### B.5 Audit des transitions

Chaque transition de statut DOIT générer une entrée dans `HistoriqueFacturation` :

```python
HistoriqueFacturation.objects.create(
    invoice=facture,
    utilisateur=request.user,
    type_action='VALIDATION',  # ou PUBLICATION, PAIEMENT, ANNULATION
    ancien_statut=ancien_statut,
    nouveau_statut=nouveau_statut,
    commentaire=raison_ou_commentaire
)
```

---

## C. PERMISSIONS CODÉES

### C.1 Classes de permissions backend

```python
# Défini dans Back/accounts/permissions.py

class CanPublishInvoices(permissions.BasePermission):
    """Publier factures : ADMIN, CHEF, AGENT"""
    roles_autorises = ['SUPER_ADMIN', 'CHEF_FACTURATION', 'AGENT_FACTURATION']

class CanCancelInvoices(permissions.BasePermission):
    """Annuler factures : ADMIN, CHEF"""
    roles_autorises = ['SUPER_ADMIN', 'CHEF_FACTURATION']

class CanValidateInvoices(permissions.BasePermission):
    """Valider factures : ADMIN, CHEF, AGENT"""
    roles_autorises = ['SUPER_ADMIN', 'CHEF_FACTURATION', 'AGENT_FACTURATION']

class CanUploadPDF(permissions.BasePermission):
    """Upload PDF : ADMIN, CHEF, AGENT"""
    roles_autorises = ['SUPER_ADMIN', 'CHEF_FACTURATION', 'AGENT_FACTURATION']

class CanManageInvoices(permissions.BasePermission):
    """Gérer factures : ADMIN, CHEF, AGENT pour écriture"""
    lecture = ['SUPER_ADMIN', 'CHEF_FACTURATION', 'AGENT_FACTURATION', 'PAYEUR', 'EMPLOYE']
    ecriture = ['SUPER_ADMIN', 'CHEF_FACTURATION', 'AGENT_FACTURATION']
```

### C.2 Vérification dans les vues

```python
# Exemple dans InvoiceViewSet

@action(detail=True, methods=['post'], permission_classes=[CanPublishInvoices])
def publier(self, request, pk=None):
    """Publier une facture VALIDEE"""
    facture = self.get_object()
    
    # Vérification statut
    if facture.statut != 'VALIDEE':
        return Response(
            {'error': 'Seules les factures VALIDEE peuvent être publiées'},
            status=400
        )
    
    # Transition
    ancien_statut = facture.statut
    facture.statut = 'PUBLIEE'
    facture.save()
    
    # Audit
    HistoriqueFacturation.objects.create(
        invoice=facture,
        utilisateur=request.user,
        type_action='PUBLICATION',
        ancien_statut=ancien_statut,
        nouveau_statut='PUBLIEE'
    )
    
    return Response({'message': 'Facture publiée avec succès'})
```

---

## D. TESTS DE VALIDATION

### D.1 Tests de transitions autorisées

```python
# À implémenter dans Back/billing/tests.py

def test_transition_brouillon_to_en_cours():
    """Vérifie BROUILLON → EN_COURS"""
    facture = Invoice.objects.create(statut='BROUILLON', ...)
    facture.statut = 'EN_COURS'
    facture.save()
    assert facture.statut == 'EN_COURS'

def test_transition_en_cours_to_validee():
    """Vérifie EN_COURS → VALIDEE après PDF"""
    facture = Invoice.objects.create(statut='EN_COURS', ...)
    facture.fichier_pdf = 'test.pdf'
    facture.statut = 'VALIDEE'
    facture.save()
    assert facture.statut == 'VALIDEE'

def test_transition_validee_to_publiee():
    """Vérifie VALIDEE → PUBLIEE"""
    facture = Invoice.objects.create(statut='VALIDEE', fichier_pdf='test.pdf', ...)
    facture.statut = 'PUBLIEE'
    facture.save()
    assert facture.statut == 'PUBLIEE'
```

### D.2 Tests de transitions interdites

```python
def test_transition_annulee_to_brouillon_forbidden():
    """Vérifie qu'ANNULEE → BROUILLON est interdit"""
    facture = Invoice.objects.create(statut='ANNULEE', ...)
    with pytest.raises(ValidationError):
        facture.statut = 'BROUILLON'
        facture.full_clean()  # Validation Django

def test_transition_payee_to_en_cours_forbidden():
    """Vérifie que PAYEE → EN_COURS est interdit"""
    facture = Invoice.objects.create(statut='PAYEE', ...)
    with pytest.raises(ValidationError):
        facture.statut = 'EN_COURS'
        facture.full_clean()
```

### D.3 Tests de permissions

```python
def test_payeur_cannot_see_non_published():
    """Payeur ne voit pas les factures non PUBLIEE"""
    client = APIClient()
    client.force_authenticate(user=payeur_user)
    
    # Créer facture VALIDEE
    facture = Invoice.objects.create(
        company=payeur_user.companies.first(),
        statut='VALIDEE'
    )
    
    # Tenter d'accéder
    response = client.get(f'/api/billing/invoices/{facture.id}/')
    assert response.status_code == 404  # Pas visible

def test_employe_cannot_see_other_lines():
    """Employé ne voit pas les factures d'autres lignes"""
    client = APIClient()
    client.force_authenticate(user=employe_user)
    
    # Créer facture d'une autre ligne
    facture = Invoice.objects.create(
        line=autre_ligne,
        statut='PUBLIEE'
    )
    
    # Tenter d'accéder
    response = client.get(f'/api/billing/invoices/{facture.id}/')
    assert response.status_code == 404  # Pas visible
```

---

**Fin de la matrice d'accès et transitions**

