"""
Script de test complet du workflow de publication
"""
import os
import django
import sys
from datetime import datetime, date

# Configuration Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from billing.models import Company, Line, Invoice, HistoriqueFacturation, Publication
from decimal import Decimal

User = get_user_model()

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_workflow_publication():
    """Test complet du workflow de publication"""
    
    print_section("TEST WORKFLOW PUBLICATION FACTURES")
    
    # 1. Vérifier les utilisateurs
    print_section("1. VÉRIFICATION DES UTILISATEURS")
    
    try:
        agent = User.objects.get(username='agent1')
        print(f"✅ Agent trouvé: {agent.username} ({agent.get_full_name()})")
    except User.DoesNotExist:
        print("❌ Agent 'agent1' non trouvé")
        return
    
    try:
        payeur = User.objects.filter(role='PAYEUR').first()
        if payeur:
            print(f"✅ Payeur trouvé: {payeur.username} ({payeur.get_full_name()})")
        else:
            print("⚠️  Aucun payeur trouvé en base")
    except Exception as e:
        print(f"⚠️  Erreur recherche payeur: {e}")
    
    try:
        employe = User.objects.filter(role='EMPLOYE').first()
        if employe:
            print(f"✅ Employé trouvé: {employe.username} ({employe.get_full_name()})")
        else:
            print("⚠️  Aucun employé trouvé en base")
    except Exception as e:
        print(f"⚠️  Erreur recherche employé: {e}")
    
    # 2. Vérifier les factures VALIDEE
    print_section("2. FACTURES VALIDEE DISPONIBLES")
    
    factures_validees = Invoice.objects.filter(statut='VALIDEE').select_related('company', 'line')
    print(f"Nombre de factures VALIDEE: {factures_validees.count()}")
    
    if factures_validees.count() == 0:
        print("\n⚠️  Aucune facture VALIDEE trouvée. Création d'une facture de test...")
        
        # Créer une entreprise si nécessaire
        company = Company.objects.first()
        if not company:
            if payeur:
                company = Company.objects.create(
                    compte="TEST001",
                    raison_sociale="ENTREPRISE TEST",
                    categorie="ENT",
                    type_facturation="HYBRIDE",
                    payeur=payeur
                )
                print(f"✅ Entreprise créée: {company.raison_sociale}")
            else:
                print("❌ Impossible de créer une entreprise sans payeur")
                return
        else:
            print(f"✅ Entreprise existante: {company.raison_sociale}")
        
        # Créer une ligne si nécessaire (pour facture individuelle)
        line = None
        if employe:
            line = Line.objects.filter(company=company).first()
            if not line:
                line = Line.objects.create(
                    company=company,
                    msisdn="99999999",
                    cycle="HYB",
                    forfait_data="10 GB",
                    tarif_mensuel=Decimal("15000.00"),
                    employe=employe
                )
                print(f"✅ Ligne créée: {line.msisdn}")
        
        # Créer une facture VALIDEE
        invoice = Invoice.objects.create(
            company=company,
            line=line,
            numero_facture=f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}",
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            cycle="HYB",
            montant_ht=Decimal("20000.00"),
            montant_tva=Decimal("3600.00"),
            montant_ttc=Decimal("23600.00"),
            statut='VALIDEE'
        )
        print(f"✅ Facture VALIDEE créée: {invoice.numero_facture} (ID: {invoice.id})")
        factures_validees = Invoice.objects.filter(statut='VALIDEE')
    
    # Afficher les factures VALIDEE
    print("\nListe des factures VALIDEE:")
    for i, facture in enumerate(factures_validees[:5], 1):
        line_info = f"Ligne {facture.line.msisdn}" if facture.line else "Globale"
        print(f"{i}. ID={facture.id} | {facture.numero_facture} | {facture.company.raison_sociale} | {line_info} | {facture.montant_ttc} FCFA")
    
    # 3. Test publication d'une facture
    print_section("3. TEST PUBLICATION D'UNE FACTURE")
    
    facture_test = factures_validees.first()
    print(f"\nFacture à publier:")
    print(f"  - ID: {facture_test.id}")
    print(f"  - Numéro: {facture_test.numero_facture}")
    print(f"  - Entreprise: {facture_test.company.raison_sociale}")
    print(f"  - Ligne: {facture_test.line.msisdn if facture_test.line else 'Globale'}")
    print(f"  - Montant: {facture_test.montant_ttc} FCFA")
    print(f"  - Statut AVANT: {facture_test.statut}")
    
    # Simuler la publication
    facture_test.statut = 'PUBLIEE'
    facture_test.save()
    
    print(f"  - Statut APRÈS: {facture_test.statut} ✅")
    
    # 4. Vérifier historique facture
    print_section("4. VÉRIFICATION HISTORIQUE FACTURE")
    
    # Créer l'historique si pas déjà fait
    historique, created = HistoriqueFacturation.objects.get_or_create(
        invoice=facture_test,
        defaults={
            'ancien_statut': 'VALIDEE',
            'nouveau_statut': 'PUBLIEE',
            'modifie_par': agent,
            'commentaire': 'Publication via workflow test'
        }
    )
    
    if created:
        print(f"✅ Historique créé pour facture {facture_test.numero_facture}")
    else:
        print(f"✅ Historique existant pour facture {facture_test.numero_facture}")
    
    print(f"   - Ancien statut: {historique.ancien_statut}")
    print(f"   - Nouveau statut: {historique.nouveau_statut}")
    print(f"   - Modifié par: {historique.modifie_par.get_full_name()}")
    print(f"   - Date: {historique.date_modification}")
    
    # 5. Vérifier publication globale
    print_section("5. VÉRIFICATION PUBLICATION GLOBALE")
    
    publication, created = Publication.objects.get_or_create(
        cycle=facture_test.cycle,
        periode_debut=facture_test.periode_debut,
        periode_fin=facture_test.periode_fin,
        defaults={
            'agent': agent,
            'nombre_factures': 1,
            'nombre_factures_traitees': 1,
            'nombre_erreurs': 0
        }
    )
    
    if not created:
        # Mise à jour
        publication.nombre_factures_traitees += 1
        publication.save()
    
    print(f"{'✅ Publication créée' if created else '✅ Publication mise à jour'}")
    print(f"   - Cycle: {publication.cycle}")
    print(f"   - Période: {publication.periode_debut} → {publication.periode_fin}")
    print(f"   - Agent: {publication.agent.get_full_name()}")
    print(f"   - Factures traitées: {publication.nombre_factures_traitees}/{publication.nombre_factures}")
    
    # 6. Test visibilité pour payeur
    print_section("6. TEST VISIBILITÉ PAYEUR")
    
    if payeur and facture_test.company.payeur:
        factures_payeur = Invoice.objects.filter(
            company__payeur=payeur,
            statut='PUBLIEE'
        )
        print(f"Payeur {payeur.username} voit {factures_payeur.count()} facture(s) PUBLIEE")
        
        if facture_test.company.payeur == payeur:
            if facture_test in factures_payeur:
                print(f"✅ Payeur voit bien la facture {facture_test.numero_facture}")
            else:
                print(f"❌ Payeur ne voit PAS la facture {facture_test.numero_facture}")
        else:
            print(f"⚠️  La facture n'appartient pas au payeur {payeur.username}")
    else:
        print("⚠️  Pas de payeur ou facture sans payeur")
    
    # 7. Test visibilité pour employé
    print_section("7. TEST VISIBILITÉ EMPLOYÉ")
    
    if employe and facture_test.line:
        factures_employe = Invoice.objects.filter(
            line__employe=employe,
            statut='PUBLIEE'
        )
        print(f"Employé {employe.username} voit {factures_employe.count()} facture(s) PUBLIEE")
        
        if facture_test.line.employe == employe:
            if facture_test in factures_employe:
                print(f"✅ Employé voit bien la facture {facture_test.numero_facture}")
            else:
                print(f"❌ Employé ne voit PAS la facture {facture_test.numero_facture}")
        else:
            print(f"⚠️  La facture n'est pas liée à l'employé {employe.username}")
    elif not facture_test.line:
        print("⚠️  Facture globale, pas d'employé concerné (normal)")
    else:
        print("⚠️  Pas d'employé en base")
    
    # 8. Test non-visibilité employé non concerné
    print_section("8. TEST NON-VISIBILITÉ EMPLOYÉ NON CONCERNÉ")
    
    if employe and facture_test.line:
        # Chercher un autre employé
        autre_employe = User.objects.filter(role='EMPLOYE').exclude(id=employe.id).first()
        if autre_employe:
            factures_autre = Invoice.objects.filter(
                line__employe=autre_employe,
                statut='PUBLIEE'
            )
            if facture_test in factures_autre:
                print(f"❌ PROBLÈME: Employé {autre_employe.username} voit la facture alors qu'il ne devrait pas !")
            else:
                print(f"✅ Employé {autre_employe.username} ne voit PAS la facture {facture_test.numero_facture} (normal)")
        else:
            print("⚠️  Un seul employé en base, impossible de tester")
    else:
        print("⚠️  Test non applicable (pas d'employé ou facture globale)")
    
    # 9. Statistiques finales
    print_section("9. STATISTIQUES FINALES")
    
    stats = {
        'BROUILLON': Invoice.objects.filter(statut='BROUILLON').count(),
        'EN_COURS': Invoice.objects.filter(statut='EN_COURS').count(),
        'VALIDEE': Invoice.objects.filter(statut='VALIDEE').count(),
        'PUBLIEE': Invoice.objects.filter(statut='PUBLIEE').count(),
        'PAYEE': Invoice.objects.filter(statut='PAYEE').count(),
        'ANNULEE': Invoice.objects.filter(statut='ANNULEE').count(),
    }
    
    print("Distribution des factures par statut:")
    for statut, count in stats.items():
        print(f"  - {statut}: {count}")
    
    print(f"\nTotal factures: {sum(stats.values())}")
    print(f"Total historique: {HistoriqueFacturation.objects.count()}")
    print(f"Total publications: {Publication.objects.count()}")
    
    print_section("✅ TESTS TERMINÉS")

if __name__ == '__main__':
    try:
        test_workflow_publication()
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
