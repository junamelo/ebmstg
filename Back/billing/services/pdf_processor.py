"""
Service de traitement et découpage de PDF
Permet de découper un gros PDF en factures individuelles par client
"""
import re
import os
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Tuple
from pathlib import Path
from django.conf import settings
from django.core.files.base import ContentFile

try:
    from PyPDF2 import PdfReader, PdfWriter
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ PyPDF2 non installé. Installer avec: pip install PyPDF2")


class PDFProcessor:
    """
    Processeur de PDF pour découpage automatique
    """
    
    # Patterns de recherche
    # Les numéros mobiles présents dans les factures de test commencent par 7
    # ou 9. L'ancien motif ne reconnaissait que ceux commençant par 9, ce qui
    # empêchait le rapprochement des lignes 79xxxxxx.
    MSISDN_PATTERN = r'\b([79][0-9]{7})\b'
    COMPTE_PATTERN = r'\b(A[0-9]{7}|C26[A-Z0-9]{6,10})\b'  # Compte Moov (format A + 7 chiffres OU C26...)
    NUMERO_FACTURE_PATTERN = r'\b(FAC-[A-Z0-9\-]+|[A-Z]{3,}[0-9]{8,})\b'
    
    # Limites de sécurité
    MAX_PAGES = 1000  # Limite de pages par PDF
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 Mo max
    
    @staticmethod
    def check_dependencies():
        """Vérifier que les dépendances sont installées"""
        if not PDF_AVAILABLE:
            raise ImportError(
                "PyPDF2 n'est pas installé. "
                "Installer avec: pip install PyPDF2"
            )
    
    @staticmethod
    def validate_pdf(pdf_file) -> Dict:
        """
        Valider qu'un fichier PDF est lisible et conforme
        
        Args:
            pdf_file: Fichier PDF à valider
            
        Returns:
            Dict avec is_valid, error_message, metadata
        """
        try:
            reader = PdfReader(pdf_file)
            
            # Vérifier si le PDF est chiffré
            if reader.is_encrypted:
                return {
                    'is_valid': False,
                    'error_message': 'Le PDF est protégé par mot de passe',
                    'metadata': None
                }
            
            # Vérifier le nombre de pages
            num_pages = len(reader.pages)
            if num_pages == 0:
                return {
                    'is_valid': False,
                    'error_message': 'Le PDF ne contient aucune page',
                    'metadata': None
                }
            
            if num_pages > PDFProcessor.MAX_PAGES:
                return {
                    'is_valid': False,
                    'error_message': f'Le PDF contient trop de pages ({num_pages} > {PDFProcessor.MAX_PAGES})',
                    'metadata': None
                }
            
            # Tentative d'extraction de texte sur la première page
            # Note: Même si le texte est vide, on accepte le PDF
            # (peut être une page de garde ou un PDF avec peu de contenu)
            try:
                first_page = reader.pages[0]
                text = first_page.extract_text()
                has_text = text and len(text.strip()) > 0
            except Exception:
                # Si l'extraction échoue, on accepte quand même
                # Le traitement ultérieur gérera les pages problématiques
                has_text = False
            
            return {
                'is_valid': True,
                'error_message': None,
                'metadata': {
                    'num_pages': num_pages,
                    'encrypted': False,
                    'has_text': has_text
                }
            }
            
        except Exception as e:
            return {
                'is_valid': False,
                'error_message': f'Erreur lors de la lecture du PDF: {str(e)}',
                'metadata': None
            }
    
    @classmethod
    def extract_text_from_page(cls, page) -> str:
        """
        Extraire le texte d'une page PDF
        
        Args:
            page: Page PyPDF2
            
        Returns:
            Texte extrait de la page
        """
        try:
            return page.extract_text()
        except Exception as e:
            print(f"Erreur extraction texte : {e}")
            return ""
    
    @classmethod
    def find_identifiers(cls, text: str) -> Dict[str, str]:
        """
        Trouver les identifiants dans le texte (MSISDN, Compte, etc.)
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dict avec les identifiants trouvés
        """
        identifiers = {}
        
        # Chercher MSISDN
        msisdn_match = re.search(cls.MSISDN_PATTERN, text)
        if msisdn_match:
            identifiers['msisdn'] = msisdn_match.group(1)
        
        # Chercher Compte
        compte_match = re.search(cls.COMPTE_PATTERN, text)
        if compte_match:
            identifiers['compte'] = compte_match.group(1)
        
        # Chercher le numéro de facture. Dans certains PDF Moov, il est collé
        # au nom de l'utilisateur (ex. « MARIEA20260601041 ») : on recherche
        # donc d'abord le format A + 11 chiffres sans exiger de frontière de mot.
        facture_match = re.search(r'A[0-9]{11,}', text)
        if not facture_match:
            facture_match = re.search(cls.NUMERO_FACTURE_PATTERN, text)
        if facture_match:
            identifiers['numero_facture'] = facture_match.group(1) if facture_match.lastindex else facture_match.group(0)

        dates = re.findall(r'\b(\d{2}/\d{2}/\d{4})\b', text)
        periode_match = re.search(
            r'\b(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}/\d{2}/\d{4})\b',
            text,
        )
        if periode_match:
            identifiers['periode_debut'] = periode_match.group(1)
            identifiers['periode_fin'] = periode_match.group(2)
        if len(dates) >= 3:
            # Dans la mise en page Moov : début période, fin période, édition,
            # puis échéance.
            identifiers['date_emission_pdf'] = dates[2]
        if len(dates) >= 4:
            identifiers['date_echeance'] = dates[3]

        # La ligne TOTAL contient HT, TVA puis TTC. Le dernier montant est donc
        # celui qui doit être enregistré dans la facture.
        total_match = re.search(r'TOTAL\s*:\s*([0-9\s]+)', text, re.IGNORECASE)
        if total_match:
            montants = re.findall(r'\d{1,3}(?:\s\d{3})*', total_match.group(1))
            if montants:
                identifiers['montant_ttc'] = montants[-1].replace(' ', '')
            if len(montants) >= 2:
                identifiers['montant_tva'] = montants[-2].replace(' ', '')
            if len(montants) >= 3:
                identifiers['montant_ht'] = montants[-3].replace(' ', '')

        # Une facture globale contient plusieurs sous-totaux. Le « TOTAL » de
        # la dernière page peut agréger des colonnes de détail et former un
        # faux très grand nombre à l'extraction. La première page contient les
        # quatre montants de synthèse : montant courant, impayés, impayés et
        # total dû. Le premier de ces quatre est le montant TTC de la facture.
        if 'FACTURE GLOBALE' in text.upper():
            entete = re.split(r'D.{0,2}TAILS DU MONTANT', text, maxsplit=1, flags=re.IGNORECASE)[0]
            montants_entete = []
            for ligne in entete.splitlines():
                valeur = ' '.join(ligne.replace('\xa0', ' ').split())
                if re.fullmatch(r'\d{1,3}(?:\s\d{3})+', valeur):
                    montants_entete.append(valeur.replace(' ', ''))
            if len(montants_entete) >= 4:
                identifiers['montant_ttc'] = montants_entete[-4]
                identifiers['montant_ht'] = '0'
                identifiers['montant_tva'] = '0'
        
        return identifiers
    
    @classmethod
    def analyze_pdf_structure(cls, pdf_file) -> Dict:
        """
        Analyser la structure du PDF et détecter les blocs par client
        
        Args:
            pdf_file: Fichier PDF à analyser
            
        Returns:
            Dict avec blocks, errors, warnings
        """
        cls.check_dependencies()
        
        # Valider le PDF d'abord
        validation = cls.validate_pdf(pdf_file)
        if not validation['is_valid']:
            return {
                'success': False,
                'error': validation['error_message'],
                'blocks': [],
                'warnings': []
            }

        pdf_file.seek(0)
        try:
            reader = PdfReader(pdf_file)
            blocks, current_block, errors_per_page, warnings = [], None, [], []
            for page_num, page in enumerate(reader.pages):
                try:
                    text = cls.extract_text_from_page(page)
                    identifiers = cls.find_identifiers(text) if text and len(text.strip()) >= 10 else {}
                    if identifiers:
                        if current_block:
                            blocks.append(current_block)
                        current_block = {'start_page': page_num, 'end_page': page_num, 'identifiers': identifiers, 'pages': [page_num]}
                    elif current_block:
                        current_block['end_page'] = page_num
                        current_block['pages'].append(page_num)
                    else:
                        warnings.append(f"Page {page_num + 1}: Aucun identifiant trouvé")
                except Exception as error:
                    errors_per_page.append({'page': page_num + 1, 'error': str(error)})
            if current_block:
                blocks.append(current_block)
            return {'success': True, 'blocks': blocks, 'total_pages': len(reader.pages), 'errors_per_page': errors_per_page, 'warnings': warnings}
        except Exception as error:
            return {'success': False, 'error': f"Erreur lors de l'analyse du PDF: {error}", 'blocks': [], 'warnings': []}

    @classmethod
    def analyze_global_pdf_structure(cls, pdf_file) -> Dict:
        """Regroupe les pages contiguës d'un même compte pour un PDF GLO."""
        cls.check_dependencies()
        validation = cls.validate_pdf(pdf_file)
        if not validation['is_valid']:
            return {'success': False, 'error': validation['error_message'], 'blocks': [], 'warnings': []}
        pdf_file.seek(0)
        reader = PdfReader(pdf_file)
        blocks, warnings, current = [], [], None
        for page_num, page in enumerate(reader.pages):
            identifiers = cls.find_identifiers(cls.extract_text_from_page(page))
            compte = identifiers.get('compte')
            if compte and (current is None or current['identifiers'].get('compte') != compte):
                if current:
                    blocks.append(current)
                # Conserver toutes les données de la première page du bloc :
                # elles sont nécessaires pour créer une facture globale si elle
                # n'existe pas encore en base (période, montant, échéance...).
                current = {
                    'start_page': page_num,
                    'end_page': page_num,
                    'identifiers': identifiers.copy(),
                    'pages': [page_num],
                }
            elif current:
                current['end_page'] = page_num
                current['pages'].append(page_num)
                # Certaines informations peuvent apparaître sur une page
                # suivante : compléter uniquement les valeurs absentes.
                for cle, valeur in identifiers.items():
                    current['identifiers'].setdefault(cle, valeur)
            else:
                warnings.append(f"Page {page_num + 1}: compte entreprise introuvable")
        if current:
            blocks.append(current)
        return {'success': bool(blocks), 'blocks': blocks, 'total_pages': len(reader.pages),
                'errors_per_page': [], 'warnings': warnings}

    @classmethod
    def process_global_pdf(cls, pdf_file) -> Dict:
        analysis = cls.analyze_global_pdf_structure(pdf_file)
        if not analysis['success']:
            return {'success': False, 'error': analysis.get('error', 'Aucun bloc global détecté'), 'blocks': [], 'files': []}
        pdf_file.seek(0)
        split_result = cls.split_pdf_by_blocks(pdf_file, analysis['blocks'])
        return {'success': bool(split_result['files']), 'total_pages': analysis['total_pages'],
                'total_blocks': len(analysis['blocks']), 'files_created': len(split_result['files']),
                'blocks': analysis['blocks'], 'files': split_result['files'],
                'errors_per_page': [], 'split_errors': split_result['errors'], 'warnings': analysis['warnings']}
        
        pdf_file.seek(0)  # Remettre le curseur au début
        
        try:
            reader = PdfReader(pdf_file)
            total_pages = len(reader.pages)
            
            blocks = []
            current_block = None
            errors_per_page = []
            warnings = []
            
            for page_num in range(total_pages):
                try:
                    page = reader.pages[page_num]
                    text = cls.extract_text_from_page(page)
                    
                    if not text or len(text.strip()) < 10:
                        warnings.append(f"Page {page_num + 1}: Très peu de texte extrait")
                        # Continuer avec le bloc actuel si existant
                        if current_block is not None:
                            current_block['end_page'] = page_num
                            current_block['pages'].append(page_num)
                        continue
                    
                    identifiers = cls.find_identifiers(text)
                    
                    # Si on trouve des identifiants, c'est potentiellement un nouveau bloc
                    if identifiers:
                        # Si on a un bloc en cours, le sauvegarder
                        if current_block is not None:
                            blocks.append(current_block)
                        
                        # Créer nouveau bloc
                        current_block = {
                            'start_page': page_num,
                            'end_page': page_num,
                            'identifiers': identifiers,
                            'pages': [page_num]
                        }
                    elif current_block is not None:
                        # Ajouter la page au bloc en cours
                        current_block['end_page'] = page_num
                        current_block['pages'].append(page_num)
                    else:
                        # Pas d'identifiants et pas de bloc en cours
                        warnings.append(
                            f"Page {page_num + 1}: Aucun identifiant trouvé (ni MSISDN, ni numéro facture)"
                        )
                
                except Exception as e:
                    errors_per_page.append({
                        'page': page_num + 1,
                        'error': str(e)
                    })
            
            # Ajouter le dernier bloc
            if current_block is not None:
                blocks.append(current_block)
            
            return {
                'success': True,
                'blocks': blocks,
                'total_pages': total_pages,
                'errors_per_page': errors_per_page,
                'warnings': warnings
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erreur lors de l\'analyse du PDF: {str(e)}',
                'blocks': [],
                'warnings': []
            }
    
    @classmethod
    def split_pdf_by_blocks(
        cls,
        pdf_file,
        blocks: List[Dict],
        output_dir: str = None
    ) -> Dict:
        """
        Découper un PDF en plusieurs fichiers selon les blocs détectés
        
        Args:
            pdf_file: Fichier PDF source
            blocks: Liste des blocs à extraire
            output_dir: Répertoire de sortie (défaut: media/factures/splits/)
            
        Returns:
            Dict avec success, files, errors
        """
        cls.check_dependencies()
        
        if output_dir is None:
            output_dir = os.path.join(settings.MEDIA_ROOT, 'factures', 'splits')
        
        # Créer le répertoire si nécessaire
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        pdf_file.seek(0)  # Remettre le curseur au début
        reader = PdfReader(pdf_file)
        created_files = []
        errors = []
        
        for idx, block in enumerate(blocks):
            try:
                # Créer un nouveau PDF pour ce bloc
                writer = PdfWriter()
                
                # Ajouter les pages du bloc
                for page_num in block['pages']:
                    if page_num < len(reader.pages):
                        writer.add_page(reader.pages[page_num])
                    else:
                        errors.append({
                            'block_index': idx,
                            'error': f'Page {page_num} hors limites (PDF a {len(reader.pages)} pages)'
                        })
                        continue
                
                # Générer nom de fichier unique
                identifiers = block['identifiers']
                # Utiliser timestamp Unix ou timestamp depuis epoch
                import time
                try:
                    if hasattr(pdf_file, 'name') and os.path.exists(pdf_file.name):
                        timestamp = int(os.path.getmtime(pdf_file.name))
                    else:
                        timestamp = int(time.time())
                except (OSError, AttributeError):
                    timestamp = int(time.time())
                
                if 'numero_facture' in identifiers:
                    base_filename = f"{identifiers['numero_facture']}"
                elif 'msisdn' in identifiers:
                    base_filename = f"facture_{identifiers['msisdn']}"
                elif 'compte' in identifiers:
                    base_filename = f"facture_{identifiers['compte']}"
                else:
                    base_filename = f"facture_bloc_{idx + 1}"
                
                # Ajouter un suffix pour éviter les collisions
                filename = f"{base_filename}_{timestamp}_{idx}.pdf"
                output_path = os.path.join(output_dir, filename)
                
                # Si le fichier existe déjà, ajouter un compteur
                counter = 1
                while os.path.exists(output_path):
                    filename = f"{base_filename}_{timestamp}_{idx}_{counter}.pdf"
                    output_path = os.path.join(output_dir, filename)
                    counter += 1
                
                # Écrire le fichier
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                created_files.append({
                    'filename': filename,
                    'path': output_path,
                    'relative_path': os.path.relpath(output_path, settings.MEDIA_ROOT),
                    'identifiers': identifiers,
                    'pages': len(block['pages']),
                    'block_index': idx
                })
                
            except Exception as e:
                errors.append({
                    'block_index': idx,
                    'identifiers': block.get('identifiers', {}),
                    'error': str(e)
                })
        
        return {
            'success': len(errors) == 0 or len(created_files) > 0,
            'files': created_files,
            'errors': errors
        }
    
    @classmethod
    def process_bulk_pdf(cls, pdf_file) -> Dict:
        """
        Traiter un gros PDF en détectant et découpant automatiquement
        
        Args:
            pdf_file: Fichier PDF à traiter
            
        Returns:
            Dict avec résultats du traitement
        """
        cls.check_dependencies()
        
        # 1. Analyser la structure
        analysis = cls.analyze_pdf_structure(pdf_file)
        
        if not analysis['success']:
            return {
                'success': False,
                'error': analysis.get('error', 'Erreur inconnue lors de l\'analyse'),
                'blocks': [],
                'files': [],
                'warnings': analysis.get('warnings', [])
            }
        
        blocks = analysis['blocks']
        
        if not blocks:
            return {
                'success': False,
                'error': 'Aucun bloc de facture détecté dans le PDF',
                'total_pages': analysis.get('total_pages', 0),
                'blocks': [],
                'files': [],
                'warnings': analysis.get('warnings', [])
            }
        
        pdf_file.seek(0)  # Remettre le curseur au début
        
        # 2. Découper en fichiers individuels
        split_result = cls.split_pdf_by_blocks(pdf_file, blocks)
        
        if not split_result['success'] and not split_result['files']:
            return {
                'success': False,
                'error': 'Échec du découpage du PDF',
                'total_pages': analysis.get('total_pages', 0),
                'blocks': blocks,
                'files': [],
                'split_errors': split_result['errors'],
                'warnings': analysis.get('warnings', [])
            }
        
        # 3. Statistiques
        result = {
            'success': True,
            'total_pages': analysis.get('total_pages', 0),
            'total_blocks': len(blocks),
            'files_created': len(split_result['files']),
            'blocks': blocks,
            'files': split_result['files'],
            'errors_per_page': analysis.get('errors_per_page', []),
            'split_errors': split_result['errors'],
            'warnings': analysis.get('warnings', [])
        }
        
        return result


