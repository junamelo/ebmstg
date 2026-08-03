# Demarrage du portail Moov Africa e-Billing

## Prerequis

- Python et les dependances de `Back/requirements.txt`
- Node.js et npm

## Lancement local

1. Dans `Back` : executer `python manage.py migrate`, puis `python manage.py runserver`.
2. Dans `Front` : executer `npm install`, puis `npm run dev`.
3. Ouvrir l'URL Vite affichee (habituellement `http://localhost:3000`).

## Donnees de demonstration PDF

Les PDF SOM et GLO ne sont pas versionnes. Les commandes suivantes ne doivent etre utilisees qu'avec les fichiers de test fournis localement :

- `python manage.py prepare_som_pdf_test_data --reset`
- `python manage.py prepare_glo_pdf_test_data`

Importer ensuite les PDF avec le cycle `OP` et la periode du 01/06/2026 au 30/06/2026.

## Verification avant livraison

- Backend : `python manage.py check`, `python manage.py test`, `python manage.py makemigrations --check --dry-run`.
- Frontend : `npm run lint`, `npm run build`.

## Limites connues

- Pas d'OCR : les PDF doivent contenir du texte exploitable.
- Le traitement PDF est synchrone ; les tres gros fichiers peuvent prendre du temps.
- Le stockage media local doit etre remplace par un stockage securise en production.
- L'envoi d'e-mails et la gestion obligatoire du changement de mot de passe ne sont pas configures.
- Avant toute mise en production, renseigner les valeurs reelles de `.env` et corriger les avertissements de `check --deploy` relatifs a HTTPS, HSTS, cookies et `DEBUG`.
