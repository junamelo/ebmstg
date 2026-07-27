"""
Script pour créer un compte Chef Facturation
Exécuter : python manage.py shell < create_chef_facturation.py
"""

from accounts.models import User

# Créer un Chef Facturation
chef = User.objects.create_user(
    username='chef.facturation',
    email='chef.facturation@moov.africa',
    password='Chef@2026',  # Changez ce mot de passe !
    first_name='Chef',
    last_name='Facturation',
    role='CHEF_FACTURATION',
    status='ACTIF'
)

print(f"✅ Chef Facturation créé avec succès !")
print(f"   Username: {chef.username}")
print(f"   Email: {chef.email}")
print(f"   Role: {chef.role}")
print(f"   Mot de passe: Chef@2026")
print(f"\n🔗 Connectez-vous sur http://localhost:3000/login")
