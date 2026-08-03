"""
Service de traitement et découpage de PDF
Permet de découper un gros PDF en factures individuelles par client
"""
import re
import os
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
    NUMERO_FACTURE_PATTERN = r'\b(A[0-9]{11,}|FAC-[A-Z0-9\-]+)\b'  # Numéro facture (format A202606... ou FAC-...)
    
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
        
        # Chercher Numéro facture
        facture_match = re.search(cls.NUMERO_FACTURE_PATTERN, text)
        if facture_match:
            identifiers['numero_facture'] = facture_match.group(1)
        
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
                current = {'start_page': page_num, 'end_page': page_num,
                           'identifiers': {'compte': compte}, 'pages': [page_num]}
                if identifiers.get('numero_facture'):
                    current['identifiers']['numero_facture'] = identifiers['numero_facture']
            elif current:
                current['end_page'] = page_num
                current['pages'].append(page_num)
                if 'numero_facture' not in current['identifiers'] and identifiers.get('numero_facture'):
                    current['identifiers']['numero_facture'] = identifiers['numero_facture']
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
        # Priorité 1 : Numéro de facture EXACT
        if 'numero_facture' in identifiers:
            invoice = invoices_queryset.filter(
                numero_facture=identifiers['numero_facture']
            ).first()
            if invoice:
                return invoice
        
        # Priorité 2 : MSISDN via relation ligne (pour PDF SOM)
        # Une facture SOM doit être reliée à la ligne exacte. Rechercher
        # seulement par entreprise pouvait retourner une autre facture de la
        # même entreprise lorsque celle-ci possède plusieurs lignes.
        if 'msisdn' in identifiers:
            invoice = invoices_queryset.filter(
                line__msisdn=identifiers['msisdn']
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
            invoice = invoices_queryset.filter(numero_facture=identifiers['numero_facture']).first()
            if invoice:
                return invoice
        if identifiers.get('compte'):
            candidates = invoices_queryset.filter(company__compte=identifiers['compte'])[:2]
            return candidates[0] if len(candidates) == 1 else None
        return None
    
    @classmethod
    def auto_attach_pdfs(cls, created_files: List[Dict], invoices_queryset, processed_invoices_queryset=None, invoice_type='SOM') -> Dict:
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
            'skipped': [],
            'errors': []
        }
        
        for file_info in created_files:
            identifiers = file_info['identifiers']
            
            # D'abord vérifier si la facture est déjà traitée (VALIDEE, PUBLIEE, PAYEE)
            processed_invoice = None
            if processed_invoices_queryset is not None:
                matcher = cls.match_global_pdf_to_invoice if invoice_type == 'GLO' else cls.match_pdf_to_invoice
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
                    # Une facture SOM est reliée à sa ligne, afin que seul
                    # l'employé titulaire de ce MSISDN puisse la consulter.
                    if 'msisdn' in identifiers and not invoice.line_id:
                        from ..models import Line
                        line = Line.objects.filter(
                            company=invoice.company,
                            msisdn=identifiers['msisdn']
                        ).first()
                        if line:
                            invoice.line = line

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
                    'error': 'Aucune facture correspondante trouvée',
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
