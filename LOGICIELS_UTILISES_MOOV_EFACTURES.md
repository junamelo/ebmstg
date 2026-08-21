# 3.1.2. Logiciels utilisés et justification des choix

Les logiciels et technologies présentés ci-dessous sont ceux qui ont réellement été utilisés pour concevoir, développer et tester le portail **Moov e-Factures**. Les choix ont été faits en fonction du caractère web de l'application, de la gestion des rôles, du traitement des fichiers PDF et du besoin de conserver les données dans une base relationnelle.

## Python et Django

**Description :** Python est le langage utilisé pour développer le backend. Django est un framework web open source qui fournit une structure organisée pour créer des applications web, gérer les utilisateurs, les modèles de données et les migrations.

**Justification :** Django a été retenu parce qu'il permet de développer rapidement une application structurée. Son ORM facilite la gestion des utilisateurs, contrats, lignes, factures, forfaits et services. Les migrations permettent également de faire évoluer la base de données sans modifier manuellement les tables.

**Alternative envisageable :** Laravel ou Symfony auraient pu être utilisés, mais ils reposent sur PHP et auraient nécessité un changement de langage et d'environnement. Node.js aurait également été possible, mais Django était mieux adapté à l'organisation du backend déjà commencée.

## Django REST Framework et JWT

**Description :** Django REST Framework est une extension de Django qui permet de construire des API REST. JWT est utilisé pour authentifier les utilisateurs au moyen de jetons d'accès et de renouvellement.

**Justification :** cette combinaison sépare clairement le frontend React du backend Django. Elle permet au frontend d'appeler les routes de connexion, de contrats, de lignes, de factures, de publications et de simulations. Les permissions vérifient ensuite le rôle de l'utilisateur avant de donner accès aux données.

**Alternative envisageable :** une authentification par session Django aurait été possible, mais les jetons JWT sont mieux adaptés à une application frontend séparée du backend.

## React et Vite

**Description :** React est une bibliothèque JavaScript utilisée pour construire l'interface web. Vite est l'outil utilisé pour lancer le serveur de développement et compiler l'application pour la livraison.

**Justification :** React permet de créer des interfaces adaptées aux différents profils : administrateur, chef, agent, commercial, payeur et employé. Les composants réutilisables facilitent la création des tableaux, formulaires, modales, paginations, notifications et badges d'état. Vite fournit un démarrage rapide et une compilation efficace.

**Bibliothèques frontend associées :** Axios est utilisé pour communiquer avec l'API, React Router pour la navigation, Recharts pour certains graphiques et Tailwind CSS pour la mise en forme de l'interface.

**Alternative envisageable :** Vue.js ou Angular auraient également permis de développer le portail. React a été conservé car il correspondait à la base frontend déjà commencée et permettait de réutiliser facilement les composants.

## PostgreSQL et SQLite

**Description :** PostgreSQL est le système de gestion de base de données relationnelle retenu pour l'environnement cible. SQLite reste disponible comme solution de secours pour certains essais locaux lorsque PostgreSQL n'est pas configuré.

**Justification :** PostgreSQL convient aux relations entre utilisateurs, entreprises, contrats, lignes, factures, forfaits, services et historiques. Il assure les contraintes d'unicité et la cohérence nécessaires au rapprochement des factures. Le support SQLite facilite les premiers tests sur un poste de développement, mais PostgreSQL est recommandé dès que plusieurs services ou utilisateurs travaillent en même temps.

**Alternative envisageable :** MySQL aurait pu être utilisé, mais PostgreSQL a été retenu pour sa robustesse et sa bonne intégration avec Django.

## Celery et Garnet

**Description :** Celery est utilisé pour exécuter les traitements longs en arrière-plan. Garnet est un serveur compatible avec le protocole Redis et sert de broker pour transmettre les tâches ainsi que de backend pour leurs résultats.

**Justification :** le découpage de gros blocs PDF peut prendre du temps. Sans tâche asynchrone, la requête web resterait bloquée et l'utilisateur ne pourrait pas quitter la page. Avec Celery et Garnet, le traitement possède un statut persistant (`EN_ATTENTE`, `EN_COURS`, `TERMINE` ou `ECHEC`) et continue même si l'agent change de page. Le cache peut également être séparé du broker et des résultats grâce aux bases logiques configurées.

**Alternative envisageable :** Redis associé à Celery aurait également convenu. Garnet a été utilisé parce qu'il est compatible avec le protocole Redis dans l'environnement de développement. Une exécution synchrone reste possible pour de petits essais, mais elle n'est pas adaptée aux gros fichiers PDF.

## PyPDF2, Pillow et pdf2image

**Description :** PyPDF2 est utilisé pour lire, analyser et découper les documents PDF. Pillow et pdf2image servent aux opérations complémentaires liées aux images et à la conversion de pages lorsque cela est nécessaire.

**Justification :** ces bibliothèques permettent de parcourir les pages d'un bloc PDF, d'extraire le texte, de détecter les identifiants utiles et de produire un fichier individuel pour chaque facture. Elles répondent au besoin principal de publication des factures globales et sommaires.

