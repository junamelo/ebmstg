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
    
    @staticmethod
    def check_dependencies():
        """Vérifier que les dépendances sont installées"""
        if not PDF_AVAILABLE:
            raise ImportError(
                "PyPDF2 n'est pas installé. "
                "Installer avec: pip install PyPDF2"
            )
    
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
    def analyze_pdf_structure(cls, pdf_file) -> List[Dict]:
        """
        Analyser la structure du PDF et détecter les blocs par client
        
        Args:
            pdf_file: Fichier PDF à analyser
            
        Returns:
            Liste de blocs avec pages et identifiants
        """
        cls.check_dependencies()
        
        reader = PdfReader(pdf_file)
        total_pages = len(reader.pages)
        
        blocks = []
        current_block = None
        
        for page_num in range(total_pages):
            page = reader.pages[page_num]
            text = cls.extract_text_from_page(page)
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
        
        # Ajouter le dernier bloc
        if current_block is not None:
            blocks.append(current_block)
        
        return blocks
    
    @classmethod
    def split_pdf_by_blocks(
        cls,
        pdf_file,
        blocks: List[Dict],
        output_dir: str = None
    ) -> List[Dict]:
        """
        Découper un PDF en plusieurs fichiers selon les blocs détectés
        
        Args:
            pdf_file: Fichier PDF source
            blocks: Liste des blocs à extraire
            output_dir: Répertoire de sortie (défaut: media/factures/splits/)
            
        Returns:
            Liste des fichiers créés avec métadonnées
        """
        cls.check_dependencies()
        
        if output_dir is None:
            output_dir = os.path.join(settings.MEDIA_ROOT, 'factures', 'splits')
        
        # Créer le répertoire si nécessaire
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        reader = PdfReader(pdf_file)
        created_files = []
        
        for idx, block in enumerate(blocks):
            # Créer un nouveau PDF pour ce bloc
            writer = PdfWriter()
            
            # Ajouter les pages du bloc
            for page_num in block['pages']:
                writer.add_page(reader.pages[page_num])
            
            # Générer nom de fichier
            identifiers = block['identifiers']
            if 'numero_facture' in identifiers:
                filename = f"{identifiers['numero_facture']}.pdf"
            elif 'msisdn' in identifiers:
                filename = f"facture_{identifiers['msisdn']}.pdf"
            elif 'compte' in identifiers:
                filename = f"facture_{identifiers['compte']}.pdf"
            else:
                filename = f"facture_bloc_{idx + 1}.pdf"
            
            output_path = os.path.join(output_dir, filename)
            
            # Écrire le fichier
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            created_files.append({
                'filename': filename,
                'path': output_path,
                'relative_path': os.path.relpath(output_path, settings.MEDIA_ROOT),
                'identifiers': identifiers,
                'pages': len(block['pages'])
            })
        
        return created_files
    
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
        blocks = cls.analyze_pdf_structure(pdf_file)
        
        # 2. Découper en fichiers individuels
        created_files = cls.split_pdf_by_blocks(pdf_file, blocks)
        
        # 3. Statistiques
        result = {
            'total_pages': sum(len(block['pages']) for block in blocks),
            'total_blocks': len(blocks),
            'files_created': len(created_files),
            'blocks': blocks,
            'files': created_files,
            'success': True
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
        # Priorité 1 : Numéro de facture
        if 'numero_facture' in identifiers:
            invoice = invoices_queryset.filter(
                numero_facture=identifiers['numero_facture']
            ).first()
            if invoice:
                return invoice
        
        # Priorité 2 : MSISDN exact (via ligne) - PLUS PRÉCIS POUR PDF SOM
        # Pour les factures individuelles, on matche directement par MSISDN
        if 'msisdn' in identifiers:
            # Chercher une facture dont le numéro contient le MSISDN
            invoice = invoices_queryset.filter(
                numero_facture__contains=identifiers['msisdn']
            ).first()
            if invoice:
                return invoice
            
            # Sinon, chercher via la relation ligne (moins précis)
            invoice = invoices_queryset.filter(
                company__lines__msisdn=identifiers['msisdn']
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
    
    @classmethod
    def auto_attach_pdfs(cls, created_files: List[Dict], invoices_queryset, processed_invoices_queryset=None) -> Dict:
        """
        Attacher automatiquement les PDF découpés aux factures
        
        Args:
            created_files: Liste des fichiers créés par le découpage
            invoices_queryset: QuerySet de factures candidates
            
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
            
            # Chercher la facture correspondante
            invoice = cls.match_pdf_to_invoice(identifiers, invoices_queryset)
            
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
                # Lors d'un second upload du même fichier, la facture peut déjà
                # avoir été traitée. Ce n'est pas une erreur de rapprochement.
                processed_invoice = None
                if processed_invoices_queryset is not None:
                    processed_invoice = cls.match_pdf_to_invoice(
                        identifiers, processed_invoices_queryset
                    )

                if processed_invoice:
                    results['skipped'].append({
                        'invoice_id': str(processed_invoice.id),
                        'numero_facture': processed_invoice.numero_facture,
                        'filename': file_info['filename'],
                        'reason': f'Facture déjà traitée ({processed_invoice.statut})'
                    })
                else:
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
