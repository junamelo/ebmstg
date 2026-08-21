# 4.2.1. Déploiement de l'application

Le déploiement de Moov e-Factures consiste à rendre disponibles le frontend React, l'API Django, la base de données et le service chargé des traitements PDF. Dans le cadre du projet, le déploiement est d'abord réalisé en environnement local afin de vérifier le fonctionnement complet de l'application avant une éventuelle installation sur un serveur.

## Préparation de l'environnement

Le code source est récupéré depuis le dépôt Git, puis les dépendances sont installées séparément pour le backend et le frontend. Le backend est exécuté avec Python et Django. Le frontend est construit avec Node.js, npm et Vite.

La configuration est centralisée dans le fichier `.env`, placé à la racine du projet et exclu du dépôt Git. Il contient notamment la clé secrète Django, le mode de débogage, les paramètres PostgreSQL, l'URL de Garnet, ainsi que les paramètres éventuels de notification. Les mots de passe et les clés d'API ne doivent pas être inscrits directement dans le code source.

## Déploiement du backend

Depuis le dossier `Back`, les migrations sont appliquées afin de créer ou de mettre à jour les tables de la base de données :

```text
python manage.py migrate
```

Le serveur Django est ensuite démarré avec la commande suivante :

```text
python manage.py runserver
```

L'API est alors accessible à l'adresse `http://localhost:8000/api/`. La documentation interactive est disponible, selon la configuration du projet, à l'adresse `http://localhost:8000/api/docs/`.

Lorsque PostgreSQL est activé dans `.env`, Django utilise cette base au lieu de SQLite. SQLite reste disponible comme solution de secours pour les essais locaux lorsque les variables PostgreSQL ne sont pas renseignées.

## Déploiement du frontend

Depuis le dossier `Front`, les dépendances sont installées puis l'application est lancée en mode développement :

```text
npm install
npm run dev
```

L'interface est accessible à l'adresse `http://localhost:3000/`. Pour préparer une version optimisée, la commande de compilation est utilisée :

```text
npm run build
```

Le frontend communique avec l'API Django configurée sur le port 8000. Les adresses utilisées par les services frontend doivent être adaptées lorsqu'un serveur distant remplace l'environnement local.

## Services PostgreSQL, Garnet et Celery

PostgreSQL conserve les comptes, contrats, lignes, forfaits, services et factures. Garnet, compatible avec le protocole Redis, fournit le cache et le broker utilisé par Celery. Le fichier `docker-compose.yml` est prévu pour lancer PostgreSQL et Redis dans des conteneurs lorsque Docker est disponible. Dans l'environnement de développement utilisé, PostgreSQL et Garnet peuvent également être installés et démarrés directement sur Windows.

Pour exécuter les traitements PDF longs indépendamment de l'interface, un worker Celery est démarré depuis le dossier `Back` :

```text
python -m celery -A moov_backend worker -l INFO -P solo
```

Le worker reçoit les tâches de découpage et de publication via Garnet. L'utilisateur peut donc quitter la page de publication pendant que le traitement se poursuit. Le statut persistant du traitement permet de suivre les états `EN_ATTENTE`, `EN_COURS`, `TERMINE` ou `ECHEC`.

## Ordre recommandé de démarrage

1. Démarrer PostgreSQL.
2. Démarrer Garnet.
3. Lancer le worker Celery.
4. Démarrer le backend Django.
5. Démarrer le frontend React.
6. Ouvrir `http://localhost:3000/` dans un navigateur.

Pour une installation sur serveur, les mêmes composants doivent être placés derrière une configuration réseau sécurisée. Le mode DEBUG doit être désactivé, les fichiers média doivent être protégés, les variables secrètes doivent être fournies par l'environnement du serveur et les sauvegardes de PostgreSQL doivent être planifiées.
