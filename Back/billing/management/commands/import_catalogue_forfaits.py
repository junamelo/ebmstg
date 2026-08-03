"""
Commande Django pour importer le catalogue de forfaits, services et options depuis Excel
"""
from django.core.management.base import BaseCommand
import pandas as pd
from billing.models import Package, Service, TarifService
from decimal import Decimal
import os


class Command(BaseCommand):
    help = 'Importe le catalogue de forfaits, services et options depuis le fichier Excel'
    
    def __init__(self):
        super().__init__()
        self.stats = {
            'packages_crees': 0,
            'packages_maj': 0,
            'services_crees': 0,
            'services_maj': 0,
            'options_creees': 0,
            'options_maj': 0,
            'erreurs': []
        }
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--excel-path',
            type=str,
            default=r"C:\Users\Benoit\Documents\BURRO\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026\Contexte\Données_Test_Facturation (1).xlsx",
            help='Chemin vers le fichier Excel'
        )
    
    def handle(self, *args, **options):
        excel_path = options['excel_path']
        
        if not os.path.exists(excel_path):
            self.stderr.write(self.style.ERROR(f'Fichier Excel introuvable : {excel_path}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Lecture du fichier : {excel_path}'))
        
        try:
            # Importer les services et options
            self.import_blackberry(excel_path)
            self.import_no_limit(excel_path)
            self.import_services_autres(excel_path)
            
            # Importer les forfaits/formules
            self.import_formules(excel_path)
            
            # Afficher le résumé
            self.afficher_resume()
            
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Erreur lors de l\'import : {e}'))
            import traceback
            traceback.print_exc()
    
    def import_blackberry(self, excel_path):
        """Importer les options BlackBerry"""
        self.stdout.write('\n=== Import BlackBerry ===')
        
        df = pd.read_excel(excel_path, sheet_name='BlackBerry')
        
        # Créer ou récupérer le service BlackBerry
        service, created = Service.objects.get_or_create(
            code='BLACKBERRY',
            defaults={
                'nom': 'BlackBerry',
                'type_service': 'OPTION',
                'description': 'Options BlackBerry pour accès emails et messagerie professionnelle',
                'est_actif': True
            }
        )
        
        if created:
            self.stats['services_crees'] += 1
            self.stdout.write(self.style.SUCCESS(f'  Service créé : {service.nom}'))
        else:
            self.stats['services_maj'] += 1
            self.stdout.write(f'  Service existant : {service.nom}')
        
        # Importer les options
        for _, row in df.iterrows():
            code = str(row['Code ']).strip() if pd.notna(row['Code ']) else None
            prix = row['Tarif (XOF)']
            
            if not code or pd.isna(prix):
                continue
            
            # Ignorer BB0 (tarif 0)
            if code == 'BB0' or float(prix) == 0:
                continue
            
            # Créer ou mettre à jour l'option
            option, created = TarifService.objects.update_or_create(
                service=service,
                nom_option=code,
                defaults={
                    'prix': Decimal(str(prix)),
                    'description': f'Option BlackBerry {code}',
                    'est_actif': True
                }
            )
            
            if created:
                self.stats['options_creees'] += 1
                self.stdout.write(self.style.SUCCESS(f'    Option créée : {code} - {prix} FCFA'))
            else:
                self.stats['options_maj'] += 1
                self.stdout.write(f'    Option MAJ : {code} - {prix} FCFA')
    
    def import_no_limit(self, excel_path):
        """Importer les options No Limit"""
        self.stdout.write('\n=== Import No Limit ===')
        
        df = pd.read_excel(excel_path, sheet_name='No Limit', header=None)
        
        # Créer ou récupérer le service No Limit
        service, created = Service.objects.get_or_create(
            code='NO_LIMIT',
            defaults={
                'nom': 'No Limit',
                'type_service': 'OPTION',
                'description': 'Options No Limit pour appels et navigation illimités',
                'est_actif': True
            }
        )
        
        if created:
            self.stats['services_crees'] += 1
            self.stdout.write(self.style.SUCCESS(f'  Service créé : {service.nom}'))
        else:
            self.stats['services_maj'] += 1
            self.stdout.write(f'  Service existant : {service.nom}')
        
        # La ligne 1 contient les en-têtes (index 1)
        # Les données commencent à la ligne 2 (index 2)
        for idx in range(2, len(df)):
            code = df.iloc[idx, 0]
            prix = df.iloc[idx, 1]
            
            if pd.isna(code) or pd.isna(prix):
                continue
            
            code = str(code).strip()
            
            # Vérifier si prix est convertible en float
            try:
                prix_float = float(prix)
            except (ValueError, TypeError):
                continue
            
            # Ignorer les codes avec tarif 0
            if code in ['AI00'] or prix_float == 0:
                continue
            
            # Créer ou mettre à jour l'option
            option, created = TarifService.objects.update_or_create(
                service=service,
                nom_option=code,
                defaults={
                    'prix': Decimal(str(prix_float)),
                    'description': f'Option No Limit {code}',
                    'est_actif': True
                }
            )
            
            if created:
                self.stats['options_creees'] += 1
                self.stdout.write(self.style.SUCCESS(f'    Option créée : {code} - {prix_float} FCFA'))
            else:
                self.stats['options_maj'] += 1
                self.stdout.write(f'    Option MAJ : {code} - {prix_float} FCFA')
    
    def import_services_autres(self, excel_path):
        """Importer les autres services (Facture Détaillée, Incognito)"""
        self.stdout.write('\n=== Import Services Autres ===')
        
        df = pd.read_excel(excel_path, sheet_name='Services Autres', header=None)
        
        # La ligne 2 contient les en-têtes (index 2)
        # Les données commencent à la ligne 3 (index 3)
        for idx in range(3, len(df)):
            code = df.iloc[idx, 0]
            prix = df.iloc[idx, 1]
            
            if pd.isna(code) or pd.isna(prix):
                continue
            
            code = str(code).strip()
            
            # Mapper code → service
            if 'FACTURE DETAILLEE' in code.upper():
                service_code = 'FACTURE_DETAILLEE'
                service_nom = 'Facture Détaillée'
                service_desc = 'Service de facturation détaillée avec historique des appels'
            elif 'INCOGNITO' in code.upper():
                service_code = 'INCOGNITO'
                service_nom = 'Incognito'
                service_desc = 'Service d\'anonymisation du numéro'
            else:
                continue
            
            # Créer ou récupérer le service
            service, created = Service.objects.get_or_create(
                code=service_code,
                defaults={
                    'nom': service_nom,
                    'type_service': 'OPTION',
                    'description': service_desc,
                    'est_actif': True
                }
            )
            
            if created:
                self.stats['services_crees'] += 1
                self.stdout.write(self.style.SUCCESS(f'  Service créé : {service.nom}'))
            
            # Créer ou mettre à jour l'option
            option, created = TarifService.objects.update_or_create(
                service=service,
                nom_option=f'{service_nom} Standard',
                defaults={
                    'prix': Decimal(str(prix)),
                    'description': f'{service_nom} - Tarif standard',
                    'est_actif': True
                }
            )
            
            if created:
                self.stats['options_creees'] += 1
                self.stdout.write(self.style.SUCCESS(f'    Option créée : {service_nom} Standard - {prix} FCFA'))
            else:
                self.stats['options_maj'] += 1
                self.stdout.write(f'    Option MAJ : {service_nom} Standard - {prix} FCFA')
    
    def import_formules(self, excel_path):
        """Importer les forfaits/formules depuis la feuille Formule UNIQUEMENT
        
        IMPORTANT : Cette méthode n'importe que les données vérifiables de l'Excel.
        Prix et quotas doivent être fournis via un référentiel métier externe.
        """
        self.stdout.write('\n=== Import Forfaits/Formules ===')
        
        df = pd.read_excel(excel_path, sheet_name='Formule', header=None)
        
        # La ligne 4 contient les en-têtes (index 4)
        # Les données commencent à la ligne 5 (index 5)
        for idx in range(5, len(df)):
            code = df.iloc[idx, 0]
            nom = df.iloc[idx, 1]
            
            if pd.isna(code) or pd.isna(nom):
                continue
            
            code = str(code).strip()
            nom = str(nom).strip()
            
            # Ignorer l'en-tête si présent
            if code == 'CODES' or nom == 'FORMULES':
                continue
            
            # Créer ou mettre à jour le forfait avec UNIQUEMENT les données de l'Excel
            # Prix et quotas à 0/NULL par défaut - à remplir via référentiel métier
            package, created = Package.objects.update_or_create(
                code=code,
                defaults={
                    'nom': nom,
                    'type_forfait': 'MIXTE',  # Type par défaut
                    'prix_mensuel': Decimal('0'),  # À définir via référentiel
                    'quota_data_mo': None,  # À définir via référentiel
                    'quota_minutes': None,  # À définir via référentiel
                    'quota_sms': None,  # À définir via référentiel
                    'description': f'Forfait {nom}',
                    'est_actif': True
                }
            )
            
            if created:
                self.stats['packages_crees'] += 1
                self.stdout.write(self.style.SUCCESS(f'  Forfait créé : {code} - {nom} (prix/quotas à définir)'))
            else:
                self.stats['packages_maj'] += 1
                self.stdout.write(f'  Forfait MAJ : {code} - {nom} (prix/quotas à définir)')
    
    def afficher_resume(self):
        """Afficher le résumé de l'import"""
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('RÉSUMÉ DE L\'IMPORT'))
        self.stdout.write('='*80)
        
        self.stdout.write(f'\nForfaits Package :')
        self.stdout.write(f'  Créés : {self.stats["packages_crees"]}')
        self.stdout.write(f'  Mis à jour : {self.stats["packages_maj"]}')
        self.stdout.write(f'  Total en base : {Package.objects.count()}')
        
        self.stdout.write(f'\nServices :')
        self.stdout.write(f'  Créés : {self.stats["services_crees"]}')
        self.stdout.write(f'  Mis à jour : {self.stats["services_maj"]}')
        self.stdout.write(f'  Total en base : {Service.objects.count()}')
        
        self.stdout.write(f'\nOptions (TarifService) :')
        self.stdout.write(f'  Créées : {self.stats["options_creees"]}')
        self.stdout.write(f'  Mises à jour : {self.stats["options_maj"]}')
        self.stdout.write(f'  Total en base : {TarifService.objects.count()}')
        
        if self.stats['erreurs']:
            self.stdout.write(f'\nErreurs : {len(self.stats["erreurs"])}')
            for err in self.stats['erreurs']:
                self.stderr.write(self.style.ERROR(f'  - {err}'))
        
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('Import terminé avec succès !'))
        self.stdout.write('='*80 + '\n')
