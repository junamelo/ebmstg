"""Envoi de notifications de disponibilité de facture (SMTP et Vonage)."""
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from billing.models import NotificationFacture


def _enregistrer(invoice, canal, destinataire, statut, detail=''):
    return NotificationFacture.objects.create(
        invoice=invoice, canal=canal, destinataire=destinataire or '-', statut=statut, detail=detail
    )


def notifier_facture(invoice, canaux):
    """Envoie les canaux demandés et retourne un bilan traçable."""
    user = invoice.line.employe if invoice.line_id and invoice.line and invoice.line.employe else invoice.company.payeur
    email = (getattr(user, 'email', '') or invoice.company.email_facturation).strip()
    telephone = (getattr(user, 'telephone', '') or '').strip()
    numero = invoice.numero_facture_pdf or invoice.numero_facture
    message = f"Votre facture {numero} est disponible dans votre portail Moov Africa."
    resultats = []

    if 'EMAIL' in canaux:
        if not email:
            resultats.append(_enregistrer(invoice, 'EMAIL', '', 'ECHEC', 'Aucune adresse e-mail pour le destinataire'))
        elif not getattr(settings, 'EMAIL_HOST', '') or not getattr(settings, 'DEFAULT_FROM_EMAIL', ''):
            resultats.append(_enregistrer(invoice, 'EMAIL', email, 'NON_CONFIGUREE', 'SMTP non configuré'))
        else:
            try:
                mail = EmailMultiAlternatives('Votre facture Moov Africa est disponible', message, settings.DEFAULT_FROM_EMAIL, [email])
                mail.send(fail_silently=False)
                resultats.append(_enregistrer(invoice, 'EMAIL', email, 'ENVOYEE'))
            except Exception as exc:
                resultats.append(_enregistrer(invoice, 'EMAIL', email, 'ECHEC', str(exc)))

    if 'SMS' in canaux:
        api_key = getattr(settings, 'VONAGE_API_KEY', '')
        api_secret = getattr(settings, 'VONAGE_API_SECRET', '')
        sender = getattr(settings, 'VONAGE_SMS_FROM', '')
        if not telephone:
            resultats.append(_enregistrer(invoice, 'SMS', '', 'ECHEC', 'Aucun numéro de téléphone pour le destinataire'))
        elif not all([api_key, api_secret, sender]):
            resultats.append(_enregistrer(invoice, 'SMS', telephone, 'NON_CONFIGUREE', 'Vonage non configuré'))
        else:
            try:
                data = urllib.parse.urlencode({
                    'api_key': api_key, 'api_secret': api_secret,
                    'to': telephone, 'from': sender, 'text': message,
                }).encode()
                request = urllib.request.Request(
                    'https://rest.nexmo.com/sms/json', data=data, method='POST'
                )
                with urllib.request.urlopen(request, timeout=15) as response:
                    body = response.read().decode('utf-8')
                if '"status":"0"' not in body and '"status": "0"' not in body:
                    raise RuntimeError('Vonage a refusé le SMS')
                resultats.append(_enregistrer(invoice, 'SMS', telephone, 'ENVOYEE'))
            except Exception as exc:
                resultats.append(_enregistrer(invoice, 'SMS', telephone, 'ECHEC', str(exc)))

    return resultats
