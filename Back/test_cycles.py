"""
Script de test pour vérifier les cycles de facturation
Exécuter après avoir démarré le serveur Django
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_login():
    """Test de connexion pour obtenir un token"""
    print("🔐 Test de connexion...")
    response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={
            "email": "admin@moov.tg",
            "password": "admin123"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Connexion réussie - Token obtenu")
        return data['access']
    else:
        print(f"❌ Échec de connexion: {response.status_code}")
        print(response.text)
        return None

def test_create_company(token):
    """Test de création d'entreprise"""
    print("\n🏢 Test de création d'entreprise...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/billing/companies/",
        headers=headers,
        json={
            "compte": "CT-TEST-001",
            "raison_sociale": "Entreprise Test Cycles",
            "code_commercial": "7000",
            "categorie": "PE",
            "statut": "ACTIF"
        }
    )
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Entreprise créée - ID: {data['id']}")
        return data['id']
    else:
        print(f"❌ Échec création entreprise: {response.status_code}")
        print(response.text)
        return None

def test_create_line_hyb(token, company_id):
    """Test de création de ligne avec cycle HYB"""
    print("\n📱 Test de création de ligne avec cycle HYB...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/billing/lines/",
        headers=headers,
        json={
            "company": company_id,
            "msisdn": "79123456",
            "utilisateur": "Test User HYB",
            "forfait": 15000.00,
            "cycle": "HYB",
            "statut": "ACTIF"
        }
    )
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Ligne HYB créée - MSISDN: {data['msisdn']}, Cycle: {data['cycle']}")
        return data['id']
    else:
        print(f"❌ Échec création ligne HYB: {response.status_code}")
        print(response.text)
        return None

def test_create_line_op(token, company_id):
    """Test de création de ligne avec cycle OP"""
    print("\n📱 Test de création de ligne avec cycle OP...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/billing/lines/",
        headers=headers,
        json={
            "company": company_id,
            "msisdn": "79654321",
            "utilisateur": "Test User OP",
            "forfait": 20000.00,
            "cycle": "OP",
            "statut": "ACTIF"
        }
    )
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Ligne OP créée - MSISDN: {data['msisdn']}, Cycle: {data['cycle']}")
        return data['id']
    else:
        print(f"❌ Échec création ligne OP: {response.status_code}")
        print(response.text)
        return None

def test_get_lines(token):
    """Test de récupération des lignes"""
    print("\n📋 Test de récupération des lignes...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/billing/lines/",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {len(data)} ligne(s) récupérée(s)")
        for line in data:
            print(f"   - MSISDN: {line['msisdn']}, Cycle: {line['cycle']}, Utilisateur: {line['utilisateur']}")
    else:
        print(f"❌ Échec récupération lignes: {response.status_code}")
        print(response.text)

def test_update_cycle(token, line_id, new_cycle):
    """Test de modification du cycle d'une ligne"""
    print(f"\n🔄 Test de modification du cycle vers {new_cycle}...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.patch(
        f"{BASE_URL}/billing/lines/{line_id}/",
        headers=headers,
        json={"cycle": new_cycle}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Cycle modifié - Nouveau cycle: {data['cycle']}")
    else:
        print(f"❌ Échec modification cycle: {response.status_code}")
        print(response.text)

def test_invalid_cycle(token, company_id):
    """Test de création avec un cycle invalide"""
    print("\n⚠️ Test de création avec cycle invalide (MON1)...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/billing/lines/",
        headers=headers,
        json={
            "company": company_id,
            "msisdn": "79999999",
            "utilisateur": "Test Invalid",
            "forfait": 10000.00,
            "cycle": "MON1",  # Ancien cycle, devrait échouer
            "statut": "ACTIF"
        }
    )
    
    if response.status_code != 201:
        print(f"✅ Validation correcte - Cycle invalide rejeté")
        print(f"   Message: {response.json()}")
    else:
        print(f"❌ Erreur: cycle invalide accepté !")

def cleanup(token, company_id):
    """Nettoyage des données de test"""
    print("\n🧹 Nettoyage des données de test...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Supprimer l'entreprise (cascade supprime les lignes)
    response = requests.delete(
        f"{BASE_URL}/billing/companies/{company_id}/",
        headers=headers
    )
    
    if response.status_code == 204:
        print("✅ Données de test supprimées")
    else:
        print(f"⚠️ Nettoyage partiel: {response.status_code}")

def main():
    """Fonction principale de test"""
    print("=" * 60)
    print("🧪 TESTS DES CYCLES DE FACTURATION HYB/OP")
    print("=" * 60)
    
    # 1. Connexion
    token = test_login()
    if not token:
        print("\n❌ Impossible de continuer sans token")
        return
    
    # 2. Créer une entreprise de test
    company_id = test_create_company(token)
    if not company_id:
        print("\n❌ Impossible de continuer sans entreprise")
        return
    
    # 3. Créer ligne avec cycle HYB
    line_hyb_id = test_create_line_hyb(token, company_id)
    
    # 4. Créer ligne avec cycle OP
    line_op_id = test_create_line_op(token, company_id)
    
    # 5. Récupérer toutes les lignes
    test_get_lines(token)
    
    # 6. Modifier le cycle d'une ligne
    if line_hyb_id:
        test_update_cycle(token, line_hyb_id, "OP")
    
    # 7. Tester un cycle invalide
    test_invalid_cycle(token, company_id)
    
    # 8. Nettoyage
    cleanup(token, company_id)
    
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
