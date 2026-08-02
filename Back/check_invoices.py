"""Quick check of invoice status"""
import os, sys, django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()

from billing.models import Invoice

print(f"📊 Total invoices: {Invoice.objects.count()}")
print(f"✅ EN_COURS: {Invoice.objects.filter(statut='EN_COURS').count()}")
print(f"\n📋 Sample invoices (first 5):")
for inv in Invoice.objects.filter(statut='EN_COURS')[:5]:
    print(f"  - {inv.numero_facture} | {inv.company.raison_sociale}")
    print(f"    Comment: {inv.commentaire[:70]}")
