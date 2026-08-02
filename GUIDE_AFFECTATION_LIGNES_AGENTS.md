# 📘 GUIDE D'AFFECTATION DES LIGNES - Pour Agents Facturation

**Public cible** : Agents et Chefs de facturation  
**Objectif** : Savoir comment affecter les lignes téléphoniques aux employés

---

## 🎯 POURQUOI AFFECTER LES LIGNES ?

Lorsqu'un employé se connecte au portail avec son numéro de ligne, il doit pouvoir **voir uniquement ses factures individuelles**.

Pour cela, il faut créer une **liaison** :
```
MSISDN (Numéro de ligne) ←→ Compte Employé
```

**Sans cette liaison** :
- ❌ L'employé ne voit aucune facture
- ❌ Seul le payeur de l'entreprise voit les factures

**Avec cette liaison** :
- ✅ L'employé voit ses factures
- ✅ Le payeur voit toujours toutes les factures de son entreprise

---

## 📋 PRÉREQUIS

Avant d'affecter une ligne, il faut :

1. ✅ **Un compte employé** créé dans le système
2. ✅ **Une ligne téléphonique** existante dans l'entreprise
3. ✅ **Les identifiants** de l'employé et de la ligne

---

## 🔧 MÉTHODE 1 : AFFECTATION VIA L'API (ACTUELLE)

### Étape 1 : Se connecter en tant qu'agent

```bash
POST http://localhost:8000/api/auth/login/
Content-Type: application/json

{
  "email": "agent@moov.tg",
  "password": "votre_mot_de_passe"
}
```

**Récupérer le token** dans la réponse :
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": { ... }
}
```

### Étape 2 : Lister les lignes disponibles

```bash
GET http://localhost:8000/api/billing/lines/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple de réponse** :
```json
{
  "results": [
    {
      "id": 1,
      "msisdn": "79300739",
      "company_name": "WACEM SA",
      "employe": null,  ← Pas d'employé affecté
      "statut": "ACTIF"
    },
    {
      "id": 4,
      "msisdn": "99475555",
      "company_name": "CAFE INFORMATIQUE ET TEL",
      "employe": {
        "id": 10,
        "first_name": "Eyram",
        "last_name": "TOTSOVI"
      },  ← Déjà affecté
      "statut": "ACTIF"
    }
  ]
}
```

### Étape 3 : Créer ou trouver le compte employé

**Option A : Créer un nouveau compte employé**

```bash
POST http://localhost:8000/api/auth/users/
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "email": "employe.test@entreprise.com",
  "username": "79300739",  ← MSISDN comme username
  "password": "MotDePasse123!",
  "first_name": "Jean",
  "last_name": "DUPONT",
  "role": "EMPLOYE",
  "telephone": "79300739",  ← Même MSISDN
  "force_password_change": false,
  "send_email": false
}
```

**Récupérer l'ID** de l'employé créé : `"id": 15`

**Option B : Chercher un employé existant**

```bash
GET http://localhost:8000/api/auth/users/?search=jean.dupont@entreprise.com
Authorization: Bearer TOKEN
```

### Étape 4 : Affecter la ligne à l'employé

```bash
POST http://localhost:8000/api/billing/lines/{line_id}/assigner_employe/
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "employe_id": 15
}
```

**Exemple concret** :
```bash
POST http://localhost:8000/api/billing/lines/1/assigner_employe/
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "employe_id": 15
}
```

**Réponse attendue** :
```json
{
  "message": "Employé Jean DUPONT affecté à la ligne 79300739 avec succès"
}
```

### Étape 5 : Vérifier l'affectation

```bash
GET http://localhost:8000/api/billing/lines/1/
Authorization: Bearer TOKEN
```

**Réponse** :
```json
{
  "id": 1,
  "msisdn": "79300739",
  "employe": {
    "id": 15,
    "first_name": "Jean",
    "last_name": "DUPONT",
    "email": "employe.test@entreprise.com"
  },  ← ✅ Affecté !
  "statut": "ACTIF"
}
```

---

## 🖥️ MÉTHODE 2 : AFFECTATION VIA L'INTERFACE (À VENIR)

