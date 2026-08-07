# 📋 FONCTIONNALITÉ - Résiliation de Contrat avec Motif

**Date** : 6 août 2026  
**Statut** : ✅ **IMPLÉMENTÉE ET OPÉRATIONNELLE**

---

## 🎯 VUE D'ENSEMBLE

La fonctionnalité de **résiliation de contrat** permet aux agents de facturation de clôturer un contrat client avec un motif et une date de résiliation. Cette action :
- ✅ Marque le contrat comme résilié
- ✅ Enregistre la date de résiliation
- ✅ Enregistre le motif de résiliation
- ✅ Enregistre une observation optionnelle
- ✅ Change le statut de facturation en "CLOS"
- ✅ Trace l'action dans l'audit

---

## 📊 MODÈLE DE DONNÉES

### Champs de résiliation dans `Company` (modèle)

```python
class Company(models.Model):
    # ... autres champs ...
    
    # Champs de résiliation
    est_resilie = models.BooleanField(
        default=False, 
        verbose_name='Résilié'
    )
    date_resiliation = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='Date de résiliation'
    )
    motif_resiliation = models.TextField(
        blank=True, 
        verbose_name='Motif de résiliation'
    )
    observation_resiliation = models.TextField(
        blank=True, 
        verbose_name='Observation résiliation'
    )
```

**Base de données** : Table `companies`

| Champ | Type | Nullable | Description |
|-------|------|----------|-------------|
| `est_resilie` | BOOLEAN | Non | Indique si le contrat est résilié (défaut: false) |
| `date_resiliation` | DATE | Oui | Date effective de la résiliation |
| `motif_resiliation` | TEXT | Oui | Motif de la résiliation |
| `observation_resiliation` | TEXT | Oui | Observations complémentaires |

---

## 🔧 API REST

### Endpoint : Résilier un contrat

**URL** : `POST /api/billing/companies/{id}/resilier/`

**Méthode** : `POST`

**Authentification** : Token JWT requis

**Permissions** : Agent de facturation uniquement

### Paramètres de la requête

```json
{
  "date_resiliation": "2026-08-31",
  "motif_resiliation": "Fin de contrat client",
  "observation_resiliation": "Client a déménagé à l'étranger"
}
```

| Paramètre | Type | Obligatoire | Description |
|-----------|------|-------------|-------------|
| `date_resiliation` | string (YYYY-MM-DD) | ✅ Oui | Date de résiliation |
| `motif_resiliation` | string | ✅ Oui | Motif de la résiliation |
| `observation_resiliation` | string | ❌ Non | Observations complémentaires |

### Validations

1. ✅ Le contrat ne doit pas être déjà résilié
2. ✅ `date_resiliation` est obligatoire
3. ✅ `motif_resiliation` est obligatoire
4. ✅ Format de date valide (YYYY-MM-DD)
5. ✅ La date de résiliation ne peut pas être antérieure à la date d'effet du contrat

### Réponse succès (200 OK)

```json
{
  "id": 1,
  "compte": "123456",
  "raison_sociale": "Entreprise ABC",
  "categorie": "PE",
  "statut": "ACTIF",
  "est_resilie": true,
  "date_resiliation": "2026-08-31",
  "motif_resiliation": "Fin de contrat client",
  "observation_resiliation": "Client a déménagé à l'étranger",
  "statut_factures": "CLOS",
  "date_creation": "2026-01-15T10:30:00Z",
  "date_modification": "2026-08-06T16:45:00Z",
  "payeur": 5,
  "payeur_info": {
    "id": 5,
    "nom": "Jean Dupont",
    "email": "jean.dupont@example.com",
    "username": "jdupont"
  },
  "commercial": 2,
  "commercial_info": {
    "id": 2,
    "nom": "Martin",
    "prenom": "Pierre",
    "matricule": "COMM-001",
    "telephone": "22891234567"
  },
  "nombre_lignes": 15,
  "nombre_lignes_actives": 15,
  "lines": [...]
}
```

### Réponses d'erreur

#### Contrat déjà résilié (400 Bad Request)

```json
{
  "error": "Ce contrat est déjà résilié."
}
```

#### Date de résiliation manquante (400 Bad Request)

```json
{
  "error": "date_resiliation est obligatoire."
}
```

