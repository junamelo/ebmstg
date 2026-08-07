"""
Script de diagnostic pour identifier le problème d'envoi SMS
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()

from django.conf import settings
import urllib.parse
import urllib.request
import json

print("\n" + "="*70)
print("🔍 DIAGNOSTIC SMS - Vonage API")
print("="*70)

# 1. Vérifier la configuration
print("\n1️⃣ VÉRIFICATION DE LA CONFIGURATION")
print("-" * 70)

api_key = settings.VONAGE_API_KEY
api_secret = settings.VONAGE_API_SECRET
sender = settings.VONAGE_SMS_FROM

print(f"✅ VONAGE_API_KEY: {api_key}")
print(f"✅ VONAGE_API_SECRET: {'*' * len(api_secret) if api_secret else '(vide)'}")
print(f"✅ VONAGE_SMS_FROM: {sender}")

if not api_key or not api_secret or not sender:
    print("\n❌ ERREUR : Configuration incomplète !")
    print("Vérifiez votre fichier .env")
    sys.exit(1)

# 2. Vérifier le solde Vonage
print("\n2️⃣ VÉRIFICATION DU SOLDE VONAGE")
print("-" * 70)

try:
    url = f'https://rest.nexmo.com/account/get-balance?api_key={api_key}&api_secret={api_secret}'
    request = urllib.request.Request(url)
    
    with urllib.request.urlopen(request, timeout=10) as response:
        balance_data = json.loads(response.read().decode('utf-8'))
        balance = float(balance_data.get('value', 0))
        
        print(f"💰 Solde actuel : {balance:.2f} EUR")
        
        if balance < 0.05:
            print(f"⚠️  ATTENTION : Solde insuffisant pour envoyer un SMS !")
            print(f"   Minimum requis : 0.05 EUR")
            print(f"   Recharger sur : https://dashboard.nexmo.com")
        else:
            print(f"✅ Solde suffisant")
            
except Exception as e:
    print(f"❌ Impossible de vérifier le solde : {str(e)}")
    print("   Vérifiez vos identifiants API")

# 3. Test d'envoi SMS avec détails complets
print("\n3️⃣ TEST D'ENVOI SMS DÉTAILLÉ")
print("-" * 70)

# Numéro de destination
numero_dest = '22892628287'
print(f"📱 Destinataire : {numero_dest}")
print(f"📤 Expéditeur : {sender}")

# Tester plusieurs formats de numéros
formats_test = [
    ('22892628287', 'Format international sans +'),
    ('+22892628287', 'Format international avec +'),
    ('92628287', 'Format local (sans indicatif pays)'),
]

print("\n🧪 Test de différents formats de numéros...")

for numero, description in formats_test:
    print(f"\n📍 Test avec : {numero} ({description})")
    print("-" * 50)
    
    try:
        # Préparer les données
        data = urllib.parse.urlencode({
            'api_key': api_key,
            'api_secret': api_secret,
            'to': numero,
            'from': sender,
            'text': f'Test SMS Moov Africa - Format: {description}',
        }).encode()
        
        # Envoyer la requête
        request = urllib.request.Request(
            'https://rest.nexmo.com/sms/json',
            data=data,
            method='POST'
        )
        
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read().decode('utf-8')
            result = json.loads(body)
            
            print(f"📥 Réponse Vonage :")
            print(json.dumps(result, indent=2))
            
            # Analyser la réponse
            if 'messages' in result and len(result['messages']) > 0:
                message = result['messages'][0]
                status = message.get('status', 'unknown')
                
                # Codes de statut Vonage
                status_codes = {
                    '0': '✅ Message envoyé avec succès',
                    '1': '⚠️  Throttled - Trop de requêtes',
                    '2': '❌ Paramètres manquants',
                    '3': '❌ Paramètres invalides',
                    '4': '❌ Identifiants API invalides',
                    '5': '❌ Erreur interne Vonage',
                    '6': '❌ Format du message invalide',
                    '7': '❌ Numéro invalide',
                    '8': '❌ Expéditeur non autorisé',
                    '9': '❌ Quota partenaire dépassé (plus de crédit)',
                    '10': '❌ Concatenation non supportée',
                    '11': '❌ Compte pas en production',
                    '12': '❌ Erreur réseau',
                    '13': '❌ Format message invalide',
                    '14': '❌ Expéditeur invalide',
                    '15': '❌ Destinataire invalide',
                    '16': '❌ Trop long',
                    '22': '❌ Signature invalide',
                    '23': '❌ Numéro en opt-out',
                    '29': '❌ Non-whitelisted destination',
                    '33': '❌ Numéro invalide'
                }
                
                status_msg = status_codes.get(status, f'❓ Code inconnu: {status}')
                print(f"\n{status_msg}")
                
                if status == '0':
                    message_id = message.get('message-id', 'N/A')
                    remaining = message.get('remaining-balance', 'N/A')
                    price = message.get('message-price', 'N/A')
                    
                    print(f"   ID du message : {message_id}")
                    print(f"   Prix : {price} EUR")
                    print(f"   Solde restant : {remaining} EUR")
                    print(f"\n🎉 SMS ENVOYÉ ! Vérifiez le téléphone +228 92 62 82 87")
                    print(f"   Format à utiliser : {numero}")
                    break
                else:
                    error_text = message.get('error-text', 'Aucun détail')
                    print(f"   Détail erreur : {error_text}")
                    
            else:
                print("❌ Réponse Vonage inattendue")
                
    except urllib.error.HTTPError as e:
        print(f"❌ Erreur HTTP {e.code} : {e.reason}")
        try:
            error_body = e.read().decode('utf-8')
            print(f"   Détail : {error_body}")
        except:
            pass
            
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")

# 4. Recommandations
print("\n" + "="*70)
print("📋 RECOMMANDATIONS")
print("="*70)

print("""
Si le SMS ne passe toujours pas :

1️⃣ VÉRIFIER LE CRÉDIT VONAGE
   - Aller sur : https://dashboard.nexmo.com
   - Menu : Billing > Balance
   - Recharger si nécessaire (minimum 5€)

2️⃣ VÉRIFIER LE COMPTE VONAGE
   - Compte en mode "Production" ?
   - Numéros de destination autorisés ?
   - Restrictions géographiques ?

3️⃣ VÉRIFIER LE NUMÉRO EXPÉDITEUR
   - Certains pays exigent un expéditeur enregistré
   - Pour le Togo : vérifier les règles locales
   - Alternative : utiliser un numéro court si disponible

4️⃣ TESTER AVEC UN AUTRE NUMÉRO
   - Essayer avec votre propre numéro
   - Vérifier si le problème est spécifique au numéro

5️⃣ LOGS VONAGE
   - Dashboard > Reports > SMS logs
   - Voir les tentatives et erreurs détaillées

6️⃣ SUPPORT VONAGE
   - https://api.support.vonage.com
   - Demander pourquoi les SMS vers le Togo échouent
""")

print("="*70)
print("FIN DU DIAGNOSTIC")
print("="*70 + "\n")
