"""
Script de test pour les endpoints de statistiques
Phase 5 : Dashboards & Stats
"""
import os, sys, django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()

from django.test import Client
from accounts.models import User
from rest_framework_simplejwt.tokens import RefreshToken

def get_jwt_token(user):
    """Générer un token JWT pour l'utilisateur"""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

def test_stats_endpoints():
    """Tester tous les endpoints de stats"""
    
    client = Client()
    
    print("🧪 TEST DES ENDPOINTS DE STATISTIQUES\n")
    print("="*70)
    
    # Récupérer ou créer les utilisateurs de test
    users = {
        'admin': User.objects.filter(role='ADMIN').first(),
        'chef': User.objects.filter(role='CHEF_FACTURATION').first(),
        'agent': User.objects.filter(role='AGENT_FACTURATION').first(),
        'payeur': User.objects.filter(role='PAYEUR').first(),
        'employe': User.objects.filter(role='EMPLOYE').first(),
    }
    
    # Endpoints à tester
    endpoints = {
        'admin': '/api/billing/stats/admin/',
        'chef': '/api/billing/stats/chef/',
        'agent': '/api/billing/stats/agent/',
        'payeur': '/api/billing/stats/payeur/',
        'employe': '/api/billing/stats/employe/',
    }
    
    results = []
    
    for role, endpoint in endpoints.items():
        user = users.get(role)
        
        if not user:
            print(f"⚠️  {role.upper():15} - Utilisateur non trouvé")
            results.append({'role': role, 'status': 'SKIP', 'reason': 'User not found'})
            continue
        
        # Générer le token JWT
        try:
            token = get_jwt_token(user)
        except Exception as e:
            print(f"❌ {role.upper():15} - Erreur génération token: {e}")
            results.append({'role': role, 'status': 'TOKEN_ERROR', 'error': str(e)})
            continue
        
        # Appeler l'endpoint
        try:
            response = client.get(
                endpoint,
                HTTP_AUTHORIZATION=f'Bearer {token}'
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {role.upper():15} - {endpoint:35} - {response.status_code}")
                
                # Afficher quelques stats clés
                if 'statistiques_globales' in data:
                    print(f"   📊 Total entreprises: {data['statistiques_globales'].get('total_entreprises', 0)}")
                elif 'statistiques' in data:
                    print(f"   📊 Total factures: {data['statistiques'].get('total_factures', 0)}")
                elif 'agents' in data:
                    print(f"   📊 Nombre agents: {len(data['agents'])}")
                
                results.append({'role': role, 'status': 'SUCCESS', 'code': response.status_code})
            else:
                print(f"❌ {role.upper():15} - {endpoint:35} - {response.status_code}")
                print(f"   Error: {response.content.decode()[:100]}")
                results.append({'role': role, 'status': 'ERROR', 'code': response.status_code})
                
        except Exception as e:
            print(f"❌ {role.upper():15} - {endpoint:35} - EXCEPTION")
            print(f"   {str(e)[:100]}")
            results.append({'role': role, 'status': 'EXCEPTION', 'error': str(e)})
        
        print()
    
    # Résumé
    print("="*70)
    print("RÉSUMÉ DES TESTS")
    print("="*70)
    
    success = sum(1 for r in results if r['status'] == 'SUCCESS')
    errors = sum(1 for r in results if r['status'] == 'ERROR')
    exceptions = sum(1 for r in results if r['status'] == 'EXCEPTION')
    skipped = sum(1 for r in results if r['status'] == 'SKIP')
    
    print(f"✅ Succès    : {success}/{len(endpoints)}")
    print(f"❌ Erreurs   : {errors}/{len(endpoints)}")
    print(f"💥 Exceptions: {exceptions}/{len(endpoints)}")
    print(f"⚠️  Ignorés   : {skipped}/{len(endpoints)}")
    print()
    
    if success == len(endpoints):
        print("🎉 TOUS LES ENDPOINTS FONCTIONNENT CORRECTEMENT !")
    elif success > 0:
        print(f"⚠️  {success}/{len(endpoints)} endpoints fonctionnent. Vérifier les erreurs ci-dessus.")
    else:
        print("❌ AUCUN ENDPOINT NE FONCTIONNE. Vérifier la configuration.")
    
    print("="*70)


if __name__ == "__main__":
    test_stats_endpoints()
