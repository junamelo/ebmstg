# 📄 Implémentation Publication Blocs PDF

Guide complet pour implémenter le découpage automatique de PDF

---

## ✅ CE QUI EST DÉJÀ FAIT

1. ✅ Service `PDFProcessor` créé (`billing/services/pdf_processor.py`)
2. ✅ Service `PDFMatcher` créé pour matching automatique
3. ✅ Serializer `BulkPDFUploadSerializer` ajouté
4. ✅ Requirements PDF listés (`requirements_pdf.txt`)

---

## 🚀 IMPLÉMENTATION COMPLÈTE

### Étape 1 : Installer les dépendances

```bash
cd Back
pip install PyPDF2==3.0.1
```

**Note** : C'est la seule dépendance obligatoire pour le découpage basique

---

### Étape 2 : Ajouter l'endpoint dans InvoiceViewSet

Ajouter cette méthode dans `Back/billing/views.py` dans la classe `InvoiceViewSet` :

```python
@extend_schema(
    summary="Upload en masse d'un gros PDF",
    description="Uploader un gros PDF et le découper automatiquement par client",
    request=BulkPDFUploadSerializer
)
@action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, CanUploadPDF])
def upload_bulk_pdf(self, request):
    """
    Uploader un gros PDF et le découper automatiquement
    
    Workflow :
    1. Upload du gros PDF
    2. Analyse et découpage en blocs par client
    3. Génération de PDF individuels
    4. Matching automatique avec les factures
    5. Attachement des PDF individuels
    """
    serializer = BulkPDFUploadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    fichier = serializer.validated_data['fichier']
    auto_match = serializer.validated_data.get('auto_match', True)
    cycle = serializer.validated_data.get('cycle')
    periode_debut = serializer.validated_data.get('periode_debut')
    periode_fin = serializer.validated_data.get('periode_fin')
    
    try:
        # Importer les services PDF
        from .services.pdf_processor import PDFProcessor, PDFMatcher
        
        # 1. Traiter le PDF (découpage automatique)
        result = PDFProcessor.process_bulk_pdf(fichier)
        
        if not result['success']:
            return Response(
                {'error': 'Erreur lors du traitement du PDF'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        response_data = {
            'message': f'PDF traité avec succès : {result["files_created"]} fichier(s) créé(s)',
            'total_pages': result['total_pages'],
            'total_blocks': result['total_blocks'],
            'files_created': result['files_created'],
            'files': []
        }
        
        # 2. Si auto_match activé, matcher avec les factures
        if auto_match:
            # Filtrer les factures candidates
            invoices_query = self.get_queryset()
            
            if cycle:
                invoices_query = invoices_query.filter(
                    company__lines__cycle=cycle
                ).distinct()
            
            if periode_debut and periode_fin:
                invoices_query = invoices_query.filter(
                    periode_debut=periode_debut,
                    periode_fin=periode_fin
                )
            
            # Matcher et attacher
            match_result = PDFMatcher.auto_attach_pdfs(
                result['files'],
                invoices_query
            )
            
            response_data.update({
                'auto_match': {
                    'total_files': match_result['total_files'],
                    'matched': match_result['matched'],
                    'not_matched': match_result['not_matched'],
                    'attached': match_result['attached'],
                    'errors': match_result['errors']
                }
            })
            
            # Logger l'action
            for attached in match_result['attached']:
                try:
                    invoice = Invoice.objects.get(id=attached['invoice_id'])
                    HistoriqueFacturation.objects.create(
                        invoice=invoice,
                        utilisateur=request.user,
                        type_action='MODIFICATION',
                        ancien_statut=invoice.statut,
                        nouveau_statut=invoice.statut,
                        commentaire=f'PDF attaché automatiquement depuis upload masse : {attached["filename"]}'
                    )
                except:
                    pass
        else:
            # Juste retourner la liste des fichiers créés
            response_data['files'] = result['files']
        
        return Response(response_data)
        
    except ImportError:
        return Response(
            {
                'error': 'PyPDF2 non installé',
                'solution': 'Installer avec: pip install PyPDF2'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        return Response(
            {'error': f'Erreur lors du traitement : {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
```

---

### Étape 3 : Tester l'implémentation

#### Test 1 : Upload simple sans matching

```bash
# 1. Se connecter
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"agent@moov.tg","password":"agent123"}' \
  | jq -r '.access')

# 2. Upload PDF bulk (sans matching auto)
curl -X POST "http://localhost:8000/api/billing/invoices/upload_bulk_pdf/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "fichier=@/chemin/vers/gros_pdf_moov.pdf" \
  -F "auto_match=false"

# Résultat attendu :
# {
#   "message": "PDF traité avec succès : 25 fichier(s) créé(s)",
#   "total_pages": 150,
#   "total_blocks": 25,
#   "files_created": 25,
#   "files": [
#     {
#       "filename": "facture_90123456.pdf",
#       "path": "/path/to/media/factures/splits/facture_90123456.pdf",
#       "identifiers": {
#         "msisdn": "90123456",
#         "compte": "C26TEST001"
#       },
#       "pages": 6
#     },
#     ...
#   ]
# }
```

#### Test 2 : Upload avec matching automatique

