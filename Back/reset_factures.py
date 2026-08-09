"""
Script pour vider la base de données des factures
Permet de refaire des tests de publication sans avoir de doublons

ATTENTION : Ce script supprime TOUTES les factures !
Utilisez-le uniquement en environnement de test.
"""
import os
import sys
import django
import shutil
from pathlib import Path

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()

from billing.models import Invoice, NotificationFacture, HistoriqueFacturation, Publication
from django.conf import settings

def reset_factures():
    """Supprime toutes les factures et leurs données associées"""
    
    print("\n" + "="*70)
    print("🧹 NETTOYAGE DE LA BASE DE DONNÉES - FACTURES")
    print("="*70)
    
    # 1. Compter les éléments avant suppression
    nb_invoices = Invoice.objects.count()
    nb_notifications = NotificationFacture.objects.count()
    nb_historique = HistoriqueFacturation.objects.count()
    nb_publications = Publication.objects.count()
    
    print(f"\n📊 Éléments à supprimer :")
    print(f"   - Factures : {nb_invoices}")
    print(f"   - Notifications : {nb_notifications}")
    print(f"   - Historique facturation : {nb_historique}")
    print(f"   - Publications : {nb_publications}")
    
    if nb_invoices == 0:
        print("\n✅ La base est déjà vide !")
        return
    
    # Demander confirmation
    print("\n⚠️  ATTENTION : Cette action est IRRÉVERSIBLE !")
    print("   Toutes les factures et leurs données associées seront supprimées.")
    
    confirmation = input("\nTaper 'OUI' en majuscules pour confirmer : ").strip()
    
    if confirmation != 'OUI':
        print("\n❌ Opération annulée.")
        return
    
    print("\n🗑️  Suppression en cours...")
    
    # 2. Supprimer les fichiers PDF
    print("\n1️⃣  Suppression des fichiers PDF...")
    media_root = Path(settings.MEDIA_ROOT)
    
    # Dossier des factures
    factures_dir = media_root / 'factures'
    if factures_dir.exists():
        nb_fichiers = len(list(factures_dir.glob('**/*')))
        try:
            shutil.rmtree(factures_dir)
            print(f"   ✅ {nb_fichiers} fichier(s) PDF supprimé(s)")
        except Exception as e:
            print(f"   ⚠️  Erreur lors de la suppression des fichiers : {e}")
    else:
        print("   ℹ️  Aucun dossier de factures à supprimer")
    
    # Dossier des publications
    publications_dir = media_root / 'publications'
    if publications_dir.exists():
        nb_fichiers_pub = len(list(publications_dir.glob('**/*')))
        try:
            shutil.rmtree(publications_dir)
            print(f"   ✅ {nb_fichiers_pub} fichier(s) de publication supprimé(s)")
        except Exception as e:
            print(f"   ⚠️  Erreur lors de la suppression des publications : {e}")
    else:
        print("   ℹ️  Aucun dossier de publications à supprimer")
    
    # 3. Supprimer les notifications de factures
    print("\n2️⃣  Suppression des notifications...")
    NotificationFacture.objects.all().delete()
    print(f"   ✅ {nb_notifications} notification(s) supprimée(s)")
    
    # 4. Supprimer l'historique de facturation
    print("\n3️⃣  Suppression de l'historique de facturation...")
    HistoriqueFacturation.objects.all().delete()
    print(f"   ✅ {nb_historique} entrée(s) d'historique supprimée(s)")
    
    # 5. Supprimer les publications
    print("\n4️⃣  Suppression des publications...")
    Publication.objects.all().delete()
    print(f"   ✅ {nb_publications} publication(s) supprimée(s)")
    
    # 6. Supprimer les factures (en dernier car elles ont des FK)
    print("\n5️⃣  Suppression des factures...")
    Invoice.objects.all().delete()
    print(f"   ✅ {nb_invoices} facture(s) supprimée(s)")
    
    # Recréer les dossiers vides
    factures_dir.mkdir(parents=True, exist_ok=True)
    publications_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*70)
    print("✅ NETTOYAGE TERMINÉ")
    print("="*70)
    print("\n📋 Résumé :")
    print(f"   ✅ {nb_invoices} facture(s) supprimée(s)")
    print(f"   ✅ {nb_notifications} notification(s) supprimée(s)")
    print(f"   ✅ {nb_historique} historique(s) supprimé(s)")
    print(f"   ✅ {nb_publications} publication(s) supprimée(s)")
    print(f"   ✅ Fichiers PDF supprimés")
    print("\n✨ Vous pouvez maintenant refaire vos tests de publication !")
    print("   Les contrats, lignes et utilisateurs sont préservés.")
    

def afficher_statistiques():
    """Affiche les statistiques de la base"""
    from billing.models import Company, Line
    from accounts.models import User
    
    print("\n" + "="*70)
    print("📊 STATISTIQUES DE LA BASE DE DONNÉES")
    print("="*70)
    
    print("\n🔢 Données préservées :")
    print(f"   - Utilisateurs : {User.objects.count()}")
    print(f"   - Contrats : {Company.objects.count()}")
    print(f"   - Lignes : {Line.objects.count()}")
    
    print("\n📄 Données factures :")
    print(f"   - Factures : {Invoice.objects.count()}")
    print(f"   - Notifications : {NotificationFacture.objects.count()}")
    print(f"   - Historique : {HistoriqueFacturation.objects.count()}")
    print(f"   - Publications : {Publication.objects.count()}")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🧪 SCRIPT DE RÉINITIALISATION DES FACTURES")
    print("="*70)
    
    # Afficher les stats avant
    afficher_statistiques()
    
    # Demander l'action
    print("\n" + "="*70)
    print("ACTIONS DISPONIBLES")
    print("="*70)
    print("\n1. Supprimer toutes les factures (pour refaire des tests)")
    print("2. Afficher les statistiques uniquement")
    print("0. Quitter")
    
    choix = input("\nVotre choix : ").strip()
    
    if choix == '1':
        reset_factures()
        # Afficher les stats après
        afficher_statistiques()
    elif choix == '2':
        print("\n✅ Statistiques affichées ci-dessus")
    else:
        print("\n👋 Au revoir !")
