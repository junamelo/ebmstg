"""Préparer les données pour le test manuel Phase 4"""
import os, sys, django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()

from decimal import Decimal
from datetime import date
from billing.models import Company, Line, Invoice
from accounts.models import User

print("🚀 Préparation des données de test pour Phase 4\n")

# 1. Vérifier/créer le payeur et l'entreprise
payeur, created = User.objects.get_or_create(
    username='cafe_payeur',
    defaults={
        'email': 'cafe.payeur@test.com',
        'role': 'PAYEUR'
    }
)
if created:
    payeur.set_password('test123')
    payeur.save()
    print(f"✅ Payeur créé: {payeur.username}")
else:
    print(f"ℹ️  Payeur existant: {payeur.username}")

company, created = Company.objects.get_or_create(
    compte='A0000009',
    defaults={
        'raison_sociale': 'CAFE INFORMATIQUE ET TEL',
        'payeur': payeur
    }
)
if created:
    print(f"✅ Entreprise créée: {company.raison_sociale}")
else:
    print(f"ℹ️  Entreprise existante: {company.raison_sociale}")

# 2. Créer les employés et lignes
employees_data = [
    {'username': 'marie.noagbodji', 'email': 'marie.n@cafe.test', 'msisdn': '99475555', 'forfait': '9998'},
    {'username': 'jean.noagbodji', 'email': 'jean.n@cafe.test', 'msisdn': '99478787', 'forfait': '36475'},
    {'username': 'secretariat.tech', 'email': 'secretariat@cafe.test', 'msisdn': '99492454', 'forfait': '19280'},
]

lines_created = []
for emp_data in employees_data:
    # Créer l'employé
    employe, created = User.objects.get_or_create(
        username=emp_data['username'],
        defaults={
            'email': emp_data['email'],
            'role': 'EMPLOYE'
        }
    )
    if created:
        employe.set_password('test123')
        employe.save()
        print(f"✅ Employé créé: {employe.username}")
    else:
        print(f"ℹ️  Employé existant: {employe.username}")
    
    # Créer la ligne
    line, created = Line.objects.get_or_create(
        company=company,
        msisdn=emp_data['msisdn'],
        defaults={
            'employe': employe,
            'forfait': Decimal(emp_data['forfait']),
            'cycle': 'HYB'
        }
    )
    if created:
        print(f"✅ Ligne créée: {line.msisdn} → {employe.username}")
        lines_created.append(line)
    else:
        print(f"ℹ️  Ligne existante: {line.msisdn}")
        lines_created.append(line)

# 3. Créer les factures EN_COURS (une par ligne)
print(f"\n📄 Création des factures EN_COURS...")
invoices_created = []

for i, line in enumerate(lines_created):
    numero_facture = f"A20260601041-{line.msisdn}"
    
    invoice, created = Invoice.objects.get_or_create(
        numero_facture=numero_facture,
        defaults={
            'company': company,
            'line': line,
            'periode_debut': date(2026, 6, 1),
            'periode_fin': date(2026, 6, 30),
            'montant_ht': line.forfait,
            'montant_tva': line.forfait * Decimal('0.18'),
            'montant_ttc': line.forfait * Decimal('1.18'),
            'date_echeance': date(2026, 7, 30),
            'statut': 'EN_COURS',
            'commentaire': f'Facture de test pour ligne {line.msisdn} - Juin 2026'
        }
    )
    if created:
        print(f"  ✅ Facture créée: {invoice.numero_facture} | {invoice.statut} | {invoice.montant_ttc} FCFA")
        invoices_created.append(invoice)
    else:
        # Mettre à jour le statut si elle existe mais est déjà traitée
        if invoice.statut != 'EN_COURS':
            print(f"  ⚠️  Facture {invoice.numero_facture} existe avec statut {invoice.statut}")
        else:
            print(f"  ℹ️  Facture existante: {invoice.numero_facture} | {invoice.statut}")
            invoices_created.append(invoice)

# 4. Vérifier l'agent de facturation
agent, created = User.objects.get_or_create(
    username='agent_factu',
    defaults={
        'email': 'agent.factu@moov.test',
        'role': 'AGENT_FACTURATION'
    }
)
if created:
    agent.set_password('test123')
    agent.save()
    print(f"\n✅ Agent créé: {agent.username}")
else:
    print(f"\nℹ️  Agent existant: {agent.username}")

# 5. Résumé
print(f"\n" + "="*60)
print(f"📊 RÉSUMÉ - Données prêtes pour test manuel")
print(f"="*60)
print(f"🏢 Entreprise: {company.raison_sociale} (Compte: {company.compte})")
print(f"👤 Payeur: {payeur.username} / Mot de passe: test123")
print(f"🔧 Agent: {agent.username} / Mot de passe: test123")
print(f"")
print(f"📱 Lignes créées: {len(lines_created)}")
for line in lines_created:
    print(f"  - {line.msisdn} ({line.employe.username if line.employe else 'Sans employé'})")
print(f"")
print(f"📄 Factures EN_COURS créées: {len(invoices_created)}")
for inv in invoices_created:
    print(f"  - {inv.numero_facture} | {inv.montant_ttc} FCFA")
print(f"")
print(f"📂 PDF de test: C:\\Users\\Benoit\\Documents\\BURRO\\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026\\Contexte\\testPDF\\PHYS.OPN.202606.GLO-1-70.pdf")
print(f"")
print(f"🔗 Frontend: http://localhost:3001/")
print(f"🔗 Backend: http://127.0.0.1:8000/")
print(f"="*60)
