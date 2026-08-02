"""
Services de calcul de tarification
Logique métier pour calculer les montants de facturation selon les paliers Moov
"""
from decimal import Decimal
from typing import Dict, List, Tuple
import math


class CalculateurTarification:
    """
    Calculateur de tarification selon les règles métier Moov
    
    Tarifs de base :
    - DATA : Paliers jusqu'à 275 Go, puis 5 FCFA/Mo + 50000 FCFA fixe
    - VOIX : 79 FCFA/min (0-30s demi-tarif, >30s tarif complet)
    - SMS : 30 FCFA/unité
    - TVA : 18%
    """
    
    # Constantes tarifaires
    TARIF_VOIX_PAR_MINUTE = Decimal('79')  # FCFA
    TARIF_SMS_UNITAIRE = Decimal('30')  # FCFA
    TAUX_TVA = Decimal('0.18')  # 18%
    
    # Paliers DATA (en Mo et FCFA)
    PALIERS_DATA = [
        (512, Decimal('1000')),      # 0.5 Go
        (1024, Decimal('2000')),     # 1 Go
        (2048, Decimal('3000')),     # 2 Go
        (3072, Decimal('4000')),     # 3 Go
        (5120, Decimal('5000')),     # 5 Go
        (10240, Decimal('8000')),    # 10 Go
        (20480, Decimal('12000')),   # 20 Go
        (51200, Decimal('20000')),   # 50 Go
        (102400, Decimal('35000')),  # 100 Go
        (153600, Decimal('45000')),  # 150 Go
        (204800, Decimal('55000')),  # 200 Go
        (256000, Decimal('65000')),  # 250 Go
        (281600, Decimal('75000')),  # 275 Go
    ]
    
    # Au-delà de 275 Go : 5 FCFA/Mo + 50000 FCFA fixe
    TARIF_DATA_HORS_PALIER = Decimal('5')  # FCFA/Mo
    FORFAIT_FIXE_HORS_PALIER = Decimal('50000')  # FCFA
    SEUIL_HORS_PALIER_MO = 281600  # 275 Go en Mo
    
    @classmethod
    def calculer_data(cls, volume_mo: int, forfait_mo: int = 0) -> Dict:
        """
        Calculer le coût DATA selon les paliers
        
        Args:
            volume_mo: Volume consommé en Mo
            forfait_mo: Volume forfait inclus en Mo
            
        Returns:
            Dict avec détails calcul (hors_forfait_mo, palier, montant_ht, etc.)
        """
        # Volume hors forfait
        hors_forfait_mo = max(0, volume_mo - forfait_mo)
        
        if hors_forfait_mo == 0:
            return {
                'volume_total_mo': volume_mo,
                'volume_forfait_mo': forfait_mo,
                'volume_hors_forfait_mo': 0,
                'palier_applique': None,
                'montant_ht': Decimal('0'),
                'details': 'Consommation dans le forfait'
            }
        
        # Chercher le palier correspondant
        palier_applique = None
        montant_ht = Decimal('0')
        
        # Vérifier si hors paliers (> 275 Go)
        if hors_forfait_mo > cls.SEUIL_HORS_PALIER_MO:
            montant_ht = cls.FORFAIT_FIXE_HORS_PALIER + (hors_forfait_mo * cls.TARIF_DATA_HORS_PALIER)
            palier_applique = f"Hors palier (> 275 Go)"
            details = f"{hors_forfait_mo} Mo × {cls.TARIF_DATA_HORS_PALIER} FCFA/Mo + {cls.FORFAIT_FIXE_HORS_PALIER} FCFA fixe"
        else:
            # Trouver le palier approprié
            for seuil_mo, prix in cls.PALIERS_DATA:
                if hors_forfait_mo <= seuil_mo:
                    montant_ht = prix
                    palier_applique = f"{seuil_mo / 1024:.1f} Go"
                    details = f"Palier {palier_applique} : {prix} FCFA"
                    break
            
            # Si aucun palier trouvé (ne devrait pas arriver)
            if palier_applique is None:
                montant_ht = cls.PALIERS_DATA[-1][1]
                palier_applique = f"{cls.PALIERS_DATA[-1][0] / 1024:.1f} Go (max)"
                details = f"Palier maximum appliqué"
        
        return {
            'volume_total_mo': volume_mo,
            'volume_forfait_mo': forfait_mo,
            'volume_hors_forfait_mo': hors_forfait_mo,
            'palier_applique': palier_applique,
            'montant_ht': montant_ht,
            'details': details
        }
    
    @classmethod
    def calculer_voix(cls, duree_secondes: int, forfait_minutes: int = 0) -> Dict:
        """
        Calculer le coût VOIX selon la règle 0-30s demi-tarif, >30s tarif complet
        
        Args:
            duree_secondes: Durée totale en secondes
            forfait_minutes: Minutes forfait incluses
            
        Returns:
            Dict avec détails calcul
        """
        # Convertir forfait en secondes
        forfait_secondes = forfait_minutes * 60
        
        # Durée hors forfait
        hors_forfait_secondes = max(0, duree_secondes - forfait_secondes)
        
        if hors_forfait_secondes == 0:
            return {
                'duree_total_secondes': duree_secondes,
                'duree_total_minutes': duree_secondes / 60,
                'duree_forfait_minutes': forfait_minutes,
                'duree_hors_forfait_secondes': 0,
                'duree_hors_forfait_minutes': 0,
                'montant_ht': Decimal('0'),
                'details': 'Consommation dans le forfait'
            }
        
        # Appliquer la règle de tarification VOIX
        # 0-30s : demi-tarif, >30s : tarif complet par minute
        montant_ht = Decimal('0')
        details_appels = []
        
        # Pour simplifier, on calcule par minute entamée
        # Si appel <= 30s : 79 FCFA / 2 = 39.5 FCFA
        # Si appel > 30s : 79 FCFA (tarif complet par minute)
        
        # On considère que chaque tranche de 60s = 1 appel pour la démonstration
        # En réalité, il faudrait les détails appel par appel
        
        # Calcul simplifié : minutes hors forfait
        minutes_hors_forfait = math.ceil(hors_forfait_secondes / 60)
        
        # Hypothèse : 70% appels > 30s (tarif complet), 30% <= 30s (demi-tarif)
        # Pour simplification, on applique 85% du tarif plein en moyenne
        facteur_moyen = Decimal('0.85')
        montant_ht = cls.TARIF_VOIX_PAR_MINUTE * minutes_hors_forfait * facteur_moyen
        
        details = f"{minutes_hors_forfait} minutes × {cls.TARIF_VOIX_PAR_MINUTE} FCFA/min (facteur moyen {facteur_moyen})"
        
        return {
            'duree_total_secondes': duree_secondes,
            'duree_total_minutes': round(duree_secondes / 60, 2),
            'duree_forfait_minutes': forfait_minutes,
            'duree_hors_forfait_secondes': hors_forfait_secondes,
            'duree_hors_forfait_minutes': round(hors_forfait_secondes / 60, 2),
            'minutes_facturees': minutes_hors_forfait,
            'montant_ht': montant_ht,
            'details': details
        }
    
    @classmethod
    def calculer_sms(cls, nombre_sms: int, forfait_sms: int = 0) -> Dict:
        """
        Calculer le coût SMS
        
        Args:
            nombre_sms: Nombre de SMS envoyés
            forfait_sms: SMS forfait inclus
            
        Returns:
            Dict avec détails calcul
        """
        # SMS hors forfait
        hors_forfait_sms = max(0, nombre_sms - forfait_sms)
        
        if hors_forfait_sms == 0:
            return {
                'nombre_total_sms': nombre_sms,
                'nombre_forfait_sms': forfait_sms,
                'nombre_hors_forfait_sms': 0,
                'montant_ht': Decimal('0'),
                'details': 'Consommation dans le forfait'
            }
        
        montant_ht = cls.TARIF_SMS_UNITAIRE * hors_forfait_sms
        details = f"{hors_forfait_sms} SMS × {cls.TARIF_SMS_UNITAIRE} FCFA/SMS"
        
        return {
            'nombre_total_sms': nombre_sms,
            'nombre_forfait_sms': forfait_sms,
            'nombre_hors_forfait_sms': hors_forfait_sms,
            'montant_ht': montant_ht,
            'details': details
        }
    
    @classmethod
    def calculer_tva(cls, montant_ht: Decimal) -> Dict:
        """
        Calculer TVA (18% au Togo)
        
        Args:
            montant_ht: Montant hors taxe
            
        Returns:
            Dict avec HT, TVA, TTC
        """
        montant_tva = montant_ht * cls.TAUX_TVA
        montant_ttc = montant_ht + montant_tva
        
        return {
            'montant_ht': montant_ht,
            'taux_tva': cls.TAUX_TVA,
            'montant_tva': montant_tva,
            'montant_ttc': montant_ttc
        }
    
    @classmethod
    def calculer_facture_ligne(
        cls,
        forfait_prix: Decimal,
        forfait_data_mo: int = 0,
        forfait_minutes: int = 0,
        forfait_sms: int = 0,
        conso_data_mo: int = 0,
        conso_duree_secondes: int = 0,
        conso_sms: int = 0,
        services_supplementaires: List[Dict] = None
    ) -> Dict:
        """
        Calculer la facture complète d'une ligne
        
        Args:
            forfait_prix: Prix mensuel du forfait
            forfait_data_mo: Quota DATA forfait (Mo)
            forfait_minutes: Quota minutes forfait
            forfait_sms: Quota SMS forfait
            conso_data_mo: Consommation DATA (Mo)
            conso_duree_secondes: Consommation VOIX (secondes)
            conso_sms: Consommation SMS
            services_supplementaires: Liste des services optionnels avec prix
            
        Returns:
            Dict avec détail complet de la facture
        """
        # Calcul DATA
        detail_data = cls.calculer_data(conso_data_mo, forfait_data_mo)
        
        # Calcul VOIX
        detail_voix = cls.calculer_voix(conso_duree_secondes, forfait_minutes)
        
        # Calcul SMS
        detail_sms = cls.calculer_sms(conso_sms, forfait_sms)
        
        # Montant forfait
        montant_forfait = forfait_prix
        
        # Montant hors forfait
        montant_hors_forfait = (
            detail_data['montant_ht'] +
            detail_voix['montant_ht'] +
            detail_sms['montant_ht']
        )
        
        # Services supplémentaires
        montant_services = Decimal('0')
        details_services = []
        if services_supplementaires:
            for service in services_supplementaires:
                prix = Decimal(str(service.get('prix', 0)))
                montant_services += prix
                details_services.append({
                    'nom': service.get('nom'),
                    'prix': prix
                })
        
        # Total HT
        montant_ht_total = montant_forfait + montant_hors_forfait + montant_services
        
        # TVA et TTC
        calcul_tva = cls.calculer_tva(montant_ht_total)
        
        return {
            'forfait': {
                'prix': montant_forfait,
                'data_mo': forfait_data_mo,
                'minutes': forfait_minutes,
                'sms': forfait_sms
            },
            'consommations': {
                'data': detail_data,
                'voix': detail_voix,
                'sms': detail_sms
            },
            'hors_forfait': {
                'data': detail_data['montant_ht'],
                'voix': detail_voix['montant_ht'],
                'sms': detail_sms['montant_ht'],
                'total': montant_hors_forfait
            },
            'services_supplementaires': {
                'montant': montant_services,
                'details': details_services
            },
            'totaux': {
                'forfait': montant_forfait,
                'hors_forfait': montant_hors_forfait,
                'services': montant_services,
                'montant_ht': calcul_tva['montant_ht'],
                'montant_tva': calcul_tva['montant_tva'],
                'montant_ttc': calcul_tva['montant_ttc']
            }
        }


# Fonctions utilitaires
def formater_montant(montant: Decimal) -> str:
    """Formater un montant en FCFA"""
    return f"{montant:,.0f} FCFA".replace(',', ' ')


def convertir_mo_en_go(mo: int) -> float:
    """Convertir Mo en Go"""
    return round(mo / 1024, 2)


def convertir_secondes_en_minutes(secondes: int) -> float:
    """Convertir secondes en minutes"""
    return round(secondes / 60, 2)
