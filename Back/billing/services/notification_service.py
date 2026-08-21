"""Envoi des notifications de disponibilité de facture (SMTP et MySMSGate)."""

import json
import re
import urllib.error
import urllib.request

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from billing.models import NotificationFacture


def _enregistrer(invoice, canal, destinataire, statut, detail=''):
    return NotificationFacture.objects.create(
        invoice=invoice,
        canal=canal,
        destinataire=destinataire or '-',
        statut=statut,
        detail=detail,
    )


def _normaliser_numero_sms(numero):
    """Convertit un numéro local togolais en format E.164 attendu par MySMSGate."""
    valeur = str(numero or '').strip()
    if not valeur:
        return ''

    international = valeur.startswith('+') or valeur.startswith('00')
    chiffres = re.sub(r'\D', '', valeur)
    if valeur.startswith('00'):
        chiffres = chiffres[2:]

    indicatif = re.sub(
        r'\D',
        '',
        str(getattr(settings, 'SMS_DEFAULT_COUNTRY_CODE', '228') or '228'),
    )

    if len(chiffres) == 8 and not international:
        chiffres = f'{indicatif}{chiffres}'
    elif not international and indicatif and chiffres.startswith(indicatif):
        pass
    elif not international:
        raise ValueError('Le numéro SMS doit contenir 8 chiffres ou être au format international')

    if not chiffres:
        raise ValueError('Numéro SMS invalide')
    return f'+{chiffres}'


def _envoyer_sms_mysmsgate(destinataire, message):
    api_url = getattr(settings, 'MYSMSGATE_API_URL', 'https://mysmsgate.net/api/v1/send')
    api_key = getattr(settings, 'MYSMSGATE_API_KEY', '')
    device_id = getattr(settings, 'MYSMSGATE_DEVICE_ID', '')
    slot = getattr(settings, 'MYSMSGATE_SIM_SLOT', '')
    timeout = getattr(settings, 'MYSMSGATE_TIMEOUT', 15)

    if not api_key:
        raise LookupError('MySMSGate non configuré')

    payload = {
        'to': _normaliser_numero_sms(destinataire),
        'message': message,
    }
    if device_id:
        payload['device_id'] = device_id
    if str(slot).strip() != '':
        slot_int = int(slot)
        if slot_int not in (0, 1):
            raise ValueError('MYSMSGATE_SIM_SLOT doit valoir 0 ou 1')
        payload['slot'] = slot_int

    request = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        method='POST',
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            http_status = response.getcode()
            body = response.read().decode('utf-8')
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode('utf-8', errors='replace')[:500]
        raise RuntimeError(f'MySMSGate HTTP {exc.code}: {detail}') from exc

    try:
        resultat = json.loads(body or '{}')
    except json.JSONDecodeError as exc:
        raise RuntimeError('Réponse JSON invalide reçue de MySMSGate') from exc

    if http_status not in (200, 201, 202) or not resultat.get('success'):
        erreur = resultat.get('error') or resultat.get('message') or 'requête refusée'
        raise RuntimeError(f'MySMSGate a refusé le SMS : {erreur}')

    return resultat


def notifier_facture(invoice, canaux):
    """Envoie les canaux demandés et retourne un bilan traçable en base."""
    ligne = invoice.line if invoice.line_id else None
    user = ligne.employe if ligne and ligne.employe else invoice.company.payeur
    email = (
        getattr(user, 'email', '')
        or invoice.company.email_facturation
        or ''
    ).strip()
    telephone = (getattr(user, 'telephone', '') or (ligne.msisdn if ligne else '') or '').strip()
    numero = invoice.numero_facture_pdf or invoice.numero_facture
    message = f'Votre facture {numero} est disponible dans votre portail Moov Africa.'
    canaux = {str(canal).upper() for canal in (canaux or [])}
    resultats = []

    if 'EMAIL' in canaux:
        if not email:
            resultats.append(_enregistrer(
                invoice, 'EMAIL', '', 'ECHEC', 'Aucune adresse e-mail pour le destinataire'
            ))
        elif not getattr(settings, 'EMAIL_HOST', '') or not getattr(settings, 'DEFAULT_FROM_EMAIL', ''):
            resultats.append(_enregistrer(
                invoice, 'EMAIL', email, 'NON_CONFIGUREE', 'SMTP non configuré'
            ))
        else:
            try:
                mail = EmailMultiAlternatives(
                    'Votre facture Moov Africa est disponible',
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                )
                mail.send(fail_silently=False)
                resultats.append(_enregistrer(invoice, 'EMAIL', email, 'ENVOYEE'))
            except Exception as exc:
                resultats.append(_enregistrer(invoice, 'EMAIL', email, 'ECHEC', str(exc)))

    if 'SMS' in canaux:
        if not telephone:
            resultats.append(_enregistrer(
                invoice, 'SMS', '', 'ECHEC', 'Aucun numéro de téléphone pour le destinataire'
            ))
        elif not getattr(settings, 'MYSMSGATE_API_KEY', ''):
            resultats.append(_enregistrer(
                invoice, 'SMS', telephone, 'NON_CONFIGUREE', 'MySMSGate non configuré'
            ))
        else:
            try:
                telephone_international = _normaliser_numero_sms(telephone)
                resultat = _envoyer_sms_mysmsgate(telephone_international, message)
                statut_fournisseur = str(resultat.get('status', 'pending')).lower()
                statut = (
                    NotificationFacture.Statut.ENVOYEE
                    if statut_fournisseur in {'sent', 'delivered'}
                    else NotificationFacture.Statut.EN_ATTENTE
                )
                sms_id = resultat.get('sms_id', '')
                detail = f'MySMSGate: sms_id={sms_id}, statut={statut_fournisseur}'
                resultats.append(_enregistrer(
                    invoice, 'SMS', telephone_international, statut, detail
                ))
            except Exception as exc:
                resultats.append(_enregistrer(invoice, 'SMS', telephone, 'ECHEC', str(exc)))

    return resultats
