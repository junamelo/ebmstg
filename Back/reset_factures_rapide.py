"""
Script RAPIDE pour vider les factures - sans confirmation
⚠️  ATTENTION : Supprime TOUT immédiatement !
"""
import os
import sys
import django
import shutil
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()

from billing.models import Invoice, NotificationFacture, HistoriqueFacturation, Publication
from django.conf import settings

print("\n🗑️  Suppression rapide des factures...")

# Compter
nb_invoices = Invoice.objects.count()
nb_notifications = NotificationFacture.objects.count()
nb_historique = HistoriqueFacturation.objects.count()
nb_publications = Publication.objects.count()

# Supprimer les fichiers
media_root = Path(settings.MEDIA_ROOT)
for folder in ['factures', 'publications']:
    folder_path = media_root / folder
    if folder_path.exists():
        shutil.rmtree(folder_path)
        folder_path.mkdir(parents=True, exist_ok=True)

# Supprimer en base
NotificationFacture.objects.all().delete()
HistoriqueFacturation.objects.all().delete()
Publication.objects.all().delete()
Invoice.objects.all().delete()

print(f"✅ Supprimé : {nb_invoices} factures, {nb_notifications} notifications")
print(f"✅ Prêt pour de nouveaux tests !")