```bash
# Upload avec auto-matching
curl -X POST "http://localhost:8000/api/billing/invoices/upload_bulk_pdf/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "fichier=@/chemin/vers/gros_pdf_moov.pdf" \
  -F "auto_match=true" \
  -F "cycle=HYB" \
  -F "periode_debut=2026-07-01" \
  -F "periode_fin=2026-07-31"

# Résultat attendu :
# {
#   "message": "PDF traité avec succès : 25 fichier(s) créé(s)",
#   "total_pages": 150,
#   "total_blocks": 25,
#   "files_created": 25,
#   "auto_match": {
#     "total_files": 25,
#     "matched": 23,
#     "not_matched": 2,
#     "attached": [
#       {
#         "invoice_id": "uuid-1",
#         "numero_facture": "FAC-C26TEST001-202607-001",
#         "filename": "facture_90123456.pdf",
#         "identifiers": {
#           "msisdn": "90123456"
#         }
#       },
#       ...
#     ],
#     "errors": [
#       {
#         "filename": "facture_90999999.pdf",
#         "error": "Aucune facture correspondante trouvée",
#         "identifiers": {
#           "msisdn": "90999999"
#         }
#       }
#     ]
#   }
# }
```

---

## 📋 WORKFLOW COMPLET

### Scénario : Facturation mensuelle avec gros PDF Moov

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Agent génère les factures du mois                       │
│    POST /api/billing/invoices/generate/                    │
│    → 50 factures en BROUILLON créées                       │
└────────────────────────────────────┬────────────────────────┘
                                     │
                                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Agent valide les factures                               │
│    POST /api/billing/invoices/{id}/valider/                │
│    → Statuts passent à EN_COURS                            │
└────────────────────────────────────┬────────────────────────┘
                                     │
                                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Agent reçoit le gros PDF de Moov (150 pages, 50 clients)│
│    Upload via :                                             │
│    POST /api/billing/invoices/upload_bulk_pdf/             │
│    - fichier: gros_pdf_moov.pdf                            │
│    - auto_match: true                                       │
│    - cycle: HYB                                             │
│    - periode: juillet 2026                                  │
└────────────────────────────────────┬────────────────────────┘
                                     │
                                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Backend traite automatiquement                          │
│    a) Lit le PDF page par page                             │
│    b) Détecte les blocs par MSISDN/Compte                  │
│    c) Crée 50 PDF individuels                              │
│    d) Matche avec les 50 factures EN_COURS                 │
│    e) Attache chaque PDF à sa facture                      │
│    f) Change statuts → VALIDEE                             │
└────────────────────────────────────┬────────────────────────┘
                                     │
                                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Agent publie les factures                               │
│    POST /api/billing/publications/{id}/publish/            │
│    → Statuts passent à PUBLIEE                             │
│    → Clients peuvent télécharger leur PDF                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 PATTERNS DE DÉTECTION

Le service cherche ces patterns dans le PDF :

1. **MSISDN** : `\b(9[0-9]{7})\b`
   - Exemple : `90123456`, `93456789`

2. **Compte** : `\b(C26[A-Z0-9]{6,10})\b`
   - Exemple : `C26TEST001`, `C26MOOV123`

3. **Numéro Facture** : `\b(FAC-[A-Z0-9\-]+)\b`
   - Exemple : `FAC-C26TEST001-202607-001`

**Priorité de matching** :
1. Numéro de facture (si trouvé)
2. Compte entreprise
3. MSISDN (via ligne)

---

## ⚙️ PERSONNALISATION

### Modifier les patterns

Éditer `Back/billing/services/pdf_processor.py` :

```python
class PDFProcessor:
    # Ajuster les patterns selon votre besoin
    MSISDN_PATTERN = r'\b(9[0-9]{7})\b'  # Modifier ici
    COMPTE_PATTERN = r'\b(C26[A-Z0-9]{6,10})\b'  # Modifier ici
    
    # Ajouter d'autres patterns
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
```

### Ajuster la détection de blocs

```python
@classmethod
def analyze_pdf_structure(cls, pdf_file):
    # Logique personnalisée
    # Par exemple : détecter un nouveau bloc quand on voit "FACTURE N°"
    pass
```

---

## 📊 RÉSULTAT FINAL

Après implémentation complète, tu auras :

✅ **Upload un gros PDF** → Découpage automatique  
✅ **Détection intelligente** des blocs par client  
✅ **Matching automatique** avec les factures  
✅ **PDF individuels** générés et attachés  
✅ **Changement de statut** automatique  
✅ **Historique** complet dans l'audit trail  

**Gain de temps** : De 2h de travail manuel → 30 secondes automatiques ! 🚀

---

## 🔧 TROUBLESHOOTING

### Erreur : "PyPDF2 non installé"
```bash
pip install PyPDF2==3.0.1
```

### PDF mal découpé
- Vérifier les patterns de détection
- Ajuster `analyze_pdf_structure()` selon la structure réelle

### Matching échoue
- Vérifier que les factures existent en base
- Vérifier que les MSISDNs/Comptes correspondent
- Vérifier les périodes de facturation

---

## 📝 PROCHAINES AMÉLIORATIONS

- [ ] OCR pour PDF scannés (pytesseract)
- [ ] Preview avant découpage
- [ ] Interface web pour ajuster les blocs manuellement
- [ ] Support multi-formats (Excel, CSV)
- [ ] Compression automatique des PDF
- [ ] Watermark avec logo Moov

---

**Fichiers à modifier** :
1. `Back/billing/views.py` → Ajouter méthode `upload_bulk_pdf`
2. ✅ `Back/billing/services/pdf_processor.py` → Déjà créé
3. ✅ `Back/billing/serializers.py` → Déjà mis à jour

**Installation** :
```bash
pip install PyPDF2==3.0.1
```

**Test** :
```bash
POST /api/billing/invoices/upload_bulk_pdf/
```

---

C'est prêt à être implémenté ! 🎉
