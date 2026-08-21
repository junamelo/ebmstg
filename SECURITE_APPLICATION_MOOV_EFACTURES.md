# 3.3. SÉCURITÉ DE L'APPLICATION

La sécurité de **Moov e-Factures** repose sur l'authentification, le contrôle des rôles et la protection des données et des fichiers PDF.

## Authentification et autorisations

Le backend Django utilise Django REST Framework et des jetons JWT pour sécuriser les échanges avec React. Les mots de passe sont hachés et contrôlés par les validateurs de Django. Les permissions de l'API limitent chaque action au rôle autorisé : le super administrateur possède l'accès global, le chef et l'agent gèrent la facturation, le commercial suit ses demandes, le payeur son contrat et l'employé sa ligne.

Le frontend protège les routes selon le rôle et transmet le jeton dans l'en-tête `Authorization`. Cette protection côté interface est complétée par les vérifications obligatoires du backend.

## Double authentification

Le 2FA est optionnel et compatible avec Google Authenticator. Lorsqu'il est activé, un code TOTP à six chiffres est demandé pour modifier le mot de passe. Le secret est chiffré avant son enregistrement et le code est vérifié côté serveur.

## Données et fichiers PDF

PostgreSQL conserve les données métier avec leurs relations et contraintes d'unicité. Les factures sont filtrées par contrat ou par ligne afin d'empêcher un accès entre entreprises ou entre employés. Les PDF sont conservés dans le stockage média et doivent être servis uniquement après vérification des droits.

Les secrets, mots de passe et paramètres SMTP sont fournis par les variables d'environnement et ne doivent pas être versionnés. Avant la production, il faudra désactiver `DEBUG`, imposer HTTPS, définir les hôtes autorisés, protéger le stockage média et sauvegarder la base ainsi que les PDF. Le SMS n'est pas actif dans la version actuelle.
