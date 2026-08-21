# 3.2.2. Architecture logicielle

L'architecture logicielle de l'application **Moov e-Factures** repose sur une architecture client-serveur qui sépare l'interface utilisateur, la logique métier et la persistance des données. Cette organisation facilite la maintenance, les tests et l'évolution de la plateforme.

## Frontend React / Vite

Le frontend a été développé avec React et Vite. React organise l'interface en composants réutilisables et Vite assure le lancement du serveur de développement ainsi que la compilation. React Router protège la navigation selon les rôles, tandis qu'Axios centralise les appels vers l'API. Cette couche regroupe les tableaux de bord, les formulaires, les contrats, les factures, la publication et la simulation.

## Backend Django et Django REST Framework

Le backend est développé avec Python, Django et Django REST Framework. Les applications `accounts` et `billing` regroupent respectivement l'authentification, les rôles, les utilisateurs et les fonctions de facturation. Les vues, serializers et permissions traitent les requêtes REST, valident les données et limitent chaque action au rôle autorisé. Les échanges sont sécurisés par des jetons JWT.

## Données et traitement des PDF

Les modèles Django et l'ORM assurent la gestion des utilisateurs, entreprises, contrats, lignes, factures, services, forfaits et historiques dans PostgreSQL. Les fichiers PDF sont conservés dans le stockage média, tandis que la base enregistre leurs métadonnées, leur statut et leur chemin d'accès.

Le service PDF extrait les identifiants, découpe les blocs et tente le rapprochement avec les factures. Les traitements longs sont exécutés par Celery, avec Garnet comme broker compatible Redis. Le statut persistant passe de `EN_ATTENTE` à `EN_COURS`, puis à `TERMINE` ou `ECHEC`, ce qui permet au frontend d'afficher le résultat sans bloquer l'utilisateur.

## Sécurité et communications

La sécurité repose sur l'authentification Django, les jetons JWT et les permissions par rôle. Le payeur est limité à son contrat et l'employé à sa ligne. Le 2FA basé sur TOTP est optionnel pour les opérations sensibles. Les communications utilisent HTTP/HTTPS et JSON, SQL pour PostgreSQL, le protocole Redis pour Garnet et `multipart/form-data` pour les importations PDF. Cette séparation permet de faire évoluer les rôles, les services et les formats de facture sans modifier toute l'application.
