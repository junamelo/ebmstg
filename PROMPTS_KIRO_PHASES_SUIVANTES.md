# Prompts Kiro — phases suivantes du projet

Ce document contient les prompts à soumettre **un par un** à Kiro après la Priorité 0 (règles métier et workflow de publication). Ne lance pas la phase suivante tant que la phase en cours n'a pas été vérifiée avec les commandes demandées.

## Règles communes à ajouter à chaque demande

Les consignes suivantes s'appliquent à toutes les phases :

- Lis les fichiers concernés avant toute modification et vérifie les modèles, serializers, routes et migrations existants.
- Ne crée ni données mock, ni champs inexistants, ni nouveaux modèles sans migration Django.
- Ne remplace pas du code fonctionnel sans expliquer la raison et sans conserver la compatibilité.
- Ne modifie pas les données de démonstration existantes, ne supprime aucun fichier et n'exécute aucune commande destructive.
- Utilise les API backend existantes ; n'invente pas une seconde API côté frontend.
- Ajoute des tests réels pour toute logique métier nouvelle ou corrigée.
- Avant de conclure, exécute `python manage.py check`, les tests pertinents et la vérification frontend disponible.
- Dans le résultat final, indique les fichiers modifiés, les commandes exécutées avec leurs résultats et les limites restantes. Ne dis pas « terminé » lorsqu'une vérification échoue.

---

## Phase 1 — Remplacer tous les mocks par les API réelles

```text
Tu dois terminer le raccordement frontend/backend de l'application. Objectif : supprimer les données mock des écrans métier et faire utiliser les API Django réelles, sans modifier les règles métier déjà validées.

Périmètre : gestion des utilisateurs, agents de facturation, comptes/payeurs, services, forfaits, contrats, tableaux de bord, historique et toutes les pages qui utilisent encore des tableaux ou services mock.

Travail demandé :

1. Fais un audit précis du frontend : cherche mock, fake, hardcoded, USE_MOCK, tableaux statiques, localStorage utilisé comme source métier et appels API obsolètes.
2. Pour chaque écran trouvé, associe l'endpoint backend réellement disponible. Vérifie les serializers, permissions et formats de réponse avant de coder.
3. Remplace les mocks progressivement par les appels API réels. Garde des adaptateurs frontend uniquement si le format de l'interface le nécessite ; ces adaptateurs ne doivent pas inventer de données.
4. Corrige les chemins API obsolètes, notamment tout chemin différent des routes réellement enregistrées dans Django.
5. Ajoute sur chaque écran : chargement, erreur lisible, état vide et rechargement après création/modification/suppression si cette opération est autorisée.
6. Ne crée pas d'écran pour une API inexistante. Dans ce cas, implémente l'API Django complète uniquement si le modèle métier existe déjà et si les permissions sont définies.
7. Vérifie les rôles : administrateur, chef de facturation, agent, payeur et employé ne doivent voir que les actions et données autorisées.
8. Ne touche pas au workflow de publication sauf pour corriger une intégration nécessaire et compatible avec la spécification.

Critères d'acceptation :
- aucune donnée mock ne pilote une fonctionnalité métier ;
- création, lecture, modification et suppression autorisées se reflètent après rechargement ;
- aucun 404, 401 ou 403 inattendu sur les parcours testés ;
- les rôles ne peuvent pas accéder aux données d'un autre rôle ou d'une autre entreprise.

Vérifications obligatoires :
- `python manage.py check`
- `python manage.py test`
- build ou vérification de compilation du frontend selon le script réellement défini dans package.json
- liste finale des mocks volontairement conservés, avec justification ; s'il n'y en a aucun, l'indiquer explicitement.
```

---

## Phase 2 — Gestion complète des utilisateurs, entreprises et affectations

