"""
Script de test pour les nouveaux modèles
Exécuter après avoir démarré le serveur Django
"""

import requests
import json
from datetime import date, timedelta

BASE_URL = "http://localhost:8000/api"

def test_login():
    """Test de connexion"""
    print("🔐 Test de connexion...")
    response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={"email": "admin@moov.tg", "password": "admin123"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Connexion réussie")
        return data['access']
    else:
        print(f"❌ Échec de connexion: {response.status_code}")
        return None

def test_create_package(token):
    """Test de création de forfait"""
    print("\n📦 Test de création de forfait...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/billing/packages/",
        headers=headers,
        json={
            "nom": "Formule Moon 2",
            "code": "MOON2",
            "type_forfait": "MIXTE",
            "prix_mensuel": 15000.00,
            "quota_data_mo": 2000,
            "quota_minutes": 100,
            "quota_sms": 50,
            "description": "Forfait mixte complet",
            "est_actif": True
        }
    )
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Forfait créé - ID: {data['id']}")
        return data['id']
    else:
        print(f"❌ Échec création forfait: {response.status_code}")
        print(response.text)
        return None

def test_create_service(token):
    """Test de création de service"""
    print("\n🔧 Test de création de service...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/billing/services/",
        headers=headers,
        json={
            "nom": "International",
            "code": "INT",
            "type_service": "PASS",
            "description": "Pass appels internationaux",
            "est_actif": True
        }
    )
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Service créé - ID: {data['id']}")
        return data['id']
    else:
        print(f"❌ Échec création service: {response.status_code}")
        print(response.text)
        return None

def test_create_tarif_service(token, service_id):
    """Test de création de tarif pour un service"""
    print("\n💰 Test de création de tarif service...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/billing/tarifs-services/",
        headers=headers,
        json={
            "service": service_id,
            "nom_option": "Pass 48h",
            "prix": 2000.00,
            "duree_validite_heures": 48,
            "description": "Accès illimité pendant 48h",
            "est_actif": True
        }
    )
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Tarif créé - ID: {data['id']}")
        return data['id']
    else:
        print(f"❌ Échec création tarif: {response.status_code}")
        print(response.text)
        return None

def test_list_packages(token):
    """Test de récupération des forfaits"""
    print("\n📋 Test de récupération des forfaits...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/billing/packages/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {len(data)} forfait(s) récupéré(s)")
        for package in data:
            print(f"   - {package['nom']} ({package['code']}) - {package['prix_mensuel']} FCFA")
    else:
        print(f"❌ Échec récupération forfaits: {response.status_code}")

def test_list_services(token):
    """Test de récupération des services"""
    print("\n📋 Test de récupération des services...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/billing/services/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {len(data)} service(s) récupéré(s)")
        for service in data:
            print(f"   - {service['nom']} ({service['code']}) - {service['nombre_tarifs']} tarif(s)")
    else:
        print(f"❌ Échec récupération services: {response.status_code}")

def test_toggle_package(token, package_id):
    """Test d'activation/désactivation de forfait"""
    print("\n🔄 Test toggle forfait...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.patch(
        f"{BASE_URL}/billing/packages/{package_id}/toggle_actif/",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Forfait {'activé' if data['est_actif'] else 'désactivé'}")
    else:
        print(f"❌ Échec toggle: {response.status_code}")

def test_create_simulation(token):
    """Test de création de simulation"""
    print("\n🧮 Test de création de simulation...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/billing/simulations/",
        headers=headers,
        json={
            "montant_estime": 25000.00,
            "services_selectionnes": [
                {"nom": "International", "prix": 2000},
                {"nom": "Data Boost", "prix": 3000}
            ],
            "resultat_detaille": {
                "forfait_base": 15000,
                "services": 5000,
                "total": 25000
            }
        }
    )
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Simulation créée - ID: {data['id']}")
        print(f"   Montant estimé: {data['montant_estime']} FCFA")
        return data['id']
    else:
        print(f"❌ Échec création simulation: {response.status_code}")
        print(response.text)
        return None

def test_list_simulations(token):
    """Test de récupération des simulations"""
    print("\n📋 Test de récupération des simulations...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/billing/simulations/mes_simulations/",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {len(data)} simulation(s) récupérée(s)")
        for sim in data:
            print(f"   - {sim['date_simulation']} - {sim['montant_estime']} FCFA")
    else:
        print(f"❌ Échec récupération simulations: {response.status_code}")

def test_get_service_tarifs(token, service_id):
    """Test de récupération des tarifs d'un service"""
    print("\n💰 Test de récupération des tarifs d'un service...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/billing/services/{service_id}/tarifs/",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {len(data)} tarif(s) récupéré(s)")
        for tarif in data:
            print(f"   - {tarif['nom_option']} - {tarif['prix']} FCFA")
    else:
        print(f"❌ Échec récupération tarifs: {response.status_code}")

def cleanup(token, package_id, service_id):
    """Nettoyage des données de test"""
    print("\n🧹 Nettoyage des données de test...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Supprimer le forfait
    if package_id:
        response = requests.delete(
            f"{BASE_URL}/billing/packages/{package_id}/",
            headers=headers
        )
        if response.status_code == 204:
            print("✅ Forfait supprimé")
    
    # Supprimer le service (cascade supprime les tarifs)
    if service_id:
        response = requests.delete(
            f"{BASE_URL}/billing/services/{service_id}/",
            headers=headers
        )
        if response.status_code == 204:
            print("✅ Service supprimé")

def main():
    """Fonction principale de test"""
    print("=" * 60)
    print("🧪 TESTS DES NOUVEAUX MODÈLES")
    print("=" * 60)
    
    # 1. Connexion
    token = test_login()
    if not token:
        print("\n❌ Impossible de continuer sans token")
        return
    
    # 2. Créer un forfait
    package_id = test_create_package(token)
    
    # 3. Créer un service
    service_id = test_create_service(token)
    
    # 4. Créer un tarif pour le service
    if service_id:
        tarif_id = test_create_tarif_service(token, service_id)
    
    # 5. Lister les forfaits
    test_list_packages(token)
    
    # 6. Lister les services
    test_list_services(token)
    
    # 7. Toggle un forfait
    if package_id:
        test_toggle_package(token, package_id)
    
    # 8. Récupérer les tarifs d'un service
    if service_id:
        test_get_service_tarifs(token, service_id)
    
    # 9. Créer une simulation
    test_create_simulation(token)
    
    # 10. Lister les simulations
    test_list_simulations(token)
    
    # 11. Nettoyage
    cleanup(token, package_id, service_id)
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Erreur: Impossible de se connecter au serveur")
        print("   Assurez-vous que le serveur Django est démarré:")
        print("   python manage.py runserver")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
