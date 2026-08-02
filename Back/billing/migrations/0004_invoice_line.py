from django.db import migrations, models
import django.db.models.deletion


def link_existing_individual_invoices(apps, schema_editor):
    """Relie les factures déjà créées à leur ligne si le MSISDN est dans le numéro."""
    Invoice = apps.get_model('billing', 'Invoice')
    Line = apps.get_model('billing', 'Line')

    for invoice in Invoice.objects.filter(line__isnull=True).select_related('company'):
        line = Line.objects.filter(company_id=invoice.company_id).filter(
            msisdn__in=[
                value for value in Line.objects.filter(company_id=invoice.company_id)
                .values_list('msisdn', flat=True)
                if value in invoice.numero_facture
            ]
        ).first()
        if line:
            invoice.line_id = line.id
            invoice.save(update_fields=['line'])


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0003_package_service_invoice_historiquefacturation_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='line',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='invoices',
                to='billing.line',
                verbose_name='Ligne concernée',
            ),
        ),
        migrations.RunPython(link_existing_individual_invoices, migrations.RunPython.noop),
    ]
