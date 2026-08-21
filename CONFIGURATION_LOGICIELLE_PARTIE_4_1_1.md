# 4.1.1. Configuration logicielle

Le portail Moov e-Factures est exploité dans une architecture web séparant le frontend, le backend et les services de données. La configuration présentée ci-dessous correspond à l'environnement utilisé pour le développement et les essais de l'application.

**Tableau : Configuration logicielle de l'application**

| Composant | Version / paquet | Description / rôle |
|---|---|---|
| Système d'exploitation | Windows 11 64 bits | Système utilisé sur le poste de développement et de test. |
| Visual Studio Code | Version installée sur le poste | Environnement de développement intégré utilisé pour écrire, organiser et déboguer le code du backend et du frontend. |
| Python | 3.14.2 | Langage et environnement d'exécution du backend. |
| Django | 6.0.3 | Framework utilisé pour développer l'API et la logique métier. |
| Django REST Framework | 3.17.1 | Extension utilisée pour exposer les fonctionnalités sous forme d'API REST. |
| Simple JWT | 5.5.1 | Gestion de l'authentification par jetons. |
| React | 18.3.1 | Bibliothèque utilisée pour construire l'interface web. |
| Vite | 5.x | Outil de développement et de compilation du frontend React. |
| Node.js | 24.16.0 | Environnement d'exécution nécessaire au frontend. |
| npm | 11.13.0 | Gestionnaire des dépendances et des scripts frontend. |
| PostgreSQL | 16 | Système de gestion de base de données relationnelle utilisé pour la persistance des données. |
| Garnet | Compatible Redis | Service utilisé comme serveur de données en mémoire et comme intermédiaire pour les tâches asynchrones. |
| Celery | 5.6.3 | Exécution en arrière-plan des traitements longs, notamment le découpage et la publication des blocs PDF. |
| django-redis | 7.0.0 | Connexion de Django au serveur Garnet compatible avec le protocole Redis. |
| PyPDF2 | 3.0.1 | Lecture, découpage et manipulation des fichiers PDF. |
| Pillow / ReportLab | 12.1.1 / 4.4.10 | Traitement d'images et génération de documents PDF lorsque nécessaire. |
| PostgreSQL pour Python | psycopg 3.3.4 | Pilote permettant à Django de communiquer avec PostgreSQL. |
| Git et GitHub | Git 2.45.1 | Gestion des versions et conservation du code source. |
| Postman | Version installée sur le poste | Vérification des endpoints de l'API indépendamment de l'interface React. |
| Navigateur web | Chrome, Edge ou équivalent récent | Accès à l'interface et réalisation des tests fonctionnels. |

La base SQLite fournie dans le projet peut être utilisée pour un démarrage local rapide. Pour une exploitation plus proche de la production, PostgreSQL est recommandé. Garnet et Celery sont nécessaires lorsque les traitements PDF doivent être exécutés de manière persistante en arrière-plan ; le frontend reste accessible pendant le traitement.

Les paramètres variables, notamment les identifiants de la base de données, l'URL de Garnet, la clé secrète Django et les paramètres SMTP, sont placés dans le fichier `.env`. Les valeurs sensibles ne doivent pas être enregistrées dans le dépôt Git.
