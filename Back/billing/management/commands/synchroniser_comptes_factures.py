"""Crée et rattache les comptes nécessaires à la consultation des factures publiées."""

import re

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import User
from billing.models import Company, Invoice, Line


def _nom_utilisateur(nom, fallback):
    """Produit un prénom/nom lisible, même si le PDF ne contient aucun titulaire."""
    morceaux = (nom or '').strip().split()
    if not morceaux:
        return fallback, ''
    return morceaux[0][:150], ' '.join(morceaux[1:])[:150]


def _telephone(msisdn):
    chiffres = re.sub(r'\D', '', msisdn or '')
    return chiffres[-8:] if len(chiffres) >= 8 else ''


class Command(BaseCommand):
    help = (
        "Crée les comptes payeurs et employés manquants puis les rattache aux "
        "contrats/lignes qui possèdent au moins une facture PUBLIEE. "
        "Sans --confirm, la commande reste une simulation."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--temporary-password',
            help='Mot de passe temporaire commun aux comptes créés. Obligatoire avec --confirm.',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Exécute réellement la création et les rattachements.',
        )
        parser.add_argument(
            '--only',
            choices=['PAYEURS', 'EMPLOYES'],
            help='Limite la synchronisation aux payeurs ou aux employés.',
        )

    def handle(self, *args, **options):
        if options['confirm'] and not options['temporary_password']:
            raise CommandError(
                'Pour créer des comptes, indiquez un mot de passe temporaire avec --temporary-password.'
            )

        invoice_ids = Invoice.objects.filter(statut='PUBLIEE')
        companies = Company.objects.filter(
            id__in=invoice_ids.values('company_id'),
            payeur__isnull=True,
        ).order_by('compte')
        lines = Line.objects.filter(
            id__in=invoice_ids.exclude(line__isnull=True).values('line_id'),
            employe__isnull=True,
        ).select_related('company').order_by('msisdn')

        existing_users = {
            user.username: user
            for user in User.objects.filter(
                username__in=list(companies.values_list('compte', flat=True))
                + list(lines.values_list('msisdn', flat=True))
            )
        }

        def analyse(cibles, role, identifiant):
            create, link, conflicts = [], [], []
            for cible in cibles:
                username = identifiant(cible)
                user = existing_users.get(username)
                if not user:
                    create.append(cible)
                elif user.role == role:
                    link.append((cible, user))
                else:
                    conflicts.append((cible, user))
            return create, link, conflicts

        payeurs_a_creer, payeurs_a_lier, conflits_payeur = analyse(
            companies, 'PAYEUR', lambda company: company.compte
        )
        employes_a_creer, employes_a_lier, conflits_employe = analyse(
            lines, 'EMPLOYE', lambda line: line.msisdn
        )

        self.stdout.write(
            'Factures publiées analysées : {}. Payeurs : {} à créer, {} à lier, {} conflit(s). '
            'Employés : {} à créer, {} à lier, {} conflit(s).'.format(
                invoice_ids.count(),
                len(payeurs_a_creer), len(payeurs_a_lier), len(conflits_payeur),
                len(employes_a_creer), len(employes_a_lier), len(conflits_employe),
            )
        )

        for company, user in conflits_payeur[:5]:
            self.stdout.write(self.style.WARNING(
                f'Conflit payeur : {company.compte} correspond déjà au compte {user.username} ({user.role}).'
            ))
        for line, user in conflits_employe[:5]:
            self.stdout.write(self.style.WARNING(
                f'Conflit employé : {line.msisdn} correspond déjà au compte {user.username} ({user.role}).'
            ))

        if not options['confirm']:
            self.stdout.write(self.style.WARNING(
                'Simulation uniquement : aucune donnée n’a été modifiée. Ajoutez --confirm et --temporary-password.'
            ))
            return

        password = options['temporary_password']
        created_payeurs = created_employes = linked_payeurs = linked_employes = 0

        with transaction.atomic():
            if options['only'] != 'EMPLOYES':
                for company in payeurs_a_creer:
                    first_name, last_name = _nom_utilisateur(company.raison_sociale, 'Payeur')
                    payeur = User.objects.create_user(
                        username=company.compte,
                        password=password,
                        role='PAYEUR',
                        status='ACTIF',
                        est_actif=True,
                        first_name=first_name,
                        last_name=last_name,
                    )
                    company.payeur = payeur
                    company.save(update_fields=['payeur', 'date_modification'])
                    created_payeurs += 1
                for company, payeur in payeurs_a_lier:
                    company.payeur = payeur
                    company.save(update_fields=['payeur', 'date_modification'])
                    linked_payeurs += 1

            if options['only'] != 'PAYEURS':
                for line in employes_a_creer:
                    first_name, last_name = _nom_utilisateur(line.utilisateur, 'Employé')
                    employe = User.objects.create_user(
                        username=line.msisdn,
                        password=password,
                        role='EMPLOYE',
                        status='ACTIF',
                        est_actif=True,
                        telephone=_telephone(line.msisdn),
                        first_name=first_name,
                        last_name=last_name,
                    )
                    line.employe = employe
                    line.save(update_fields=['employe', 'date_modification'])
                    created_employes += 1
                for line, employe in employes_a_lier:
                    line.employe = employe
                    line.save(update_fields=['employe', 'date_modification'])
                    linked_employes += 1

        self.stdout.write(self.style.SUCCESS(
            'Synchronisation terminée : '
            f'{created_payeurs} payeur(s) créé(s), {linked_payeurs} payeur(s) lié(s), '
            f'{created_employes} employé(s) créé(s), {linked_employes} employé(s) lié(s). '
            'Les conflits signalés n’ont pas été modifiés.'
        ))
        self.stdout.write(
            'Connexion : un payeur utilise le numéro de compte du contrat ; un employé utilise son MSISDN. '
            'Le mot de passe temporaire fourni doit être modifié avant toute utilisation réelle.'
        )