#### Motif de résiliation manquant (400 Bad Request)

```json
{
  "error": "motif_resiliation est obligatoire."
}
```

#### Format de date invalide (400 Bad Request)

```json
{
  "error": "Format de date invalide (YYYY-MM-DD)."
}
```

#### Date de résiliation antérieure à la date d'effet (400 Bad Request)

```json
{
  "error": "La date de résiliation ne peut pas être antérieure à la date d'effet."
}
```

---

## 🔍 TRAÇABILITÉ - Audit

Chaque résiliation est tracée dans la table `audit_contrats` :

```python
AuditContrat.objects.create(
    company=company,
    utilisateur=request.user,
    type_action='RESILIATION',
    description=f"Contrat résilié. Motif : {motif_resiliation}",
    anciennes_valeurs={
        'est_resilie': False, 
        'statut_factures': 'ACTIF'
    },
    nouvelles_valeurs={
        'est_resilie': True, 
        'date_resiliation': '2026-08-31', 
        'motif_resiliation': 'Fin de contrat client'
    }
)
```

**Consultation de l'historique** :
- Endpoint : `GET /api/billing/companies/{id}/historique/`
- Retourne toutes les actions sur le contrat, y compris les résiliations

---

## 💻 EXEMPLES D'UTILISATION

### Exemple 1 : Résiliation simple

```bash
curl -X POST https://api.example.com/api/billing/companies/123/resilier/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "date_resiliation": "2026-08-31",
    "motif_resiliation": "Fin de contrat client"
  }'
```

### Exemple 2 : Résiliation avec observation

```bash
curl -X POST https://api.example.com/api/billing/companies/123/resilier/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "date_resiliation": "2026-09-15",
    "motif_resiliation": "Faillite de l'entreprise",
    "observation_resiliation": "Liquidation judiciaire prononcée le 01/09/2026"
  }'
```

### Exemple 3 : Avec Python (requests)

```python
import requests

url = "https://api.example.com/api/billing/companies/123/resilier/"
headers = {
    "Authorization": "Bearer <token>",
    "Content-Type": "application/json"
}
data = {
    "date_resiliation": "2026-08-31",
    "motif_resiliation": "Fin de contrat client",
    "observation_resiliation": "Client a déménagé à l'étranger"
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    print("Contrat résilié avec succès")
    print(response.json())
else:
    print(f"Erreur : {response.json()}")
```

### Exemple 4 : Avec JavaScript (Axios)

```javascript
import axios from 'axios';

const resilierContrat = async (companyId, data) => {
  try {
    const response = await axios.post(
      `https://api.example.com/api/billing/companies/${companyId}/resilier/`,
      data,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    console.log('Contrat résilié avec succès', response.data);
    return response.data;
  } catch (error) {
    console.error('Erreur lors de la résiliation', error.response.data);
    throw error;
  }
};

// Utilisation
resilierContrat(123, {
  date_resiliation: '2026-08-31',
  motif_resiliation: 'Fin de contrat client',
  observation_resiliation: 'Client a déménagé à l'étranger'
});
```

---

## 🎨 INTERFACE UTILISATEUR (Frontend)

### Formulaire de résiliation

Créer un composant React pour la résiliation :

```jsx
import React, { useState } from 'react';
import axios from 'axios';

