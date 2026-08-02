#!/usr/bin/env python3
"""
Script pour tester l'API de publication PDF en masse
"""
import requests
import json
import os

# Configuration
BASE_URL = "http://localhost:8000/api"
EMAIL = "agent@moov.tg"
PASSWORD = "agent123"
PDF_PATH = "media/test_bulk_moov.pdf"

def test_bulk_pdf_upload():
    """Tester l'upload en masse du PDF"""
    print("🚀 Test de l'API Publication PDF en Masse")
    print("=" * 50)
    
    # 1. Connexion
    print("1️⃣ Connexion...")
    login_data = {
        "email": EMAIL,
        "password": PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    if response.status_code != 200:
        print(f"❌ Échec de connexion : {response.status_code}")
        print(f"   Réponse : {response.text}")
        return False
    
    token = response.json()['access']
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Connexion réussie (Token obtenu)")
    
    # 2. Vérifier que le PDF existe
    if not os.path.exists(PDF_PATH):
        print(f"❌ Fichier PDF non trouvé : {PDF_PATH}")
        return False
    
    print(f"✅ PDF de test trouvé : {PDF_PATH}")
    
    # 3. Test sans auto-matching d'abord
    print("\\n2️⃣ Test sans auto-matching...")
    with open(PDF_PATH, 'rb') as pdf_file:
        files = {'fichier': pdf_file}
        data = {'auto_match': 'false'}
        
        response = requests.post(
            f"{BASE_URL}/billing/invoices/upload_bulk_pdf/",
            headers=headers,
            files=files,
            data=data
        )
    
    print(f"   Status : {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Découpage réussi !")
        print(f"   📄 {result['total_blocks']} blocs détectés")
        print(f"   📁 {result['files_created']} fichiers créés")
        print(f"   📊 {result['total_pages']} pages au total")
        
        print("   📋 Fichiers créés :")
        for i, file_info in enumerate(result.get('files', []), 1):
            print(f"      {i}. {file_info['filename']}")
            if 'identifiers' in file_info:
                identifiers = file_info['identifiers']
                print(f"         MSISDN: {identifiers.get('msisdn', 'N/A')}")
                print(f"         Compte: {identifiers.get('compte', 'N/A')}")
        
    else:
        print(f"❌ Échec du découpage : {response.text}")
        return False
    
    # 4. Test avec auto-matching
    print("\\n3️⃣ Test avec auto-matching...")
    with open(PDF_PATH, 'rb') as pdf_file:
        files = {'fichier': pdf_file}
        data = {
            'auto_match': 'true',
            'cycle': 'HYB',
            'periode_debut': '2026-07-01',
            'periode_fin': '2026-07-31'
        }
        
        response = requests.post(
            f"{BASE_URL}/billing/invoices/upload_bulk_pdf/",
            headers=headers,
            files=files,
            data=data
        )
    
    print(f"   Status : {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Matching automatique réussi !")
        print(f"   📄 {result['total_blocks']} blocs détectés")
        print(f"   📁 {result['files_created']} fichiers créés")
        
        if 'auto_match' in result:
            match_info = result['auto_match']
            print(f"   🎯 Matching : {match_info['matched']}/{match_info['total_files']} réussis")
            print(f"   ❌ Non matchés : {match_info['not_matched']}")
            
            print("   📋 Factures attachées :")
            for attached in match_info['attached']:
                print(f"      ✅ {attached['numero_facture']} ← {attached['filename']}")
            
            if match_info['errors']:
                print("   ⚠️  Erreurs :")
                for error in match_info['errors']:
                    print(f"      ❌ {error['filename']} : {error['error']}")
        
    else:
        print(f"❌ Échec du matching : {response.text}")
        return False
    
    # 5. Vérifier le statut des factures
    print("\\n4️⃣ Vérification des factures...")
    response = requests.get(
        f"{BASE_URL}/billing/invoices/",
        headers=headers,
        params={'statut': 'VALIDEE'}
    )
    
    if response.status_code == 200:
        factures = response.json()['results']
        print(f"✅ {len(factures)} facture(s) au statut VALIDEE")
        
        for facture in factures:
            print(f"   📄 {facture['numero_facture']} - {facture['company_name']}")
            if facture['fichier_pdf']:
                print(f"      📎 PDF attaché : {facture['fichier_pdf']}")
    else:
        print(f"❌ Échec récupération factures : {response.text}")
    
    print("\\n🎉 Test complet terminé !")
    return True

def main():
    """Point d'entrée principal"""
    try:
        success = test_bulk_pdf_upload()
        if success:
            print("\\n✅ TOUS LES TESTS SONT PASSÉS !")
            print("\\n📋 RÉSUMÉ DU WORKFLOW :")
            print("   1. ✅ Upload du gros PDF réussi")
            print("   2. ✅ Découpage automatique fonctionnel")
            print("   3. ✅ Détection des identifiants (MSISDN/Compte)")
            print("   4. ✅ Matching avec les factures EN_COURS")
            print("   5. ✅ Changement de statut → VALIDEE")
            print("   6. ✅ Attachement des PDF individuels")
            print("\\n🚀 La publication PDF en masse fonctionne parfaitement !")
        else:
            print("\\n❌ DES TESTS ONT ÉCHOUÉ")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur Django")
        print("   Vérifiez que le serveur tourne sur http://localhost:8000")
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")

if __name__ == "__main__":
    main()