### Interface à développer

**Page** : `/agent/lignes` ou `/agent/contrats/{id}`

**Écran "Gestion des Lignes"** :

```
┌────────────────────────────────────────────────────────────┐
│  Gestion des Lignes - WACEM SA                             │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  MSISDN        Utilisateur       Employé affecté   Actions │
│  ─────────────────────────────────────────────────────────│
│  79300739     KPONOU Jean        [Sélectionner ▼]  [✓]    │
│  79300742     AGBO Marie         Jean DUPONT       [✎]    │
│  79300744     ABLAVI Pascal      Aucun             [+]    │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

**Actions** :
- **Sélectionner** : Liste déroulante des employés existants
- **✓** : Valider l'affectation
- **✎** : Modifier l'affectation
- **+** : Créer un nouvel employé et affecter

### Composant React suggéré

```jsx
// Front/src/pages/agent/GestionLignesAffectation.jsx

export default function GestionLignesAffectation() {
  const [lignes, setLignes] = useState([])
  const [employes, setEmployes] = useState([])
  
  const affecterEmploye = async (ligneId, employeId) => {
    await api.post(`/billing/lines/${ligneId}/assigner_employe/`, {
      employe_id: employeId
    })
    // Recharger la liste
  }
  
  return (
    <div>
      <h1>Gestion des Affectations</h1>
      <table>
        <thead>
          <tr>
            <th>MSISDN</th>
            <th>Utilisateur</th>
            <th>Employé affecté</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {lignes.map(ligne => (
            <tr key={ligne.id}>
              <td>{ligne.msisdn}</td>
              <td>{ligne.utilisateur}</td>
              <td>
                <select 
                  value={ligne.employe?.id || ''}
                  onChange={(e) => affecterEmploye(ligne.id, e.target.value)}
                >
                  <option value="">-- Aucun --</option>
                  {employes.map(emp => (
                    <option key={emp.id} value={emp.id}>
                      {emp.first_name} {emp.last_name}
                    </option>
                  ))}
                </select>
              </td>
              <td>
                <button onClick={() => creerEtAffecter(ligne)}>
                  + Nouvel employé
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

---

## 📊 SCRIPT PYTHON POUR AFFECTATION EN MASSE

Si vous avez un fichier CSV avec les affectations :

**Format CSV** (`affectations.csv`) :
```csv
msisdn,email,prenom,nom,mot_de_passe
79300739,jean.dupont@wacem.tg,Jean,DUPONT,Pass123!
79300742,marie.agbo@wacem.tg,Marie,AGBO,Pass456!
79300744,pascal.ablavi@wacem.tg,Pascal,ABLAVI,Pass789!
```

**Script Python** (`Back/affectation_masse.py`) :
```python
import os
import django
import csv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()

from accounts.models import User
from billing.models import Line

def affecter_depuis_csv(fichier_csv):
    with open(fichier_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            msisdn = row['msisdn']
            email = row['email']
            prenom = row['prenom']
            nom = row['nom']
            mdp = row['mot_de_passe']
            
            # Créer ou récupérer l'employé
            employe, created = User.objects.get_or_create(
                username=msisdn,
                defaults={
                    'email': email,
                    'first_name': prenom,
                    'last_name': nom,
                    'role': 'EMPLOYE',
                    'telephone': msisdn,
                    'status': 'ACTIF'
                }
            )
            
            if created:
                employe.set_password(mdp)
                employe.save()
                print(f"✅ Employé créé : {prenom} {nom}")
            else:
                print(f"ℹ️  Employé existant : {prenom} {nom}")
            
            # Trouver et affecter la ligne
            try:
                ligne = Line.objects.get(msisdn=msisdn)
                ligne.employe = employe
                ligne.save()
                print(f"   ✅ Ligne {msisdn} affectée à {prenom} {nom}")
            except Line.DoesNotExist:
                print(f"   ❌ Ligne {msisdn} introuvable !")
            except Line.MultipleObjectsReturned:
                print(f"   ⚠️  Plusieurs lignes {msisdn} trouvées !")

if __name__ == '__main__':
    affecter_depuis_csv('affectations.csv')
    print("\n🎉 Affectation terminée !")
```

**Exécution** :
```bash
cd Back
python affectation_masse.py
```

---

## 🔍 VÉRIFICATIONS APRÈS AFFECTATION

### 1. Vérifier en base de données

```bash
cd Back
python manage.py shell
```

```python
from billing.models import Line

# Lignes affectées
lignes_ok = Line.objects.exclude(employe__isnull=True)
print(f"Lignes affectées : {lignes_ok.count()}")
for ligne in lignes_ok:
    print(f"  {ligne.msisdn} → {ligne.employe.first_name} {ligne.employe.last_name}")

# Lignes non affectées
lignes_ko = Line.objects.filter(employe__isnull=True)
print(f"\nLignes sans employé : {lignes_ko.count()}")
```

### 2. Tester la connexion employé

1. Aller sur `http://localhost:3000/login`
2. Entrer le MSISDN comme identifiant
3. Entrer le mot de passe
4. Se connecter
5. Aller sur "Mes factures"
6. Vérifier qu'il voit uniquement SES factures

### 3. Vérifier l'API

```bash
# Login employé
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"79300739","password":"Pass123!"}'

# Récupérer le token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Lister ses factures
curl -X GET http://localhost:8000/api/billing/invoices/ \
  -H "Authorization: Bearer $TOKEN"
```

**Résultat attendu** :
- Uniquement les factures de la ligne 79300739
- Aucune facture d'autres lignes

---

## ⚠️ ERREURS COURANTES

### Erreur 1 : "Ligne introuvable"

**Cause** : Le MSISDN n'existe pas dans la table `Line`.

**Solution** :
1. Vérifier que la ligne a bien été créée lors de l'upload du PDF
2. Vérifier l'orthographe du MSISDN (pas d'espace, pas de +228)

### Erreur 2 : "Employé déjà affecté à une autre ligne"

**Cause** : Un employé ne peut pas être affecté à plusieurs lignes (dans la version actuelle).

**Solution** :
1. Retirer l'affectation de l'ancienne ligne
2. Ou créer un nouveau compte employé si c'est une personne différente

### Erreur 3 : "Permission refusée"

**Cause** : L'utilisateur connecté n'a pas le rôle AGENT ou CHEF.

**Solution** :
1. Se connecter avec un compte ayant les bonnes permissions
2. Vérifier le rôle dans la base de données

### Erreur 4 : "L'employé ne voit aucune facture"

**Cause** : Plusieurs possibilités.

**Vérifications** :
```python
from accounts.models import User
from billing.models import Line, Invoice

employe = User.objects.get(username='79300739')
ligne = Line.objects.get(msisdn='79300739')

# 1. L'employé est-il bien affecté à la ligne ?
print(f"Ligne.employe = {ligne.employe}")  # Doit afficher l'employé

# 2. Y a-t-il des factures pour cette ligne ?
factures = Invoice.objects.filter(line=ligne)
print(f"Nombre de factures : {factures.count()}")  # Doit être > 0

# 3. Les factures sont-elles bien liées ?
for f in factures:
    print(f"  {f.numero_facture} - line={f.line}")  # line ne doit pas être None
```

---

## 📞 SUPPORT

En cas de difficulté, exécuter le script de test :

```bash
cd Back
python test_affectation_employe.py
```

Ce script affiche tous les détails et aide au diagnostic.

---

## ✅ CHECKLIST POUR UNE AFFECTATION RÉUSSIE

- [ ] L'entreprise existe dans la base
- [ ] Les lignes ont été importées (via upload PDF ou création manuelle)
- [ ] Le compte employé a été créé avec le rôle `EMPLOYE`
- [ ] Le username de l'employé = MSISDN de sa ligne
- [ ] L'affectation `ligne.employe = user` a été faite
- [ ] Les factures de cette ligne ont bien `invoice.line = ligne`
- [ ] L'employé peut se connecter avec son MSISDN
- [ ] L'employé voit uniquement ses factures

---

**Date** : 30 juillet 2026  
**Version** : 1.0  
**Auteur** : Équipe Moov Africa e-Billings  
**Projet** : Portail e-Billings - Moov Africa Togo

