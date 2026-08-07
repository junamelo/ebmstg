"""
Script pour vérifier le mode du compte Vonage
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
print("🔍 VÉRIFICATION DU COMPTE VONAGE")
print("="*70)

api_key = settings.VONAGE_API_KEY
api_secret = settings.VONAGE_API_SECRET

print("\n📋 Informations du compte :")
print(f"   API Key : {api_key}")

# 1. Vérifier le solde
print("\n💰 SOLDE DU COMPTE")
print("-" * 70)
try:
    url = f'https://rest.nexmo.com/account/get-balance?api_key={api_key}&api_secret={api_secret}'
    request = urllib.request.Request(url)
    
    with urllib.request.urlopen(request, timeout=10) as response:
        balance_data = json.loads(response.read().decode('utf-8'))
        balance = float(balance_data.get('value', 0))
        auto_reload = balance_data.get('autoReload', False)
        
        print(f"   Solde actuel : {balance:.2f} EUR")
        print(f"   Auto-reload : {'Activé' if auto_reload else 'Désactivé'}")
        
except Exception as e:
    print(f"   ❌ Erreur : {str(e)}")

# 2. Vérifier les paramètres du compte
print("\n⚙️  PARAMÈTRES DU COMPTE")
print("-" * 70)
try:
    url = f'https://rest.nexmo.com/account/settings?api_key={api_key}&api_secret={api_secret}'
    request = urllib.request.Request(url)
    
    with urllib.request.urlopen(request, timeout=10) as response:
        settings_data = json.loads(response.read().decode('utf-8'))
        
        print(json.dumps(settings_data, indent=2))
        
except Exception as e:
    print(f"   ❌ Erreur : {str(e)}")
    print("   Note : Cet endpoint peut ne pas être disponible pour tous les comptes")

# 3. Informations importantes
print("\n" + "="*70)
print("🚨 PROBLÈME IDENTIFIÉ")
print("="*70)

print("""
Vos SMS sont marqués avec : [FREE SMS DEMO, TEST MESSAGE]
Status : rejected
Prix : $ 0

Cela signifie que votre compte Vonage est en MODE DÉMO.

En mode démo :
   ✅ Les SMS sont acceptés (status 0)
   ❌ Mais ne sont JAMAIS livrés (rejected)
   💰 Vous n'êtes pas facturé ($ 0)
   📝 Un message de test est ajouté au SMS

""")

print("="*70)
print("✅ SOLUTION")
print("="*70)

print("""
Pour envoyer de VRAIS SMS, vous devez :

1️⃣ ACTIVER LE MODE PRODUCTION
   - Aller sur : https://dashboard.nexmo.com
   - Menu : Settings > API Settings
   - Chercher : "Account mode" ou "API mode"
   - Passer de "Demo/Test" à "Production"

2️⃣ VÉRIFIER VOTRE COMPTE
   - Vonage peut demander une vérification d'identité
   - Menu : Settings > Account verification
   - Fournir les informations demandées :
     • Nom de l'entreprise
     • Utilisation prévue (ex: notifications de factures)
     • Numéro de téléphone
     • Éventuellement un document d'identité

3️⃣ RECHARGER LE SOLDE
   - Le mode production nécessite du crédit réel
   - Menu : Billing > Add credit
   - Minimum recommandé : 5 EUR (≈ 10 SMS vers le Togo)

4️⃣ VÉRIFIER LES RESTRICTIONS
   - Menu : Settings > Restrictions
   - S'assurer que le Togo (TG) est autorisé
   - Vérifier que les SMS sortants sont activés

5️⃣ RELANCER UN TEST
   - Après activation, relancer :
     python Back/test_sms_final.py
   - Le SMS devrait maintenant être livré sans "[FREE SMS DEMO]"

""")

print("="*70)
print("📞 SUPPORT VONAGE")
print("="*70)

print("""
Si vous avez des difficultés à activer le mode production :

   🌐 Dashboard : https://dashboard.nexmo.com
   💬 Support : https://api.support.vonage.com
   📧 Email : support@vonage.com

Questions à poser au support :
   "Comment activer le mode production pour mon compte ?"
   "Pourquoi mes SMS sont marqués [FREE SMS DEMO, TEST MESSAGE] ?"
   "Quelles étapes pour envoyer de vrais SMS vers le Togo ?"

""")

print("="*70)
print("FIN DE LA VÉRIFICATION")
print("="*70 + "\n")
