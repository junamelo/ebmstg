"""
Script de test pour valider l'affectation des factures aux employés
Date: 30 juillet 2026
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()

from accounts.models import User
from billing.models import Line, Invoice, Company
from django.db.models import Q

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_employe_totsovi():
    """Test de l'employé TOTSOVI Eyram"""
    print_header("TEST 1 : Vérification employé TOTSOVI Eyram")
    
    try:
        employe = User.objects.get(Q(username='99475555') | Q(email='e.totsovi@biospartners.com'))
        print(f"✅ Employé trouvé : {employe.first_name} {employe.last_name}")
        print(f"   - Email : {employe.email}")
        print(f"   - Username : {employe.username}")
        print(f"   - Téléphone : {employe.telephone}")
        print(f"   - Rôle : {employe.role}")
        print(f"   - Statut : {employe.status}")
        return employe
    except User.DoesNotExist:
        print("❌ Employé TOTSOVI non trouvé !")
        return None

def test_ligne_affectation(employe):
    """Test de l'affectation de la ligne"""
    print_header("TEST 2 : Vérification affectation ligne")
    
    try:
        ligne = Line.objects.get(msisdn='99475555')
        print(f"✅ Ligne trouvée : {ligne.msisdn}")
        print(f"   - Entreprise : {ligne.company.raison_sociale}")
        print(f"   - Compte : {ligne.company.compte}")
        print(f"   - Utilisateur : {ligne.utilisateur}")
        print(f"   - Cycle : {ligne.cycle}")
        print(f"   - Statut : {ligne.statut}")
        print(f"   - Forfait : {ligne.forfait} FCFA")
        
        if ligne.employe:
            if ligne.employe == employe:
                print(f"✅ Employé correctement affecté : {ligne.employe.first_name} {ligne.employe.last_name}")
            else:
                print(f"⚠️  Employé différent affecté : {ligne.employe.first_name} {ligne.employe.last_name}")
        else:
            print("❌ Aucun employé affecté à cette ligne !")
        
        return ligne
    except Line.DoesNotExist:
        print("❌ Ligne 99475555 non trouvée !")
        return None

def test_factures_employe(employe, ligne):
    """Test des factures visibles par l'employé"""
    print_header("TEST 3 : Factures visibles par l'employé")
    
    # Factures liées à la ligne de l'employé
    factures = Invoice.objects.filter(line=ligne)
    
    print(f"Nombre de factures trouvées : {factures.count()}")
    
    if factures.count() == 0:
        print("❌ Aucune facture trouvée pour cette ligne !")
        return []
    
    for i, facture in enumerate(factures, 1):
        print(f"\n📄 Facture #{i}")
        print(f"   - Numéro : {facture.numero_facture}")
        print(f"   - Ligne : {facture.line.msisdn if facture.line else 'N/A'}")
        print(f"   - Type : {'SOMMAIRE (individuelle)' if facture.line else 'GLOBALE'}")
        print(f"   - Montant TTC : {facture.montant_ttc:,.0f} FCFA")
        print(f"   - Période : {facture.periode_debut} → {facture.periode_fin}")
        print(f"   - Statut : {facture.statut}")
        print(f"   - PDF : {facture.fichier_pdf or 'Non attaché'}")
        
        if facture.line and facture.line.employe == employe:
            print("   ✅ Visible par cet employé")
        else:
            print("   ⚠️  Pas visible par cet employé")
    
    return list(factures)

def test_factures_payeur(ligne):
    """Test des factures visibles par le payeur"""
    print_header("TEST 4 : Factures visibles par le payeur")
    
    company = ligne.company
    payeur = company.payeur
    
    if not payeur:
        print("❌ Aucun payeur affecté à l'entreprise !")
        return []
    
    print(f"Payeur : {payeur.first_name} {payeur.last_name}")
    print(f"Email : {payeur.email}")
    
    # Toutes les factures de l'entreprise (globales + individuelles)
    factures = Invoice.objects.filter(company=company)
    
    print(f"\nNombre total de factures de l'entreprise : {factures.count()}")
    
    globales = factures.filter(line__isnull=True)
    individuelles = factures.filter(line__isnull=False)
    
    print(f"   - Factures GLOBALES : {globales.count()}")
    print(f"   - Factures SOMMAIRES : {individuelles.count()}")
    
    print("\n📋 Détail des factures SOMMAIRES :")
    for facture in individuelles[:5]:  # Limiter à 5 pour lisibilité
        print(f"   • {facture.numero_facture} - Ligne {facture.line.msisdn} - {facture.montant_ttc:,.0f} FCFA")
    
    return list(factures)

