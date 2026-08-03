# Changelog - Corrections Bugs Urgents
**Date :** 2 août 2026

## Frontend

### `Front/src/pages/admin/AdminDashboard.jsx`
**BUG 5 - Écran blanc quand stats null**
- Ajout état `erreur` et fonction `chargerStats()`
- Écran d'erreur avec bouton "Réessayer"
- Valeurs par défaut sûres : `stats?.totalContrats || 0`
- Tableau connexions : vérification `stats?.dernieresConnexions || []`
- Message "Aucune connexion récente" si tableau vide

### `Front/src/pages/simulation/Simulation.jsx`
**BUG 4 - Services vides pour employé**
- Mapping API → interface : `tarifs` → `options`
  ```js
  options: srv.tarifs.map(tarif => ({
    id: tarif.id,
    nom: tarif.nom_option,
    tarif: parseFloat(tarif.prix),
    actif: tarif.est_actif
  }))
  ```
- Filtrage services sans options actives
- Messages d'état vide pour HYBRIDE et OPEN
- Logs de débogage pour suivi chargement

### `Front/src/pages/agent/DetailContrat.jsx`
**BUG 3 - Ajout ligne échoue**
- Correction champs envoyés à l'API :
  ```js
  {
    company: parseInt(id),
    msisdn: '...',
    utilisateur: '...',
    cycle: 'HYB' | 'OP',
    forfait: 0,
    option_blackberry: '',
    option_nolimit: '',
    est_incognito: false,
    facture_detaillee: false,
    est_non_revenu: false
  }
  ```
- Suppression champ `est_active` (non accepté par serializer)
- Reset formulaire après succès
- Message d'erreur MSISDN existant

---

## Tests

### Résultats
```bash
# Backend
python manage.py check
✅ System check identified no issues (0 silenced)

python manage.py test
✅ Ran 97 tests in 320.454s - OK

# Frontend
npm run build
✅ built in 10.79s
```

### Détail tests Django
- `accounts/test_auth.py` : 10 tests authentification
- `billing/test_affectation.py` : 11 tests affectation employé
- `billing/test_publication.py` : tests publication PDF
- `billing/tests.py` : tests modèles, viewsets, permissions

---

## Règles Métier Préservées

✅ Import PDF → factures restent **VALIDEE** (pas PUBLIEE)  
✅ Publication finale → action explicite → **VALIDEE** → **PUBLIEE**  
✅ Clients voient uniquement factures **PUBLIEE**  
✅ Employé voit ses factures via `line__employe=user`  
✅ Validation inter-entreprise pour affectation employé  
✅ Lecture API autorisée pour simulation employés  
✅ Écriture réservée aux agents/chefs/admins

---

## APIs Utilisées

| Endpoint | Méthode | Usage | Permission |
|----------|---------|-------|------------|
| `/api/billing/packages/` | GET | Charger forfaits | Authentifié |
| `/api/billing/services/` | GET | Charger services | Authentifié |
| `/api/billing/tarifs/` | GET | Charger tarifs | Authentifié |
| `/api/billing/lines/` | POST | Ajouter ligne | Agent/Chef/Admin |
| `/api/billing/lines/{id}/assigner_employe/` | POST | Affecter employé | Agent/Chef/Admin |
| `/api/billing/stats/admin/` | GET | Stats admin | Admin |
| `/api/auth/users/?role=EMPLOYE` | GET | Lister employés | Agent/Chef/Admin |

---

## Points d'Attention

1. **AdminDashboard :** Surveiller temps de réponse `/api/billing/stats/admin/`
2. **Simulation :** Vérifier que services et tarifs actifs existent en base
3. **Ajout ligne :** Valider MSISDN unique côté backend (ValidationError)
4. **Affectation :** Bloquer affectation inter-entreprise (validation backend)

---

## Prochaines Actions

**Tests manuels obligatoires :**
- [ ] Admin : Dashboard stats et erreur API
- [ ] Agent : Forfaits, ajout ligne, affectation employé
- [ ] Employé : Simulation HYBRIDE et OPEN
- [ ] Payeur : Accès limité entreprise
- [ ] Chef : Publication factures

**Si tests manuels OK :**
✅ Tous les bugs urgents sont résolus et validés
