"""Normalise un export SQLite avant son import dans PostgreSQL."""

import json
import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError


CATEGORY_CODES = {
    'GRANDE_ENTREPRISE': 'GE',
    'PETITE_ENTREPRISE': 'PE',
    'PARTICULIER': 'P',
    'ORGANISME_INTERNATIONAL': 'OI',
    'ENTREPRISE_PUBLIQUE': 'EP',
    'ASSOCIATION': 'A',
    'NON_REVENU': 'NR',
}


class Command(BaseCommand):
    help = (
        "Crée une copie d'un export SQLite compatible avec les contraintes PostgreSQL. "
        "Le fichier source n'est jamais modifié."
    )

    def add_arguments(self, parser):
        parser.add_argument('--input', required=True, help="Chemin du fichier JSON issu de dumpdata.")
        parser.add_argument('--output', required=True, help="Chemin du fichier JSON normalisé à créer.")

    def handle(self, *args, **options):
        input_path = Path(options['input'])
        output_path = Path(options['output'])
        if not input_path.is_file():
            raise CommandError(f"Fichier source introuvable : {input_path}")
        if output_path.exists():
            raise CommandError(f"Le fichier de sortie existe déjà : {output_path}")

        records = json.loads(input_path.read_text(encoding='utf-8'))
        normalised_phones = 0
        normalised_categories = 0

        for record in records:
            fields = record['fields']
            if record['model'] == 'accounts.user' and fields.get('telephone'):
                digits = re.sub(r'\D', '', fields['telephone'])
                if len(digits) > 8:
                    if len(digits) == 11 and digits.startswith('228'):
                        fields['telephone'] = digits[-8:]
                        normalised_phones += 1
                    else:
                        raise CommandError(
                            f"Utilisateur {record['pk']} : numéro de téléphone non normalisable "
                            f"({len(digits)} chiffres)."
                        )

            if record['model'] == 'billing.company':
                category = fields.get('categorie')
                if category in CATEGORY_CODES:
                    fields['categorie'] = CATEGORY_CODES[category]
                    normalised_categories += 1

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(records, ensure_ascii=False, indent=2),
            encoding='utf-8',
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Fichier normalisé créé : {output_path} — "
                f"{normalised_phones} numéro(s), {normalised_categories} catégorie(s)."
            )
        )
