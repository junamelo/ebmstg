# 📄 Statut Upload PDF - Phase 4

Date : 30 juillet 2026

---

## ✅ Ce qui Fonctionne

### 1. Upload Basique de PDF

**Endpoint disponible** : `POST /api/billing/invoices/{id}/attach_pdf/`

**Ce qui est implémenté** :
- ✅ Upload de fichier PDF
- ✅ Validation format (doit être .pdf)
- ✅ Validation taille (max 50 Mo)
- ✅ Sauvegarde dans `media/factures/`
- ✅ Association à la facture
- ✅ Changement statut automatique (EN_COURS → VALIDEE)
- ✅ Historique créé
- ✅ Configuration MEDIA_ROOT et MEDIA_URL
- ✅ **[CORRIGÉ]** URLs pour servir les fichiers media en dev

### 2. Téléchargement PDF

**Accès au PDF** :
- URL générée automatiquement : `http://localhost:8000/media/factures/{filename}.pdf`
- Accessible via le champ `fichier_pdf` dans la réponse API

---

## 🧪 Test de l'Upload PDF

### Prérequis
```bash
cd Back
python manage.py runserver
```

### Test avec curl

```bash
# 1. Se connecter
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"agent@moov.tg","password":"agent123"}' \
  | jq -r '.access')

# 2. Créer une facture (si pas existante)
INVOICE_ID=$(curl -X POST http://localhost:8000/api/billing/invoices/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company": 1,
    "numero_facture": "FAC-TEST-001",
    "periode_debut": "2026-07-01",
    "periode_fin": "2026-07-31",
    "montant_ht": "10000",
    "montant_tva": "1800",
    "montant_ttc": "11800",
    "date_echeance": "2026-08-30"
  }' | jq -r '.id')

# 3. Passer la facture en EN_COURS
curl -X POST "http://localhost:8000/api/billing/invoices/$INVOICE_ID/valider/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"commentaire":"Test"}'

# 4. Upload PDF
curl -X POST "http://localhost:8000/api/billing/invoices/$INVOICE_ID/attach_pdf/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "fichier=@/chemin/vers/votre/facture.pdf"

# Résultat attendu :
# {
#   "message": "PDF attaché avec succès",
#   "facture": {
#     "id": "...",
#     "numero_facture": "FAC-TEST-001",
#     "statut": "VALIDEE",
#     "fichier_pdf": "/media/factures/facture_xyz.pdf",
#     ...
#   }
# }
```

### Test avec Swagger UI

1. Aller sur http://localhost:8000/api/docs/
2. Se connecter (Authorize)
3. Aller à `POST /api/billing/invoices/{id}/attach_pdf/`
4. Cliquer "Try it out"
5. Entrer l'ID de la facture
6. Cliquer "Choose File" et sélectionner un PDF
7. Cliquer "Execute"

### Vérifier l'upload

```bash
# Vérifier que le fichier existe
ls -la Back/media/factures/

# Télécharger le PDF
curl http://localhost:8000/media/factures/{filename}.pdf -o test.pdf
```

---

## ❌ Ce qui N'est PAS Implémenté (Phase 4.1 Future)

### Découpage Automatique de PDF

**Ce qui manque** :
- ❌ Upload d'un PDF multi-pages
- ❌ Extraction automatique par MSISDN/pattern
- ❌ Génération de PDF individuels par ligne
- ❌ Compression automatique
- ❌ OCR pour extraction de texte

**Librairies nécessaires** :
```python
pip install PyPDF2      # Manipulation PDF
pip install pdf2image   # Conversion PDF → Images
pip install pytesseract # OCR (nécessite Tesseract)
```

**Implémentation future** :
```python
# Back/billing/services/pdf_processing.py
class PDFProcessor:
    def split_pdf_by_msisdn(self, pdf_file):
        """Découper un PDF par MSISDN"""
        pass
    
    def extract_text_from_page(self, page):
        """Extraire texte d'une page"""
        pass
    
    def find_msisdn_in_text(self, text):
        """Trouver MSISDN dans le texte"""
        pass
    
    def create_individual_pdf(self, pages, output_path):
        """Créer PDF individuel"""
        pass
```

---

## 🎯 État Actuel

### ✅ Fonctionnel
- Upload simple de PDF (1 fichier → 1 facture)
- Validation et sauvegarde
- Association à la facture
- Téléchargement via URL

### ⚠️ Limitations Actuelles
- Pas de découpage automatique
- Pas d'extraction par MSISDN
- Pas de compression
- Upload manuel (1 par 1)

---

## 📋 Exemple Workflow Complet

### Scénario : Facturation Mensuelle avec PDF

```bash
# 1. Générer factures du mois
POST /api/billing/invoices/generate/
{
  "cycle": "HYB",
  "periode_debut": "2026-07-01",
  "periode_fin": "2026-07-31"
}
# → 50 factures créées en BROUILLON

# 2. Valider les factures
for each invoice:
    POST /api/billing/invoices/{id}/valider/

# 3. Attacher les PDF (manuellement pour l'instant)
for each invoice:
    POST /api/billing/invoices/{id}/attach_pdf/
    {
      "fichier": [PDF file]
    }
    # → Statut passe à VALIDEE

# 4. Publier toutes les factures
POST /api/billing/publications/
POST /api/billing/publications/{pub-id}/publish/
{
  "invoice_ids": ["uuid1", "uuid2", ...]
}
# → Statuts passent à PUBLIEE

# 5. Les clients peuvent télécharger leur PDF
GET /api/billing/invoices/{id}/
# → Réponse contient "fichier_pdf": "/media/factures/xxx.pdf"
# Client peut télécharger : http://localhost:8000/media/factures/xxx.pdf
```

---

## 🚀 Prochaines Étapes (Phase 4.1)

### Court Terme
1. ✅ **Upload basique** - FAIT
2. ⏳ **Tests upload** - À faire
3. ⏳ **Endpoint téléchargement sécurisé** - À faire

### Moyen Terme (Phase 4.1)
1. ⏳ **Service découpage PDF**
2. ⏳ **Extraction MSISDN automatique**
3. ⏳ **Génération PDF individuels**
4. ⏳ **Compression automatique**

### Long Terme
1. ⏳ **Upload en masse (drag & drop)**
2. ⏳ **Preview PDF dans l'interface**
3. ⏳ **Signature électronique PDF**
4. ⏳ **Watermark automatique**

---

## 📊 Résumé

| Fonctionnalité | Statut | Phase |
|----------------|--------|-------|
| Upload PDF simple | ✅ FAIT | Phase 4 |
| Configuration media | ✅ FAIT | Phase 4 |
| Validation fichier | ✅ FAIT | Phase 4 |
| Sauvegarde BD | ✅ FAIT | Phase 4 |
| Téléchargement | ✅ FAIT | Phase 4 |
| Découpage auto | ❌ TODO | Phase 4.1 |
| Extraction MSISDN | ❌ TODO | Phase 4.1 |
| PDF individuels | ❌ TODO | Phase 4.1 |
| Compression | ❌ TODO | Phase 4.1 |

---

## ✅ Conclusion

**L'upload basique de PDF fonctionne** ✅

Tu peux dès maintenant :
1. Uploader un PDF sur une facture
2. Le fichier sera sauvegardé dans `media/factures/`
3. Le statut de la facture changera automatiquement
4. Le PDF sera accessible via l'URL retournée

**Limitations** : Pas de découpage automatique pour l'instant (nécessite Phase 4.1)

---

**Pour tester** : Voir section "🧪 Test de l'Upload PDF" ci-dessus
