#!/usr/bin/env python
"""
Script pour lancer tous les tests du backend Moov e-Billings
Usage: python run_all_tests.py
"""
import os
import sys
import django
from django.conf import settings
from django.core.management import call_command

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()


def print_banner():
    """Afficher bannière de démarrage"""
    print("=" * 80)
    print("🧪 TESTS BACKEND MOOV E-BILLINGS")
    print("=" * 80)
    print()


def print_section(title):
    """Afficher titre de section"""
    print()
    print("-" * 80)
    print(f"📋 {title}")
    print("-" * 80)


def run_tests_by_phase():
    """Lancer les tests phase par phase"""
    
    phases = [
        {
            'name': 'Phase 1 : Authentification & Utilisateurs',
            'tests': [
                'accounts.tests.AuthenticationTests',
                'accounts.tests.UserManagementTests',
            ],
            'count': 20
        },
        {
            'name': 'Phase 2 : Contrats & Lignes',
            'tests': [
                'billing.tests.CompanyTests',
                'billing.tests.LineTests',
            ],
            'count': 13
        },
        {
            'name': 'Phase 3 : Tarification & Services',
            'tests': [
                'billing.tests.PackageTests',
                'billing.tests.ServiceTests',
                'billing.tests.TarifServiceTests',
            ],
            'count': 10
        },
        {
            'name': 'Phase 4 : Facturation Complète',
            'tests': [
                'billing.tests.CalculTarificationTests',
                'billing.tests.InvoiceTests',
                'billing.tests.PublicationTests',
            ],
            'count': 20
        },
    ]
    
    total_passed = 0
    total_failed = 0
    
    for phase in phases:
        print_section(phase['name'])
        print(f"Nombre de tests attendus : {phase['count']}")
        print()
        
        for test_class in phase['tests']:
            try:
                call_command('test', test_class, verbosity=1)
            except Exception as e:
                print(f"❌ Erreur lors de l'exécution de {test_class}: {e}")
    
    print()


def run_all_tests_at_once():
    """Lancer tous les tests d'un coup"""
    print_section("Lancement de TOUS les tests")
    print("Total attendu : 63 tests")
    print()
    
    try:
        call_command('test', 'accounts', 'billing', verbosity=2)
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution des tests: {e}")


def main():
    """Fonction principale"""
    print_banner()
    
    print("Choisissez une option :")
    print("1. Lancer tous les tests d'un coup (recommandé)")
    print("2. Lancer les tests phase par phase")
    print("3. Quitter")
    print()
    
    choice = input("Votre choix (1-3) : ").strip()
    
    if choice == '1':
        run_all_tests_at_once()
    elif choice == '2':
        run_tests_by_phase()
    elif choice == '3':
        print("Au revoir !")
        sys.exit(0)
    else:
        print("❌ Choix invalide")
        sys.exit(1)
    
    print()
    print("=" * 80)
    print("✅ Tests terminés")
    print("=" * 80)


if __name__ == '__main__':
    main()
