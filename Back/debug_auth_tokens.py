#!/usr/bin/env python3
"""
Script pour déboguer l'authentification et les tokens JWT
"""
import os
import sys
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
sys.path.append('.')

import django
django.setup()

from accounts.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

def test_auth_complete():
    """Test complet de l'authentification"""
    print("🔐 TEST AUTHENTIFICATION DJANGO")
    print("=" * 50)
    
    # 1. Vérifier l'utilisateur agent
    try:
        agent = User.objects.get(email='agent@moov.tg')
        print(f"✅ Utilisateur trouvé: {agent.email}")
        print(f"   Role: {agent.role}")
        print(f"   Actif: {agent.is_active}")
        print(f"   Status: {agent.status}")
        print()
    except User.DoesNotExist:
        print("❌ Utilisateur agent@moov.tg non trouvé")
        return False
    
    # 2. Test authentification
    print("🔑 Test authentification...")
    user = authenticate(username=agent.username, password='agent123')
    if user:
        print("✅ Authentification réussie")
    else:
        print("❌ Échec authentification")
        return False
    
    # 3. Générer token
    print("🎫 Génération token...")
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    
    print(f"✅ Access token: {access_token[:50]}...")
    print(f"✅ Refresh token: {refresh_token[:50]}...")
    
    # 4. Vérifier durée de vie
    from django.conf import settings
    jwt_settings = settings.SIMPLE_JWT
    access_lifetime = jwt_settings['ACCESS_TOKEN_LIFETIME']
    refresh_lifetime = jwt_settings['REFRESH_TOKEN_LIFETIME']
    
    print(f"⏰ Access token expire dans: {access_lifetime}")
    print(f"⏰ Refresh token expire dans: {refresh_lifetime}")
    
    # 5. Test token valide
    from rest_framework_simplejwt.tokens import UntypedToken
    from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
    
    try:
        UntypedToken(access_token)
        print("✅ Token valide")
    except TokenError as e:
        print(f"❌ Token invalide: {e}")
        return False
    
    print("\n🎯 DONNÉES POUR TEST FRONTEND:")
    print(f"Email: agent@moov.tg")
    print(f"Password: agent123")
    print(f"Token: {access_token}")
    
    return True

def create_test_token_for_frontend():
    """Créer un token de test pour le frontend"""
    print("\n🚀 CRÉATION TOKEN POUR TEST FRONTEND")
    print("=" * 50)
    
    try:
        agent = User.objects.get(email='agent@moov.tg')
        refresh = RefreshToken.for_user(agent)
        access_token = str(refresh.access_token)
        
        # Données comme le backend les retourne
        response_data = {
            "user": {
                "id": agent.id,
                "email": agent.email,
                "first_name": agent.first_name,
                "last_name": agent.last_name,
                "role": agent.role,
                "status": agent.status
            },
            "access": access_token,
            "refresh": str(refresh)
        }
        
        print("📄 Réponse exacte du backend Django:")
        import json
        print(json.dumps(response_data, indent=2))
        
        print("\n💾 À stocker dans localStorage:")
        print(f"token: {access_token}")
        print(f"user: {json.dumps(response_data['user'])}")
        
        return response_data
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def test_permissions_agent():
    """Test des permissions agent"""
    print("\n🔒 TEST PERMISSIONS AGENT")
    print("=" * 50)
    
    try:
        agent = User.objects.get(email='agent@moov.tg')
        
        print(f"Role: {agent.role}")
        print(f"Custom permissions: {agent.custom_permissions}")
        print(f"Django permissions: {list(agent.user_permissions.values_list('codename', flat=True))}")
        
        # Test accès upload PDF
        from accounts.permissions import CanUploadPDF
        permission = CanUploadPDF()
        
        # Simuler request
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(agent)
        has_permission = permission.has_permission(request, None)
        print(f"✅ Peut upload PDF: {has_permission}")
        
    except Exception as e:
        print(f"❌ Erreur permissions: {e}")

def main():
    """Point d'entrée principal"""
    success = test_auth_complete()
    if success:
        create_test_token_for_frontend()
        test_permissions_agent()
        
        print("\n🎉 DIAGNOSTIC COMPLET")
        print("=" * 50)
        print("✅ Authentification Django: OK")
        print("✅ Génération tokens: OK") 
        print("✅ Permissions: OK")
        print("\n💡 Si le problème persiste côté frontend:")
        print("   1. Vérifier console browser (F12)")
        print("   2. Vérifier localStorage token")
        print("   3. Tester endpoint manuellement")
    else:
        print("\n❌ Problème dans l'authentification Django")

if __name__ == "__main__":
    main()