const FormulaireResiliation = ({ companyId, onSuccess, onCancel }) => {
  const [dateResiliation, setDateResiliation] = useState('');
  const [motifResiliation, setMotifResiliation] = useState('');
  const [observationResiliation, setObservationResiliation] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `/api/billing/companies/${companyId}/resilier/`,
        {
          date_resiliation: dateResiliation,
          motif_resiliation: motifResiliation,
          observation_resiliation: observationResiliation
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      onSuccess(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors de la résiliation');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="formulaire-resiliation">
      <h2>Résilier le contrat</h2>
      
      {error && (
        <div className="alert alert-danger">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="date_resiliation">
            Date de résiliation <span className="required">*</span>
          </label>
          <input
            type="date"
            id="date_resiliation"
            className="form-control"
            value={dateResiliation}
            onChange={(e) => setDateResiliation(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="motif_resiliation">
            Motif de résiliation <span className="required">*</span>
          </label>
          <textarea
            id="motif_resiliation"
            className="form-control"
            rows="3"
            value={motifResiliation}
            onChange={(e) => setMotifResiliation(e.target.value)}
            placeholder="Ex: Fin de contrat, Faillite, Déménagement..."
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="observation_resiliation">
            Observations (optionnel)
          </label>
          <textarea
            id="observation_resiliation"
            className="form-control"
            rows="3"
            value={observationResiliation}
            onChange={(e) => setObservationResiliation(e.target.value)}
            placeholder="Informations complémentaires..."
          />
        </div>

        <div className="form-actions">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onCancel}
            disabled={loading}
          >
            Annuler
          </button>
          <button
            type="submit"
            className="btn btn-danger"
            disabled={loading}
          >
            {loading ? 'Résiliation en cours...' : 'Résilier le contrat'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default FormulaireResiliation;
```

### Intégration dans la page de détail du contrat

```jsx
import React, { useState } from 'react';
import FormulaireResiliation from './FormulaireResiliation';

const DetailContrat = ({ company }) => {
  const [showResiliationForm, setShowResiliationForm] = useState(false);

  const handleResiliationSuccess = (updatedCompany) => {
    alert('Contrat résilié avec succès');
    setShowResiliationForm(false);
    // Recharger les données du contrat
    window.location.reload();
  };

  return (
    <div className="detail-contrat">
      <h1>{company.raison_sociale}</h1>
      
      {/* Affichage du statut de résiliation */}
      {company.est_resilie ? (
        <div className="alert alert-warning">
          <strong>Contrat résilié</strong>
          <p>Date : {company.date_resiliation}</p>
          <p>Motif : {company.motif_resiliation}</p>
          {company.observation_resiliation && (
            <p>Observations : {company.observation_resiliation}</p>
          )}
        </div>
      ) : (
        <div>
          <button
            className="btn btn-danger"
            onClick={() => setShowResiliationForm(true)}
          >
            Résilier le contrat
          </button>
        </div>
      )}

      {/* Formulaire de résiliation en modal ou inline */}
      {showResiliationForm && !company.est_resilie && (
        <FormulaireResiliation
          companyId={company.id}
          onSuccess={handleResiliationSuccess}
          onCancel={() => setShowResiliationForm(false)}
        />
      )}

      {/* Reste des détails du contrat */}
      {/* ... */}
    </div>
  );
};

export default DetailContrat;
```

---

## 📊 STATISTIQUES ET FILTRES

### Filtrer les contrats résiliés

```bash
# Tous les contrats résiliés
GET /api/billing/companies/?est_resilie=true

# Contrats non résiliés
GET /api/billing/companies/?est_resilie=false
```

### Recherche par motif de résiliation

Ajouter un filtre dans le backend :

```python
# Dans billing/views.py

class CompanyViewSet(viewsets.ModelViewSet):
    # ... existing code ...
    
    filterset_fields = [
        'categorie', 
        'statut', 
        'payeur', 
        'est_resilie'  # ← Ajouter ce filtre
    ]
```

---

## 🧪 TESTS

### Test de résiliation réussie

```python
# Dans billing/tests.py

from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import User
from billing.models import Company

class ResiliationContratTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Créer un agent de facturation
        self.agent = User.objects.create_user(
            username='agent1',
            email='agent@example.com',
            password='testpass',
            role='AGENT_FACTURATION'
        )
        
        # Créer un contrat
        self.company = Company.objects.create(
            compte='123456',
            raison_sociale='Test Company',
            categorie='PE',
            date_effet='2026-01-01'
        )
        
    def test_resilier_contrat_success(self):
        """Test de résiliation réussie"""
        self.client.force_authenticate(user=self.agent)
        
        response = self.client.post(
            f'/api/billing/companies/{self.company.id}/resilier/',
            {
                'date_resiliation': '2026-08-31',
                'motif_resiliation': 'Fin de contrat client',
                'observation_resiliation': 'Test observation'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.company.refresh_from_db()
        self.assertTrue(self.company.est_resilie)
        self.assertEqual(str(self.company.date_resiliation), '2026-08-31')
        self.assertEqual(self.company.motif_resiliation, 'Fin de contrat client')
        self.assertEqual(self.company.statut_factures, 'CLOS')
        
    def test_resilier_contrat_deja_resilie(self):
        """Test résiliation d'un contrat déjà résilié"""
        # Marquer le contrat comme résilié
        self.company.est_resilie = True
        self.company.date_resiliation = '2026-07-01'
        self.company.motif_resiliation = 'Ancien motif'
        self.company.save()
        
        self.client.force_authenticate(user=self.agent)
        
        response = self.client.post(
            f'/api/billing/companies/{self.company.id}/resilier/',
            {
                'date_resiliation': '2026-08-31',
                'motif_resiliation': 'Nouveau motif'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('déjà résilié', response.data['error'])
        
    def test_resilier_sans_date(self):
        """Test résiliation sans date"""
        self.client.force_authenticate(user=self.agent)
        
        response = self.client.post(
            f'/api/billing/companies/{self.company.id}/resilier/',
            {
                'motif_resiliation': 'Test'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('obligatoire', response.data['error'])
```

---

## 📋 CHECKLIST D'IMPLÉMENTATION

### Backend ✅

- [x] Champs de résiliation dans le modèle `Company`
- [x] Endpoint `/resilier/` dans `CompanyViewSet`
- [x] Validations des données
- [x] Traçabilité dans `AuditContrat`
- [x] Changement de statut en "CLOS"
- [x] Tests unitaires

### Frontend ⏱️

- [ ] Composant `FormulaireResiliation.jsx`
- [ ] Intégration dans la page de détail du contrat
- [ ] Affichage du statut de résiliation
- [ ] Modal de confirmation
- [ ] Gestion des erreurs
- [ ] Tests e2e

---

## 🎯 SCÉNARIOS D'UTILISATION

### Scénario 1 : Fin de contrat normal

**Contexte** : Un client souhaite résilier son contrat à la fin du mois.

**Actions** :
1. Agent ouvre la page du contrat
2. Clique sur "Résilier le contrat"
3. Remplit :
   - Date : 31/08/2026
   - Motif : "Fin de contrat - Demande client"
   - Observation : "Client satisfait, souhait de changer d'opérateur"
4. Valide
5. Le contrat passe en statut "CLOS"
6. Les lignes restent actives jusqu'à la date de résiliation

### Scénario 2 : Faillite d'entreprise

**Contexte** : Une entreprise cliente fait faillite.

**Actions** :
1. Agent ouvre la page du contrat
2. Clique sur "Résilier le contrat"
3. Remplit :
   - Date : Date de la liquidation
   - Motif : "Liquidation judiciaire"
   - Observation : "Jugement du tribunal du 15/08/2026"
4. Valide
5. Le contrat est immédiatement clos

### Scénario 3 : Déménagement à l'étranger

**Contexte** : Un client déménage hors du Togo.

**Actions** :
1. Agent ouvre la page du contrat
2. Clique sur "Résilier le contrat"
3. Remplit :
   - Date : Date de départ
   - Motif : "Déménagement hors zone de couverture"
   - Observation : "Client s'installe en France"
4. Valide

---

## 📝 MOTIFS DE RÉSILIATION COURANTS

Voici des exemples de motifs fréquents :

1. **Fin de contrat** : "Fin de contrat - Demande client"
2. **Faillite** : "Liquidation judiciaire" / "Redressement judiciaire"
3. **Déménagement** : "Déménagement hors zone de couverture"
4. **Insatisfaction** : "Insatisfaction client - Service"
5. **Prix** : "Offre concurrente plus avantageuse"
6. **Impayés** : "Résiliation pour non-paiement"
7. **Fermeture** : "Fermeture définitive de l'entreprise"
8. **Fusion** : "Fusion avec une autre entreprise"
9. **Changement** : "Changement de système de communication"
10. **Autre** : "Autre motif (voir observations)"

---

## 🏁 CONCLUSION

La fonctionnalité de résiliation de contrat est **complète et opérationnelle** côté backend. Elle permet :

✅ Résiliation avec date et motif  
✅ Validation des données  
✅ Traçabilité complète  
✅ Changement de statut automatique  
✅ Protection contre double résiliation  

**Prochaines étapes** : Implémenter l'interface utilisateur (formulaire de résiliation dans le frontend React).

---

**Date de documentation** : 6 août 2026  
**Version** : 1.0  
**Auteur** : Système Kiro
