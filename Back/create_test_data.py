#!/usr/bin/env python3
"""
Script pour créer des données de test pour tester le matching PDF
"""
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
sys.path.append('.')

import django
django.setup()

from accounts.models import User
from billing.models import Company, Line, Invoice

def create_test_data():
    """Créer des données de test"""
    print("🔧 Création des données de test...")
    
    # 1. Créer un utilisateur agent de test
    agent, created = User.objects.get_or_create(
        email='agent@moov.tg',
        defaults={
            'username': 'agent@moov.tg',
            'first_name': 'Agent',
            'last_name': 'Test',
            'role': 'AGENT_FACTURATION',
            'is_active': True
        }
    )
    if created:
        agent.set_password('agent123')
        agent.save()
        print("✅ Agent de test créé")
    else:
        print("✅ Agent de test existe déjà")
    
    # 2. Créer un utilisateur payeur de test
    payeur, created = User.objects.get_or_create(
        email='payeur.test@moov.tg',
        defaults={
            'username': 'A26TEST001',
            'first_name': 'Payeur',
            'last_name': 'Test',
            'role': 'PAYEUR',
            'is_active': True
        }
    )
    if created:
        payeur.set_password('Moov@20260730')
        payeur.save()
        print("✅ Payeur de test créé")
    else:
        print("✅ Payeur de test existe déjà")
    
    # 3. Créer les entreprises de test
    companies_data = [
        {
            'compte': 'C26TEST001',
            'raison_sociale': 'ENTREPRISE ALPHA SARL',
            'nom_commercial': 'ALPHA',
            'categorie': 'PME',
            'adresse': '123 Rue de Lomé, Togo',
            'payeur': payeur
        },
        {
            'compte': 'C26TEST002',
            'raison_sociale': 'BETA CORPORATION',
            'nom_commercial': 'BETA CORP',
            'categorie': 'GRANDE_ENTREPRISE',
            'adresse': '456 Avenue Principale, Lomé',
            'payeur': payeur
        },
        {
            'compte': 'C26TEST003',
            'raison_sociale': 'GAMMA TECHNOLOGIES',
            'nom_commercial': 'GAMMA TECH',
            'categorie': 'PME',
            'adresse': '789 Boulevard Central, Kara',
            'payeur': payeur
        }
    ]
    
    companies = []
    for company_data in companies_data:
        company, created = Company.objects.get_or_create(
            compte=company_data['compte'],
            defaults=company_data
        )
        companies.append(company)
        if created:
            print(f"✅ Entreprise créée : {company.raison_sociale}")
        else:
            print(f"✅ Entreprise existe : {company.raison_sociale}")
    
    # 4. Créer les lignes de test
    lines_data = [
        {
            'company': companies[0],
            'msisdn': '90123456',
            'utilisateur': 'Directeur ALPHA',
            'forfait': Decimal('25000'),
            'cycle': 'HYB'
        },
        {
            'company': companies[1],
            'msisdn': '93456789',
            'utilisateur': 'PDG BETA',
            'forfait': Decimal('30000'),
            'cycle': 'HYB'
        },
        {
            'company': companies[2],
            'msisdn': '96789012',
            'utilisateur': 'CTO GAMMA',
            'forfait': Decimal('35000'),
            'cycle': 'HYB'
        }
    ]
    
    lines = []
    for line_data in lines_data:
        line, created = Line.objects.get_or_create(
            msisdn=line_data['msisdn'],
            defaults=line_data
        )
        lines.append(line)
        if created:
            print(f"✅ Ligne créée : {line.msisdn} ({line.company.raison_sociale})")
        else:
            print(f"✅ Ligne existe : {line.msisdn} ({line.company.raison_sociale})")
    
    # 5. Créer les factures de test (statut EN_COURS pour matching)
    periode_debut = datetime(2026, 7, 1).date()
    periode_fin = datetime(2026, 7, 31).date()
    date_echeance = periode_fin + timedelta(days=30)
    
    factures_data = [
        {
            'company': companies[0],
            'numero_facture': 'FAC-C26TEST001-202607-001',
            'periode_debut': periode_debut,
            'periode_fin': periode_fin,
            'montant_ht': Decimal('25000'),
            'montant_tva': Decimal('4500'),
            'montant_ttc': Decimal('29500'),
            'date_echeance': date_echeance,
            'statut': 'EN_COURS'
        },
        {
            'company': companies[1],
            'numero_facture': 'FAC-C26TEST002-202607-001',
            'periode_debut': periode_debut,
            'periode_fin': periode_fin,
            'montant_ht': Decimal('30000'),
            'montant_tva': Decimal('5400'),
            'montant_ttc': Decimal('35400'),
            'date_echeance': date_echeance,
            'statut': 'EN_COURS'
        },
        {
            'company': companies[2],
            'numero_facture': 'FAC-C26TEST003-202607-001',
            'periode_debut': periode_debut,
            'periode_fin': periode_fin,
            'montant_ht': Decimal('35000'),
            'montant_tva': Decimal('6300'),
            'montant_ttc': Decimal('41300'),
            'date_echeance': date_echeance,
            'statut': 'EN_COURS'
        }
    ]
    
    factures = []
    for facture_data in factures_data:
        facture, created = Invoice.objects.get_or_create(
            numero_facture=facture_data['numero_facture'],
            defaults=facture_data
        )
        factures.append(facture)
        if created:
            print(f"✅ Facture créée : {facture.numero_facture} ({facture.company.raison_sociale}) - {facture.statut}")
        else:
            print(f"✅ Facture existe : {facture.numero_facture} ({facture.company.raison_sociale}) - {facture.statut}")
    
    print(f"\n🎯 RÉSUMÉ DES DONNÉES DE TEST :")
    print(f"   📊 {len(companies)} entreprises créées")
    print(f"   📞 {len(lines)} lignes créées")
    print(f"   📄 {len(factures)} factures créées (statut EN_COURS)")
    print(f"   👤 1 agent et 1 payeur")
    
    print(f"\n🔐 COMPTES DE TEST :")
    print(f"   Agent : agent@moov.tg / agent123")
    print(f"   Payeur : payeur.test@moov.tg / Moov@20260730")
    
    print(f"\n🚀 PRÊT POUR TEST :")
    print(f"   1. Serveur : http://localhost:8000")
    print(f"   2. PDF test : media/test_bulk_moov.pdf")
    print(f"   3. Endpoint : POST /api/billing/invoices/upload_bulk_pdf/")
    print(f"   4. Les 3 factures sont EN_COURS → deviendront VALIDEE après matching")

if __name__ == "__main__":
    create_test_data()