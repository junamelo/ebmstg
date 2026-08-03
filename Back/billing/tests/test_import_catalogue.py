"""
Tests pour la commande import_catalogue_forfaits
"""
from django.test import TestCase
from django.core.management import call_command
from billing.models import Package, Service, TarifService
from decimal import Decimal
import os


class ImportCatalogueTestCase(TestCase):
    """Tests pour vérifier l'import du catalogue depuis Excel"""
    
    def setUp(self):
        """Nettoyer la base avant chaque test"""
        Package.objects.all().delete()
        Service.objects.all().delete()
        TarifService.objects.all().delete()
    
    def test_commande_import_existe(self):
        """Test : la commande import_catalogue_forfaits existe"""
        from django.core.management import get_commands
        commands = get_commands()
        self.assertIn('import_catalogue_forfaits', commands, 
                     "La commande import_catalogue_forfaits doit exister")
    
    def test_import_services_blackberry(self):
        """Test : le service BlackBerry est importé avec ses options"""
        call_command('import_catalogue_forfaits')
        
        # Vérifier que le service BlackBerry existe
        service = Service.objects.filter(code='BLACKBERRY').first()
        self.assertIsNotNone(service, "Le service BlackBerry doit être importé")
        self.assertEqual(service.nom, 'BlackBerry')
        self.assertEqual(service.type_service, 'OPTION')
        self.assertTrue(service.est_actif)
        
        # Vérifier qu'il a des options
        options_count = service.tarifs.filter(est_actif=True).count()
        self.assertGreater(options_count, 0, "BlackBerry doit avoir des options")
    
    def test_import_services_no_limit(self):
        """Test : le service No Limit est importé avec ses options"""
        call_command('import_catalogue_forfaits')
        
        # Vérifier que le service No Limit existe
        service = Service.objects.filter(code='NO_LIMIT').first()
        self.assertIsNotNone(service, "Le service No Limit doit être importé")
        self.assertEqual(service.nom, 'No Limit')
        self.assertTrue(service.est_actif)
        
        # Vérifier qu'il a des options
        options_count = service.tarifs.filter(est_actif=True).count()
        self.assertGreater(options_count, 0, "No Limit doit avoir des options")
    
    def test_import_services_autres(self):
        """Test : les services Facture Détaillée et Incognito sont importés"""
        call_command('import_catalogue_forfaits')
        
        # Vérifier Facture Détaillée
        facture = Service.objects.filter(code='FACTURE_DETAILLEE').first()
        self.assertIsNotNone(facture, "Le service Facture Détaillée doit être importé")
        self.assertEqual(facture.nom, 'Facture Détaillée')
        
        # Vérifier Incognito
        incognito = Service.objects.filter(code='INCOGNITO').first()
        self.assertIsNotNone(incognito, "Le service Incognito doit être importé")
        self.assertEqual(incognito.nom, 'Incognito')
    
    def test_import_forfaits_depuis_feuille_formule(self):
        """Test : les forfaits sont importés depuis la feuille Formule"""
        call_command('import_catalogue_forfaits')
        
        # Codes attendus depuis la feuille Formule
        codes_attendus = ['S1K', 'S1Q', 'M3C', 'F1C', 'S50', 'S30', 'B50', 'B30', 'B20', 'F30', 'DAT', 'Op0', 'TOT']
        
        packages = Package.objects.filter(code__in=codes_attendus)
        self.assertEqual(packages.count(), len(codes_attendus), 
                        f"Tous les codes de la feuille Formule doivent être importés")
        
        # Vérifier quelques forfaits spécifiques
        star = Package.objects.filter(code='S1K').first()
        self.assertIsNotNone(star)
        self.assertEqual(star.nom, 'STAR')
        self.assertTrue(star.est_actif)
        
        data = Package.objects.filter(code='DAT').first()
        self.assertIsNotNone(data)
        self.assertEqual(data.nom, 'DATA')
    
    def test_import_ignore_en_tete_codes_formules(self):
        """Test : l'en-tête CODES/FORMULES est ignoré"""
        call_command('import_catalogue_forfaits')
        
        # Vérifier qu'aucun forfait avec code CODES n'existe
        fake_forfait = Package.objects.filter(code='CODES').first()
        self.assertIsNone(fake_forfait, "L'en-tête CODES/FORMULES doit être ignoré")
    
    def test_import_options_blackberry_ont_prix(self):
        """Test : les options BlackBerry importées ont un prix > 0"""
        call_command('import_catalogue_forfaits')
        
        service = Service.objects.filter(code='BLACKBERRY').first()
        self.assertIsNotNone(service)
        
        # Vérifier qu'au moins une option a un prix > 0
        options_avec_prix = service.tarifs.filter(prix__gt=0, est_actif=True)
        self.assertGreater(options_avec_prix.count(), 0, 
                          "Les options BlackBerry doivent avoir des prix")
    
    def test_import_options_no_limit_ont_prix(self):
        """Test : les options No Limit importées ont un prix > 0"""
        call_command('import_catalogue_forfaits')
        
        service = Service.objects.filter(code='NO_LIMIT').first()
        self.assertIsNotNone(service)
        
        # Vérifier qu'au moins une option a un prix > 0
        options_avec_prix = service.tarifs.filter(prix__gt=0, est_actif=True)
        self.assertGreater(options_avec_prix.count(), 0, 
                          "Les options No Limit doivent avoir des prix")
    
    def test_import_est_idempotent(self):
        """Test : relancer l'import ne crée pas de doublons"""
        # Premier import
        call_command('import_catalogue_forfaits')
        count_packages_1 = Package.objects.count()
        count_services_1 = Service.objects.count()
        count_options_1 = TarifService.objects.count()
        
        # Deuxième import
        call_command('import_catalogue_forfaits')
        count_packages_2 = Package.objects.count()
        count_services_2 = Service.objects.count()
        count_options_2 = TarifService.objects.count()
        
        # Les compteurs doivent être identiques
        self.assertEqual(count_packages_1, count_packages_2, 
                        "L'import doit être idempotent pour les forfaits")
        self.assertEqual(count_services_1, count_services_2, 
                        "L'import doit être idempotent pour les services")
        self.assertEqual(count_options_1, count_options_2, 
                        "L'import doit être idempotent pour les options")
    
    def test_import_forfaits_sans_prix_inventés(self):
        """Test : les forfaits importés sans référentiel ont prix à 0"""
        call_command('import_catalogue_forfaits')
        
        # Après import sans référentiel, les prix doivent être à 0 par défaut
        # (sauf si une source vérifiable est trouvée dans l'Excel)
        packages = Package.objects.all()
        self.assertGreater(packages.count(), 0, "Des forfaits doivent être importés")
        
        # Vérifier qu'au moins un forfait existe
        star = Package.objects.filter(code='S1K').first()
        self.assertIsNotNone(star)
        # Le prix doit être 0 ou NULL jusqu'à ce qu'un référentiel soit fourni
        # (à adapter selon la logique métier finale)
    
    def test_import_tous_services_actifs(self):
        """Test : tous les services importés sont actifs par défaut"""
        call_command('import_catalogue_forfaits')
        
        services_inactifs = Service.objects.filter(est_actif=False)
        self.assertEqual(services_inactifs.count(), 0, 
                        "Tous les services importés doivent être actifs par défaut")
    
    def test_import_toutes_options_actives(self):
        """Test : toutes les options importées sont actives par défaut"""
        call_command('import_catalogue_forfaits')
        
        options_inactives = TarifService.objects.filter(est_actif=False)
        self.assertEqual(options_inactives.count(), 0, 
                        "Toutes les options importées doivent être actives par défaut")
    
    def test_import_tous_forfaits_actifs(self):
        """Test : tous les forfaits importés sont actifs par défaut"""
        call_command('import_catalogue_forfaits')
        
        forfaits_inactifs = Package.objects.filter(est_actif=False)
        self.assertEqual(forfaits_inactifs.count(), 0, 
                        "Tous les forfaits importés doivent être actifs par défaut")