def test_api_simulation():
    """Simuler les requêtes API"""
    print_header("TEST 5 : Simulation requêtes API")
    
    employe = User.objects.get(username='99475555')
    
    # Simulation GET /api/billing/invoices/ en tant qu'employé
    print("\n🔍 GET /api/billing/invoices/ (rôle EMPLOYE)")
    factures_employe = Invoice.objects.filter(line__employe=employe)
    print(f"   Résultat : {factures_employe.count()} facture(s)")
    for f in factures_employe:
        print(f"   • {f.numero_facture}")
    
    # Simulation GET /api/billing/invoices/ en tant que payeur
    print("\n🔍 GET /api/billing/invoices/ (rôle PAYEUR)")
    company = Line.objects.get(msisdn='99475555').company
    if company.payeur:
        factures_payeur = Invoice.objects.filter(company__payeur=company.payeur)
        print(f"   Résultat : {factures_payeur.count()} facture(s)")
        print(f"   Entreprises : {', '.join(set([f.company.raison_sociale for f in factures_payeur[:5]]))}")

def test_statistiques():
    """Statistiques globales"""
    print_header("TEST 6 : Statistiques globales")
    
    total_employes = User.objects.filter(role='EMPLOYE').count()
    total_lignes = Line.objects.count()
    lignes_affectees = Line.objects.exclude(employe__isnull=True).count()
    total_factures = Invoice.objects.count()
    factures_individuelles = Invoice.objects.exclude(line__isnull=True).count()
    factures_globales = Invoice.objects.filter(line__isnull=True).count()
    
    print(f"👥 Employés enregistrés : {total_employes}")
    print(f"📱 Lignes totales : {total_lignes}")
    print(f"✅ Lignes affectées à un employé : {lignes_affectees} ({lignes_affectees/total_lignes*100:.1f}%)")
    print(f"\n📄 Factures totales : {total_factures}")
    print(f"   - GLOBALES : {factures_globales}")
    print(f"   - SOMMAIRES : {factures_individuelles}")
    
    # Lignes sans employé
    print("\n⚠️  Lignes sans employé affecté :")
    lignes_sans_employe = Line.objects.filter(employe__isnull=True)[:10]
    for ligne in lignes_sans_employe:
        print(f"   • {ligne.msisdn} - {ligne.company.raison_sociale}")

def main():
    """Exécution principale des tests"""
    print("\n" + "🧪"*35)
    print("  TESTS D'AFFECTATION DES FACTURES AUX EMPLOYÉS")
    print("  Portail e-Billings - Moov Africa Togo")
    print("🧪"*35)
    
    try:
        # Test 1 : Vérifier l'employé
        employe = test_employe_totsovi()
        if not employe:
            print("\n❌ Test arrêté : employé non trouvé")
            return
        
        # Test 2 : Vérifier la ligne
        ligne = test_ligne_affectation(employe)
        if not ligne:
            print("\n❌ Test arrêté : ligne non trouvée")
            return
        
        # Test 3 : Factures employé
        factures_emp = test_factures_employe(employe, ligne)
        
        # Test 4 : Factures payeur
        factures_pay = test_factures_payeur(ligne)
        
        # Test 5 : Simulation API
        test_api_simulation()
        
        # Test 6 : Statistiques
        test_statistiques()
        
        # Résumé
        print_header("✅ RÉSUMÉ DES TESTS")
        print(f"✅ Employé TOTSOVI : OK")
        print(f"✅ Ligne 99475555 : OK")
        print(f"✅ Affectation ligne → employé : {'OK' if ligne.employe == employe else 'KO'}")
        print(f"✅ Factures employé : {len(factures_emp)}")
        print(f"✅ Factures payeur : {len(factures_pay)}")
        print("\n🎉 Tous les tests sont terminés !")
        
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
