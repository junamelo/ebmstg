from decimal import Decimal

from django.core.management.base import BaseCommand

from billing.models import Service


class Command(BaseCommand):
    help = "Renomme les options No Limit avec leur tarif lisible en FCFA."

    def handle(self, *args, **options):
        services = Service.objects.filter(code__iexact='NO_LIMIT')
        if not services.exists():
            self.stdout.write(self.style.WARNING('Aucun service No Limit trouvé.'))
            return

        updated = 0
        for service in services:
            for tarif in service.tarifs.all():
                montant = Decimal(tarif.prix).quantize(Decimal('1'))
                montant_lisible = f'{montant:,.0f}'.replace(',', '\u202f')
                nouveau_nom = f'No Limit {montant_lisible} FCFA'
                if tarif.nom_option != nouveau_nom:
                    tarif.nom_option = nouveau_nom
                    tarif.save(update_fields=['nom_option', 'date_modification'])
                    updated += 1

        self.stdout.write(self.style.SUCCESS(f'{updated} option(s) No Limit renommée(s).'))
