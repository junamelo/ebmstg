"""
Script pour créer des factures de test correspondant au PDF SOM
IMPORTANT: Ce script crée 1 facture PAR LIGNE (individuelle) pour matcher avec le PDF SOMMAIRE
où chaque page correspond à un employé/MSISDN différent.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()

from billing.models import Company, Line, Invoice
from accounts.models import User
from datetime import datetime

def create_test_data():
    """Créer les données de test pour le PDF SOM"""
    
    # Récupérer l'agent pour l'attribution
    try:
        agent = User.objects.filter(role='AGENT_FACTURATION').first()
        if not agent:
            print("❌ Aucun agent trouvé. Créez un agent d'abord.")
            return
    except:
        print("❌ Erreur lors de la récupération de l'agent")
        return
    
    print("🏗️  Création des données de test...\n")
    
    # Données extraites du PDF
    companies_data = [
        {
            'compte': 'A0000009',
            'raison_sociale': 'CAFE INFORMATIQUE ET TEL',
            'categorie': 'GE',
            'adresse': 'Rte de Kpalimé, Adidogomé, cité Maman N\'danida',
            'adresse2': '07 BP: 12596',
            'lignes': [
                {'msisdn': '99475555', 'utilisateur': 'NOAGBODJI MARIE'},
                {'msisdn': '99478787', 'utilisateur': 'NOAGBODJI JEAN MARIE'},
                {'msisdn': '99492454', 'utilisateur': 'SECRETARIAT TECHNIQUE'},
            ]
        },
        {
            'compte': 'A0000011',
            'raison_sociale': 'CAURIS MANAGEMENT',
            'categorie': 'GE',
            'adresse': '68 Avenue de la Libération, BP:1172 Lomé Togo',
            'adresse2': '',
            'lignes': [
                {'msisdn': '99421137', 'utilisateur': 'CAURIS MANAGEMENT'},
                {'msisdn': '99421146', 'utilisateur': 'CAURIS MANAGEMENT'},
                {'msisdn': '99426714', 'utilisateur': 'YAWO NOEL EKLO'},
                {'msisdn': '99520226', 'utilisateur': 'CAURIS MANAGEMENT'},
            ]
        },
        {
            'compte': 'A0000039',
            'raison_sociale': 'LABOREX TOGO',
            'categorie': 'GE',
            'adresse': 'Rue des Hydrocarbures à côté de TOGO GAZ',
            'adresse2': '01BP:1653',
            'lignes': [
                {'msisdn': '97525353', 'utilisateur': 'LABOREX TOGO'},
                {'msisdn': '99672121', 'utilisateur': 'LABOREX TOGO'},
            ]
        },
        {
            'compte': 'A0000049',
            'raison_sociale': 'CFAO MOBILITY TOGO SA',
            'categorie': 'GE',
            'adresse': 'BD EYADEMA, BP:332 LOME-TOGO',
            'adresse2': '',
            'lignes': [
                {'msisdn': '99453100', 'utilisateur': 'CFAO MOBILITY TOGO SA'},
            ]
        },
        {
            'compte': 'A0000101',
            'raison_sociale': 'VIVI ROYALE',
            'categorie': 'PE',
            'adresse': '41 Rue des Moissons, Mson Vivi Royale Nyékonakpoé',
            'adresse2': '',
            'lignes': [
                {'msisdn': '99476053', 'utilisateur': 'ADJAMAGBO VIVI'},
            ]
        },
        {
            'compte': 'A0000106',
            'raison_sociale': 'WACEM SA',
            'categorie': 'GE',
            'adresse': 'BP:07 Tabligbo TOGO, West Africa /BP:9159 Lomé',
            'adresse2': 'franckaf1.wacem@gmail.com',
            'lignes': [
                {'msisdn': '79300739', 'utilisateur': 'WACEM SA'},
                {'msisdn': '79300742', 'utilisateur': 'WACEM SA'},
                {'msisdn': '79300744', 'utilisateur': 'WACEM SA'},
                {'msisdn': '79300746', 'utilisateur': 'WACEM'},
                {'msisdn': '79302368', 'utilisateur': 'WACEM SA'},
                {'msisdn': '79302369', 'utilisateur': 'WACEM SA'},
                {'msisdn': '79302370', 'utilisateur': 'WACEM SA'},
                {'msisdn': '79603053', 'utilisateur': 'WACEM SA'},
                {'msisdn': '79603054', 'utilisateur': 'WACEM SA'},
            ]
        },
    ]
    
    created_companies = 0
    created_lines = 0
    created_invoices = 0
    
    for company_data in companies_data:
        # Créer ou récupérer l'entreprise
        company, created = Company.objects.get_or_create(
            compte=company_data['compte'],
            defaults={
                'raison_sociale': company_data['raison_sociale'],
                'categorie': company_data['categorie'],
                'adresse': company_data['adresse'],
                'adresse2': company_data['adresse2'],
                'statut': 'ACTIF',
            }
        )
        
        if created:
            created_companies += 1
            print(f"✅ Entreprise créée : {company.raison_sociale} ({company.compte})")
        else:
            print(f"ℹ️  Entreprise existante : {company.raison_sociale} ({company.compte})")
        
        # Créer les lignes ET une facture par ligne (pour PDF SOM)
        for idx, ligne_data in enumerate(company_data['lignes']):
            line, created = Line.objects.get_or_create(
                msisdn=ligne_data['msisdn'],
                defaults={
                    'company': company,
                    'utilisateur': ligne_data['utilisateur'],
                    'cycle': 'OP',  # OPEN d'après le PDF
                    'statut': 'ACTIF',
                    'forfait': '0',
                }
            )
            
            if created:
                created_lines += 1
                print(f"   📞 Ligne créée : {line.msisdn} - {line.utilisateur}")
            
            # Créer une facture INDIVIDUELLE pour cette ligne (SOM = 1 facture/employé)
            invoice_number = f"A202606{ligne_data['msisdn']}"  # Numéro unique par MSISDN
            invoice, inv_created = Invoice.objects.get_or_create(
                numero_facture=invoice_number,
                defaults={
                    'company': company,
                    'periode_debut': datetime(2026, 6, 1).date(),
                    'periode_fin': datetime(2026, 6, 30).date(),
                    'date_echeance': datetime(2026, 7, 30).date(),
                    'montant_ht': 5000,  # Montant fictif
                    'montant_tva': 900,   # TVA 18%
                    'montant_ttc': 5900,
                    'statut': 'EN_COURS',  # Prêt pour attachement PDF
                    'commentaire': f'Facture individuelle pour {ligne_data["utilisateur"]} - {ligne_data["msisdn"]}',
                }
            )
            
            if inv_created:
                created_invoices += 1
                print(f"      📄 Facture créée : {invoice.numero_facture}")
    
    print(f"\n{'='*60}")
    print(f"✅ Création terminée !")
    print(f"   Entreprises créées : {created_companies}")
    print(f"   Lignes créées : {created_lines}")
    print(f"   Factures créées : {created_invoices}")
    print(f"{'='*60}")
    print("\n🎯 Vous pouvez maintenant uploader le PDF à nouveau !")

if __name__ == "__main__":
    create_test_data()