**Limite :** la version actuelle privilégie les PDF contenant une couche de texte. `pytesseract` est prévu comme dépendance optionnelle pour une évolution OCR, mais la reconnaissance de documents scannés n'est pas considérée comme une fonction entièrement disponible dans la version actuelle.

## Google Authenticator et TOTP

**Description :** le double facteur optionnel repose sur un code TOTP compatible avec Google Authenticator. Les bibliothèques `pyotp`, `qrcode` et `cryptography` sont utilisées pour générer, afficher et vérifier le secret du deuxième facteur.

**Justification :** l'utilisateur peut activer le 2FA depuis son profil. Lorsqu'il est activé, le code temporaire est demandé lors des opérations sensibles, notamment la modification du mot de passe. Cette protection renforce la sécurité des comptes sans imposer le 2FA à tous les utilisateurs.

## Kiro, navigateur et outils de test

**Description :** Kiro a été utilisé comme environnement principal d'aide au développement et de travail sur le code. Le navigateur a servi à tester les interfaces et les différents rôles. Les tests backend sont exécutés avec les outils de test Django et les vérifications frontend sont réalisées avec les commandes `npm run build` et `npm run lint` lorsqu'elles sont disponibles.

**Justification :** cet ensemble permet de vérifier le fonctionnement complet de l'application : connexion, gestion des contrats, affectation des lignes, import PDF, publication, consultation des factures et simulation. Les erreurs de la console et les réponses de l'API sont contrôlées pendant les essais.

## Visual Studio Code

**Description :** Visual Studio Code, souvent abrégé VS Code, est un éditeur de code source gratuit et multiplateforme développé par Microsoft. Il peut être utilisé comme environnement de développement intégré (IDE) grâce à ses extensions, son terminal intégré, ses outils de recherche, son système de débogage et sa prise en charge de nombreux langages et frameworks.

**Justification :** il a servi d'IDE pour le développement du portail Moov e-Factures. Il a permis d'écrire et de modifier le backend Django en Python, le frontend React, les fichiers de configuration et la documentation Markdown. Son terminal intégré a également facilité le lancement du serveur Django, du frontend et des commandes de test. Il a été utilisé en complément de Kiro pour les corrections et les vérifications manuelles.

**Alternatives envisageables :** Kiro, utilisé en complément pour l'assistance au développement et l'analyse du projet ; PyCharm, qui propose un environnement spécialisé pour Python et Django ; WebStorm, orienté vers le développement JavaScript et React. Ces solutions auraient également pu être utilisées, mais Visual Studio Code a été retenu pour sa légèreté, sa polyvalence et ses nombreuses extensions.

## Git et GitHub

**Description :** Git est l'outil de gestion de versions utilisé pour enregistrer les modifications du projet. GitHub sert de dépôt distant pour conserver le code, suivre son évolution et disposer d'une sauvegarde du projet.

**Justification :** l'association de Git et GitHub permet de garder un historique des corrections, de revenir à une version stable et de sécuriser le travail réalisé sur le backend, le frontend et la documentation. Elle facilite également le suivi des différentes phases de développement.

## Postman

**Description :** Postman est un outil de test, de développement et de documentation d'API REST. Il permet d'envoyer des requêtes HTTP, notamment GET, POST, PUT et DELETE, puis d'examiner les réponses retournées par le serveur Django REST Framework.

**Justification :** Postman a été choisi pour sa large adoption dans le développement d'API, son interface accessible et sa capacité à organiser les requêtes dans des collections et des environnements. Il prend en charge les paramètres, les en-têtes, les jetons JWT et les scripts de test, tout en facilitant le partage des scénarios entre développeurs. Il a donc été préféré à des outils plus légers comme Insomnia ou Thunder Client lorsque des tests structurés et une documentation des endpoints étaient nécessaires.

**Alternatives envisageables :** Insomnia, un outil équivalent plus léger qui offre des fonctionnalités de test similaires, mais dont l'écosystème de documentation partagée est moins répandu ; Thunder Client, une extension légère intégrée directement à Visual Studio Code, adaptée aux tests rapides mais moins complète que Postman pour la documentation et le suivi des requêtes.

## Résumé des choix

| Ressource | Utilisation principale |
|---|---|
| Python / Django | Backend, modèles, règles métier et API |
| Django REST Framework / JWT | Échanges frontend-backend et authentification |
| React / Vite | Interface web et compilation frontend |
| PostgreSQL | Base de données cible |
| SQLite | Solution de secours pour certains tests locaux |
| Celery / Garnet | Traitements PDF en arrière-plan |
| PyPDF2 / Pillow / pdf2image | Lecture et découpage des PDF |
| pyotp / qrcode / cryptography | Double authentification optionnelle |
| Visual Studio Code (IDE) / Kiro | Développement, correction et lecture du code |
| Git / GitHub | Gestion des versions et sauvegarde distante du projet |
| Postman | Tests directs des API REST |
| Navigateur | Tests et vérification des interfaces |