class PDFMatcher:
    """
    Service pour matcher les PDF découpés avec les factures en base
    """
    
    @staticmethod
    def match_pdf_to_invoice(identifiers: Dict, invoices_queryset):
        """
        Trouver la facture correspondant aux identifiants
        
        Args:
            identifiers: Dict avec MSISDN, compte, numéro facture
            invoices_queryset: QuerySet de factures
            
        Returns:
            Facture trouvée ou None
        """
        # Priorité 1 : MSISDN via relation ligne (pour PDF SOM).
        # Les PDF Moov peuvent partager un même numéro de facture imprimé pour
        # plusieurs lignes d'une entreprise ; le MSISDN est alors le seul
        # identifiant réellement unique de la facture sommaire.
        if 'msisdn' in identifiers:
            invoices = invoices_queryset.filter(line__msisdn=identifiers['msisdn'])
            if identifiers.get('compte'):
                invoices = invoices.filter(company__compte=identifiers['compte'])
            invoice = invoices.first()
            if invoice:
                return invoice

        # Priorité 2 : Numéro de facture exact, si aucune ligne n'est connue.
        if identifiers.get('numero_facture'):
            invoice = invoices_queryset.filter(
                numero_facture=identifiers['numero_facture']
            ).first()
            if invoice:
                return invoice
        
        # Priorité 3 : Compte entreprise (seulement si pas de MSISDN)
        # Utilisé pour les PDF globaux (GLO) où il n'y a qu'une facture par entreprise
        if 'compte' in identifiers and 'msisdn' not in identifiers:
            invoice = invoices_queryset.filter(
                company__compte=identifiers['compte']
            ).first()
            if invoice:
                return invoice
        
        return None

    @staticmethod
    def match_global_pdf_to_invoice(identifiers: Dict, invoices_queryset):
        """Rapproche une GLO par numéro exact, sinon par compte si non ambigu."""
        if identifiers.get('numero_facture'):
            invoices = invoices_queryset.filter(
                numero_facture_pdf=identifiers['numero_facture']
            )
            if identifiers.get('compte'):
                invoices = invoices.filter(company__compte=identifiers['compte'])
            invoice = invoices.first()
            if invoice:
                return invoice
            # Compatibilité avec les factures importées avant l'ajout du champ
            # numero_facture_pdf.
            invoice = invoices_queryset.filter(
                numero_facture=identifiers['numero_facture']
            ).first()
            if invoice:
                return invoice
        if identifiers.get('compte'):
            candidates = invoices_queryset.filter(company__compte=identifiers['compte'])[:2]
            return candidates[0] if len(candidates) == 1 else None
        return None

    @staticmethod
    def _date_depuis_pdf(valeur):
        return datetime.strptime(valeur, '%d/%m/%Y').date()

    @classmethod
    def creer_facture_depuis_pdf(cls, identifiers: Dict, invoice_type: str):
        """Crée une facture en attente si le contrat/la ligne existe déjà.

        Cette solution évite de bloquer un import lorsque les contrats et les
        lignes sont présents mais qu'aucune facture provisoire n'a été créée
        avant la réception du bloc PDF.
        """
        from ..models import Company, Invoice, Line

        requis = ('periode_debut', 'periode_fin', 'date_echeance')
        if invoice_type == 'SOM':
            requis = ('numero_facture', *requis)
        manquants = [champ for champ in requis if not identifiers.get(champ)]
        if manquants:
            return None, f"Informations PDF insuffisantes : {', '.join(manquants)}"

        try:
            periode_debut = cls._date_depuis_pdf(identifiers['periode_debut'])
            periode_fin = cls._date_depuis_pdf(identifiers['periode_fin'])
            date_echeance = cls._date_depuis_pdf(identifiers['date_echeance'])
            montant_ht = Decimal(identifiers.get('montant_ht', '0'))
            montant_tva = Decimal(identifiers.get('montant_tva', '0'))
            montant_ttc = Decimal(identifiers.get('montant_ttc', '0'))
        except (ValueError, InvalidOperation):
            return None, 'Informations de date ou de montant invalides dans le PDF'

        compte = identifiers.get('compte')
        line = None
        if invoice_type == 'SOM':
            msisdn = identifiers.get('msisdn')
            if not msisdn:
                return None, 'MSISDN absent de la facture sommaire'
            lignes = Line.objects.select_related('company').filter(msisdn=msisdn)
            if compte:
                lignes = lignes.filter(company__compte=compte)
            line = lignes.first()
            if not line:
                return None, 'Aucune ligne active ne correspond au MSISDN et au compte du PDF'
            company = line.company
        else:
            if not compte:
                return None, 'Compte entreprise absent de la facture globale'
            company = Company.objects.filter(compte=compte).first()
            if not company:
                return None, 'Aucun contrat ne correspond au compte du PDF'

        numero_pdf = identifiers.get('numero_facture', '')
        numero_interne = numero_pdf
        if invoice_type == 'SOM':
            # Le champ numero_facture est unique en base ; l'identifiant imprimé
            # pouvant être commun à plusieurs lignes, on le complète en interne
            # avec le MSISDN. L'interface affiche toujours numero_facture_pdf.
            numero_interne = f'{numero_pdf}-{line.msisdn}'
        else:
            # Le même numéro imprimé peut exister sur les factures sommaires
            # et la facture globale d'un contrat. Le numéro interne global est
            # donc préfixé ; le vrai numéro reste numero_facture_pdf.
            numero_interne = (
                f'GLO-{numero_pdf or company.compte}-{company.compte}-'
                f'{periode_debut:%Y%m%d}-{periode_fin:%Y%m%d}'
            )

        try:
            invoice = Invoice.objects.create(
                company=company,
                line=line,
                numero_facture=numero_interne,
                numero_facture_pdf=numero_pdf,
                periode_debut=periode_debut,
                periode_fin=periode_fin,
                montant_ht=montant_ht,
                montant_tva=montant_tva,
                montant_ttc=montant_ttc,
                date_echeance=date_echeance,
                statut='EN_COURS',
                commentaire='Facture créée automatiquement lors du rapprochement du bloc PDF.',
            )
        except Exception as exc:
            return None, f'Création de facture impossible : {exc}'

        return invoice, ''
    
    @classmethod
    def auto_attach_pdfs(
        cls,
        created_files: List[Dict],
        invoices_queryset,
        processed_invoices_queryset=None,
        invoice_type='SOM',
        creer_factures_absentes=False,
    ) -> Dict:
        """
        Attacher automatiquement les PDF découpés aux factures
        
        Args:
            created_files: Liste des fichiers créés par le découpage
            invoices_queryset: QuerySet de factures candidates (EN_COURS)
            processed_invoices_queryset: QuerySet de factures déjà traitées (VALIDEE, PUBLIEE, PAYEE)
            
        Returns:
            Dict avec résultats de l'attachement
        """
        results = {
            'total_files': len(created_files),
            'matched': 0,
            'not_matched': 0,
            'attached': [],
            'created': [],
            'skipped': [],
            'errors': []
        }
        
        for file_info in created_files:
            identifiers = file_info['identifiers']
            matcher = cls.match_global_pdf_to_invoice if invoice_type == 'GLO' else cls.match_pdf_to_invoice
            
            # D'abord vérifier si la facture est déjà traitée (VALIDEE, PUBLIEE, PAYEE)
            processed_invoice = None
            if processed_invoices_queryset is not None:
                processed_invoice = matcher(
                    identifiers, processed_invoices_queryset
                )
            
            if processed_invoice:
                # Facture déjà traitée : on skip
                results['skipped'].append({
                    'invoice_id': str(processed_invoice.id),
                    'numero_facture': processed_invoice.numero_facture,
                    'filename': file_info['filename'],
                    'reason': f'Facture déjà traitée ({processed_invoice.statut})'
                })
                continue
            
            # Sinon, chercher dans les factures EN_COURS
            invoice = matcher(identifiers, invoices_queryset)
            creation_erreur = ''
            if not invoice and creer_factures_absentes:
                invoice, creation_erreur = cls.creer_facture_depuis_pdf(
                    identifiers,
                    invoice_type,
                )
                if invoice:
                    results['created'].append({
                        'invoice_id': str(invoice.id),
                        'numero_facture': invoice.numero_facture,
                        'filename': file_info['filename'],
                    })
            
            if invoice:
                try:
                    # Attacher le PDF
                    with open(file_info['path'], 'rb') as pdf_file:
                        from django.core.files import File
                        invoice.fichier_pdf.save(
                            file_info['filename'],
                            File(pdf_file),
                            save=True
                        )
                    
                    # Changer statut si nécessaire
                    # Seule une facture SOM est reliée à une ligne : une GLO
                    # peut aussi afficher un MSISDN de contact dans son en-tête,
                    # sans pour autant appartenir à cette ligne.
                    if invoice_type == 'SOM' and 'msisdn' in identifiers and not invoice.line_id:
                        from ..models import Line
                        line = Line.objects.filter(
                            company=invoice.company,
                            msisdn=identifiers['msisdn']
                        ).first()
                        if line:
                            invoice.line = line

                    if identifiers.get('numero_facture'):
                        invoice.numero_facture_pdf = identifiers['numero_facture']
                    if identifiers.get('date_emission_pdf'):
                        from datetime import datetime
                        invoice.date_emission_pdf = datetime.strptime(
                            identifiers['date_emission_pdf'], '%d/%m/%Y'
                        ).date()

                    if invoice.statut == 'EN_COURS':
                        invoice.statut = 'VALIDEE'
                    invoice.save()
                    
                    results['matched'] += 1
                    results['attached'].append({
                        'invoice_id': str(invoice.id),
                        'numero_facture': invoice.numero_facture,
                        'filename': file_info['filename'],
                        'identifiers': identifiers
                    })
                    
                except Exception as e:
                    results['errors'].append({
                        'filename': file_info['filename'],
                        'error': str(e)
                    })
            else:
                # Aucune facture trouvée
                results['not_matched'] += 1
                results['errors'].append({
                    'filename': file_info['filename'],
                    'error': creation_erreur or 'Aucune facture correspondante trouvée',
                    'identifiers': identifiers
                })
        
        return results


# Fonctions utilitaires

def get_pdf_info(pdf_path: str) -> Dict:
    """Obtenir infos sur un PDF"""
    if not PDF_AVAILABLE:
        return {'error': 'PyPDF2 non disponible'}
    
    try:
        reader = PdfReader(pdf_path)
        return {
            'pages': len(reader.pages),
            'metadata': reader.metadata,
            'encrypted': reader.is_encrypted
        }
    except Exception as e:
        return {'error': str(e)}
