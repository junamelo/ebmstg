"""
Script pour initialiser l'environnement Phase 1
"""
import os
import sys
from pathlib import Path

def setup():
    """Initialiser les dossiers et fichiers nécessaires"""
    
    BASE_DIR = Path(__file__).resolve().parent
    
    print("🚀 Configuration Phase 1 - Authentification & Gestion Utilisateurs")
    print("=" * 60)
    
    # 1. Créer le dossier logs
    logs_dir = BASE_DIR / 'logs'
    if not logs_dir.exists():
        logs_dir.mkdir()
        print(f"✅ Dossier créé : {logs_dir}")
    else:
        print(f"ℹ️  Dossier existant : {logs_dir}")
    
    # 2. Créer le dossier media
    media_dir = BASE_DIR / 'media'
    if not media_dir.exists():
        media_dir.mkdir()
        print(f"✅ Dossier créé : {media_dir}")
    else:
        print(f"ℹ️  Dossier existant : {media_dir}")
    
    # 3. Créer .gitignore pour les logs
    gitignore_path = logs_dir / '.gitignore'
    if not gitignore_path.exists():
        with open(gitignore_path, 'w') as f:
            f.write('*.log\n')
        print(f"✅ Fichier créé : {gitignore_path}")
    
    # 4. Créer .gitignore pour media
    gitignore_media_path = media_dir / '.gitignore'
    if not gitignore_media_path.exists():
        with open(gitignore_media_path, 'w') as f:
            f.write('*\n!.gitignore\n')
        print(f"✅ Fichier créé : {gitignore_media_path}")
    
    print("\n" + "=" * 60)
    print("✅ Configuration terminée !")
    print("\n📋 Prochaines étapes :")
    print("   1. python manage.py makemigrations")
    print("   2. python manage.py migrate")
    print("   3. python create_superuser.py (si nécessaire)")
    print("   4. python manage.py runserver")
    print("\n📖 Documentation : Lire PHASE1_README.md")

if __name__ == '__main__':
    setup()
