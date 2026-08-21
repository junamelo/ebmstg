# 3.2.1. Architecture matérielle

L'architecture matérielle de l'application **Moov e-Factures** repose sur un modèle client-serveur. Elle décrit les équipements et les services qui participent à l'exécution de la plateforme, à la conservation des données et au traitement des fichiers PDF. Dans l'environnement de développement, ces différents composants peuvent fonctionner sur un même ordinateur. Pour un déploiement de production, ils peuvent être répartis sur plusieurs serveurs afin d'améliorer la sécurité, les performances et la maintenance.

Notre architecture est organisée autour de trois ensembles : la couche de présentation, la couche métier et la couche d'accès aux données.

## Couche de présentation

La couche de présentation correspond aux utilisateurs qui accèdent au portail depuis un navigateur web. Elle concerne le super administrateur, le chef de facturation, l'agent de facturation, le commercial, le payeur et l'employé. L'interface web a été développée avec React et Vite, puis elle est exécutée dans le navigateur de l'utilisateur.

Le navigateur permet de consulter les tableaux de bord, les contrats, les lignes, les factures, les forfaits, les services et les historiques. Il permet également de lancer une simulation et d'importer un fichier PDF lorsque l'utilisateur possède les droits nécessaires. Les échanges entre le navigateur et le serveur applicatif s'effectuent au moyen de requêtes HTTP ou HTTPS et de données au format JSON. Lorsqu'un fichier est envoyé, la requête utilise également le format multipart/form-data.

## Couche métier

La couche métier est assurée par le serveur applicatif qui exécute l'API développée avec Django et Django REST Framework. Il reçoit les requêtes envoyées par le frontend, vérifie l'authentification et les permissions, applique les règles métier, puis prépare les réponses destinées au navigateur.

Cette couche prend en charge la gestion des comptes, des rôles, des entreprises, des contrats, des lignes, des forfaits, des services, des factures et des simulations. Elle contrôle également le rapprochement entre les factures découpées et les comptes ou les lignes correspondants.

Le traitement des gros blocs PDF est confié à un worker Celery. Celui-ci exécute les tâches longues en arrière-plan afin que le navigateur ne reste pas bloqué pendant le découpage et la publication. Garnet, compatible avec le protocole Redis, sert de broker pour transmettre les tâches au worker et pour faciliter le suivi des résultats du traitement.

## Couche d'accès aux données

La couche d'accès aux données est principalement assurée par PostgreSQL. Cette base de données relationnelle conserve les utilisateurs, les entreprises, les contrats, les lignes téléphoniques, les factures, les forfaits, les services, les simulations, les historiques de publication et les journaux d'actions.

Les fichiers PDF ne sont pas stockés directement dans les tables PostgreSQL. Ils sont conservés dans le stockage média de l'application, tandis que la base enregistre le chemin et les informations nécessaires pour retrouver chaque document. Le worker Celery lit les fichiers importés, crée les PDF individuels et enregistre leur association avec les factures dans la base de données.

## Communication entre les composants

Les communications entre les différents composants reposent sur des protocoles standards :

- HTTP ou HTTPS et JSON entre le navigateur et l'API Django ;
- SQL entre l'API Django et PostgreSQL ;
- protocole Redis entre l'application, Garnet et Celery ;
- lecture et écriture de fichiers entre le worker Celery et le stockage média.

Dans l'environnement de développement utilisé pour le projet, le serveur Django, le frontend, PostgreSQL, Garnet et le worker Celery peuvent être lancés sur le même ordinateur. L'ordinateur utilisé pour les essais est un Huawei MateBook D14 équipé d'un processeur AMD Ryzen 5, de 8 Go de mémoire vive, d'un SSD et du système Windows 11.

Dans une architecture cible, le navigateur des utilisateurs communique avec un serveur web ou un serveur frontend. L'API Django est exécutée par un serveur applicatif, PostgreSQL est placé sur un serveur de données protégé, Garnet et les workers Celery sont supervisés séparément et les fichiers PDF sont conservés dans un stockage média sécurisé. Cette séparation permet de limiter les accès directs à la base, de traiter plusieurs imports simultanément et de faire évoluer les ressources sans modifier l'interface utilisateur.

![Figure : Architecture matérielle de l'application Moov e-Factures](docs/architecture_materielle_moov_efactures_nb.png)

*Figure : Architecture matérielle de l'application Moov e-Factures.*

# 3.2.2. Architecture logicielle

L'architecture logicielle de l'application **Moov e-Factures** repose sur une architecture client-serveur qui sépare l'interface utilisateur, la logique métier et la persistance des données. Cette organisation facilite la maintenance, les tests et l'évolution de la plateforme.

## Frontend React / Vite

Le frontend a été développé avec React et Vite. React organise l'interface en composants réutilisables et Vite assure le lancement du serveur de développement ainsi que la compilation. React Router protège la navigation selon les rôles, tandis qu'Axios centralise les appels vers l'API. Cette couche regroupe les tableaux de bord, les formulaires, les contrats, les factures, la publication et la simulation.

## Backend Django et Django REST Framework

Le backend est développé avec Python, Django et Django REST Framework. Les applications `accounts` et `billing` regroupent respectivement l'authentification, les rôles, les utilisateurs et les fonctions de facturation. Les vues, serializers et permissions traitent les requêtes REST, valident les données et limitent chaque action au rôle autorisé. Les échanges sont sécurisés par des jetons JWT.

## Données et traitement des PDF

Les modèles Django et l'ORM assurent la gestion des utilisateurs, entreprises, contrats, lignes, factures, services, forfaits et historiques dans PostgreSQL. Les fichiers PDF sont conservés dans le stockage média, tandis que la base enregistre leurs métadonnées, leur statut et leur chemin d'accès.

Le service PDF extrait les identifiants, découpe les blocs et tente le rapprochement avec les factures. Les traitements longs sont exécutés par Celery, avec Garnet comme broker compatible Redis. Le statut persistant passe de `EN_ATTENTE` à `EN_COURS`, puis à `TERMINE` ou `ECHEC`, ce qui permet au frontend d'afficher le résultat sans bloquer l'utilisateur.

## Sécurité et contrôle des accès

La sécurité repose sur l'authentification Django, les jetons JWT et les permissions par rôle. Le payeur est limité à son contrat et l'employé à sa ligne. Le 2FA basé sur TOTP est optionnel pour les opérations sensibles. Les communications utilisent HTTP/HTTPS et JSON, SQL pour PostgreSQL, le protocole Redis pour Garnet et `multipart/form-data` pour les importations PDF. Cette séparation permet de faire évoluer les rôles, les services et les formats de facture sans modifier toute l'application.