```text
Tu dois rendre complète et fiable la gestion des comptes et l'affectation des factures aux employés.

Règle métier impérative : une facture employé est reliée à une ligne téléphonique (`Invoice.line`), une ligne est reliée à un employé (`Line.employe`), et l'employé connecté ne peut consulter que les factures PUBLIEE de ses propres lignes. Le MSISDN sert à établir la liaison lors de l'import PDF, mais ne doit pas remplacer les relations de base de données.

Travail demandé :

1. Auditer les modèles et endpoints User, Company, Line, Invoice et les serializers associés.
2. Rendre opérationnels les écrans de création, modification, activation/désactivation et consultation des utilisateurs lorsque les permissions le permettent.
3. Rendre opérationnelle l'affectation d'une ligne à un employé et son retrait. Vérifier les contrôles d'entreprise et les permissions.
4. Empêcher les incohérences : ligne sans entreprise, ligne attribuée à un utilisateur non employé, accès à une ligne d'une autre entreprise, doublon de MSISDN si le modèle l'interdit.
5. Vérifier l'import PDF : lorsqu'un MSISDN est reconnu, l'Invoice doit être associée à la bonne Line existante. Lorsqu'il n'est pas reconnu, retourner un résultat clair sans divulguer de données sensibles.
6. Vérifier les listes pour chaque rôle et les filtres par entreprise, utilisateur, ligne, période et statut si ces filtres existent dans l'interface.
7. Ne crée pas de nouveaux employés fictifs dans les scripts de test de développement.

Tests minimaux à créer :
- un administrateur/chef autorisé peut attribuer une ligne à un employé ;
- un employé voit seulement ses factures publiées ;
- un autre employé ne les voit pas ;
- un payeur ne voit que les factures publiées de son entreprise ;
- une ligne non attribuée et une facture sans ligne sont gérées proprement ;
- tentative d'affectation inter-entreprise refusée.

Vérifications obligatoires :
- `python manage.py check`
- tests Django ciblés et complets
- vérification frontend avec un compte de chaque rôle, sans changer la base de démonstration.
```

---

## Phase 3 — Contrats, services, forfaits et tarification

```text
Tu dois finaliser la gestion métier des contrats, services, forfaits et tarifs. Le résultat doit être cohérent avec les factures sans inventer de calculs non validés.

Travail demandé :

1. Lire la spécification métier et les modèles existants avant toute modification.
2. Auditer les fonctionnalités actuelles : création/modification de contrats, services, forfaits, paliers, tarifs, dates de validité et rattachement à une entreprise ou à une ligne.
3. Corriger les écrans encore mock et les raccorder aux API réelles.
4. Valider les règles de cohérence : dates de début/fin, tarifs non négatifs, contrat rattaché à la bonne entreprise, service actif/inactif, impossibilité de sélectionner un élément archivé lorsque cela est interdit.
5. S'il existe un calcul de facture basé sur contrat/forfait, le rendre déterministe, testable et traçable. Ne pas modifier des factures déjà publiées ; toute régénération doit respecter les statuts et l'historique.
6. Si une règle tarifaire manque dans la spécification, ne l'invente pas : liste-la clairement comme décision métier à obtenir.
7. Ajouter les messages d'erreur côté API et côté interface.

Tests minimaux :
- création valide et refus d'un contrat incohérent ;
- application correcte d'un tarif ou forfait actif ;
- non-application d'un tarif expiré/inactif ;
- isolation des données entre entreprises ;
- absence de modification d'une facture PUBLIEE ou PAYEE.

Vérifications obligatoires :
- migrations si et seulement si les modèles changent ;
- `python manage.py check`
- tests des applications concernées ;
- compilation frontend.
```

---

## Phase 4 — Génération, import et traitement robuste des factures PDF

```text
Tu dois fiabiliser de bout en bout le traitement des factures PDF postpayées : import, découpage, extraction, rapprochement, erreurs et publication. Respecte strictement le workflow métier déjà établi.

Règles :
- import PDF réussi => facture VALIDEE, jamais PUBLIEE automatiquement ;
- publication explicite par agent/chef => facture PUBLIEE ;
- visibilité client uniquement après publication ;
- rapprochement par MSISDN vers la ligne existante, puis vers l'employé ;
- une erreur sur une page/facture ne doit pas bloquer les autres éléments valides du lot.

Travail demandé :

1. Auditer les limites de fichier, contrôles MIME, extensions, taille, pages et gestion des PDF protégés ou illisibles.
2. Vérifier le découpage des gros PDF et le nommage des fichiers générés. Éviter les collisions et les fichiers orphelins en cas d'erreur.
3. Améliorer le rapport de traitement : total traité, factures créées, mises à jour, ignorées, erreurs détaillées par page/numéro de facture, sans exposer de données non nécessaires.
4. Rendre l'opération idempotente : réimporter le même PDF ne doit ni créer de doublons ni transformer une facture déjà publiée.
5. Vérifier la détection du MSISDN et du numéro de facture sur les vrais formats de PDF fournis. Ne pas promettre d'OCR si l'OCR n'est pas implémenté.
6. S'assurer que les fichiers PDF sont accessibles seulement par les utilisateurs autorisés ou, si l'architecture actuelle utilise des médias publics, documenter explicitement cette limite et proposer une correction séparée.
7. Prévoir une stratégie sûre pour les lots très volumineux : pas de timeout silencieux, retour clair à l'utilisateur. Ne mets pas en place Celery/Redis sans configuration complète et validée.

Tests minimaux :
- PDF valide contenant plusieurs factures ;
- réimport du même lot ;
- page invalide au milieu d'un lot ;
- MSISDN reconnu et non reconnu ;
- facture déjà PUBLIEE ;
- fichier non-PDF et PDF illisible ;
- contrôle d'accès au téléchargement.

Vérifications obligatoires :
- tests backend ciblés ;
- test manuel avec un petit PDF anonymisé de référence ;
- `python manage.py check` ;
- ne modifie pas les PDF sources de l'utilisateur.
```

