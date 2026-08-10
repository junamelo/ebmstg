"""Outils TOTP compatibles avec Google Authenticator."""
import base64
import hashlib
import io
import time

import pyotp
import qrcode
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


def _fernet():
    """Dérive une clé Fernet stable depuis DJANGO_SECRET_KEY."""
    key = hashlib.sha256(settings.SECRET_KEY.encode('utf-8')).digest()
    return Fernet(base64.urlsafe_b64encode(key))


def encrypt_secret(secret):
    return _fernet().encrypt(secret.encode('utf-8')).decode('utf-8')


def decrypt_secret(encrypted_secret):
    if not encrypted_secret:
        return ''
    try:
        return _fernet().decrypt(encrypted_secret.encode('utf-8')).decode('utf-8')
    except InvalidToken:
        return ''


def provisioning_uri(secret, user):
    account_name = user.email or user.username
    return pyotp.TOTP(secret).provisioning_uri(name=account_name, issuer_name='Moov Africa e-Billing')


def qr_code_data_uri(uri):
    image = qrcode.make(uri)
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    encoded = base64.b64encode(buffer.getvalue()).decode('ascii')
    return f'data:image/png;base64,{encoded}'


def verify_code(encrypted_secret, code):
    secret = decrypt_secret(encrypted_secret)
    clean_code = ''.join(char for char in str(code or '') if char.isdigit())
    # Codes TOTP de 30 secondes : UTC+1 appliqué au calcul de vérification,
    # avec une tolérance de ±20 intervalles, soit ±10 minutes.
    server_time = time.time() + settings.TOTP_TIME_OFFSET_SECONDS
    return bool(secret and len(clean_code) == 6 and pyotp.TOTP(secret).verify(clean_code, for_time=server_time, valid_window=20))