---

## Phase 5 — Sécurité, authentification et gestion de session

```text
Tu dois sécuriser l'authentification et les autorisations de l'application sans casser les comptes et identifiants de démonstration existants.

Travail demandé :

1. Auditer login, refresh token, logout, stockage du token frontend, expiration de session, redirections et contrôle des routes protégées.
2. Conserver la connexion par email ou MSISDN si elle est déjà prévue, avec validation correcte des entrées et messages d'erreur non révélateurs.
3. Vérifier que chaque endpoint sensible utilise les permissions adaptées : utilisateurs, entreprises, lignes, contrats, factures, PDF, publication et historique.
4. Corriger les routes frontend qui affichent un écran sans vérifier le rôle réel de l'utilisateur.
5. Pour « mot de passe oublié », ne conserve pas un écran factice : soit implémente entièrement le flux avec e-mail configuré, soit masque/désactive l'option avec un message explicite de fonctionnalité indisponible. Ne crée pas d'endpoint simulé.
6. Mettre les secrets et paramètres sensibles hors du code source quand la configuration actuelle le permet, via variables d'environnement documentées. Ne régénère pas de secret en production et ne divulgue aucune valeur sensible.
7. Vérifier CORS, DEBUG, ALLOWED_HOSTS et accès aux fichiers média selon les environnements, sans casser le développement local.

Tests minimaux :
- refus des actions non autorisées pour chaque rôle ;
- refus sans token et avec token expiré/invalide ;
- accès employé/payeur limité à ses données ;
- absence de fuite de détails techniques dans les réponses d'erreur.

Vérifications obligatoires :
- `python manage.py check --deploy` en interprétant les avertissements sans les masquer ;
- tests d'authentification et de permissions ;
- compilation frontend.
```

---

## Phase 6 — Qualité, tests d'intégration et préparation de livraison

```text
Tu dois préparer l'application pour une livraison complète et maintenable. Cette phase ne doit pas ajouter de nouvelles fonctionnalités métier ; elle sert à vérifier, corriger les défauts et documenter l'exécution du projet.

Travail demandé :

1. Auditer les erreurs console frontend, erreurs serveur, imports inutilisés, routes mortes, appels API obsolètes, formulaires sans validation et incohérences d'affichage.
2. Créer ou compléter une suite de tests Django pour les parcours critiques : authentification, comptes, affectations, contrats/tarifs, import PDF, publication, consultation employé/payeur.
3. Ajouter les tests frontend existants seulement si l'outillage du projet le permet déjà. Ne pas introduire une lourde dépendance uniquement pour afficher un pourcentage de couverture.
4. Vérifier manuellement les parcours complets avec les rôles disponibles : administrateur, chef, agent, payeur, employé.
5. Mettre à jour un seul guide de démarrage fiable : prérequis, installation, migrations, création des données de démonstration si un script officiel existe, lancement backend, lancement frontend, comptes de test sans mots de passe réels sensibles.
6. Créer ou mettre à jour `.env.example` sans secrets. Ne pas inclure la base SQLite locale, les PDF clients ou les tokens dans Git.
7. Préparer une liste de limites honnêtes : OCR non disponible, traitement asynchrone absent, stockage média à sécuriser, e-mail non configuré, etc. Ne marque pas ces éléments comme terminés s'ils ne le sont pas.

Critères de sortie :
- backend démarre ;
- frontend démarre et compile ;
- migrations applicables sur une base neuve ;
- tests critiques verts ;
- parcours démonstration documenté ;
- aucune dépendance à des données mock pour les fonctions métier.

Commandes à exécuter et rapporter exactement :
- `python manage.py check`
- `python manage.py check --deploy`
- `python manage.py test`
- commandes frontend réellement définies dans package.json (installation/build/test selon disponibilité)
- `python manage.py makemigrations --check --dry-run`
```

---

## Ordre d'exécution recommandé

1. Terminer d'abord la correction actuelle du workflow de publication demandée à Kiro.
2. Phase 1 : supprimer les mocks et reconnecter l'interface.
3. Phase 2 : fiabiliser les utilisateurs, lignes et affectations.
4. Phase 3 : contrats, services et tarification.
5. Phase 4 : robustesse PDF et facturation.
6. Phase 5 : sécurité et authentification.
7. Phase 6 : tests, nettoyage et livraison.

Une phase peut révéler une anomalie de la phase précédente : dans ce cas, corriger le défaut minimal puis reprendre la phase, sans dériver vers une fonctionnalité non demandée.
