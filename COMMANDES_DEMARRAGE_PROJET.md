# Commandes de démarrage — Moov e-Factures

Ce guide permet de démarrer l'application locale. Ouvrir **cinq terminaux PowerShell** : PostgreSQL, Garnet, Django, Celery et React/Vite. Laisser les terminaux ouverts pendant l'utilisation du portail.

> Les mots de passe restent uniquement dans le fichier `.env`, à la racine du projet. Ne pas les recopier dans ce document ni dans Git.

## 0. Se placer à la racine du projet

Dans chaque nouveau terminal :

```powershell
Set-Location "C:\Users\Benoit\Documents\BURRO\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026"
```

## 1. Démarrer ou vérifier PostgreSQL

PostgreSQL est installé localement et utilise le port défini dans `.env` (actuellement `5433`). Vérifier son état :

```powershell
Get-Service | Where-Object { $_.Name -like '*postgres*' }
```

Si le service PostgreSQL 16 est arrêté, le démarrer (adapter le nom s'il est différent dans la commande précédente) :

```powershell
Start-Service -Name 'postgresql-x64-16'
```

Vérifier ensuite que le port répond :

```powershell
Test-NetConnection 127.0.0.1 -Port 5433
```

Le résultat attendu est `TcpTestSucceeded : True`.

## 2. Démarrer Garnet (compatible Redis)

Dans un deuxième terminal, lancer Garnet sur le port `6379`. Remplacer le texte entre chevrons par le mot de passe Redis présent dans `.env` ; ne pas laisser les chevrons :

```powershell
Set-Location "C:\Users\Benoit\Documents\garnet\garnet"
$projectRoot = "C:\Users\Benoit\Documents\BURRO\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026"
$redisUrl = ((Get-Content "$projectRoot\.env" | Where-Object { $_ -match '^REDIS_URL=' }) -replace '^REDIS_URL=', '')
$encodedPassword = (([uri]$redisUrl).UserInfo -replace '^:', '')
$env:GARNET_PASSWORD = [uri]::UnescapeDataString($encodedPassword)
.\main\GarnetServer\bin\Release\net10.0\GarnetServer.exe --bind 127.0.0.1 --port 6379 --auth Password --password $env:GARNET_PASSWORD --lua
```

Dans un autre terminal, cette vérification doit retourner `True` :

```powershell
Test-NetConnection 127.0.0.1 -Port 6379
```

> Si le chemin de `GarnetServer.exe` est différent après une nouvelle compilation, rechercher le fichier avec : `Get-ChildItem -Recurse -Filter GarnetServer.exe` depuis le dossier `garnet`.

## 3. Préparer le backend (seulement au premier démarrage ou après une mise à jour)

Dans un troisième terminal :

```powershell
Set-Location "C:\Users\Benoit\Documents\BURRO\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026\Back"

# À exécuter seulement si un environnement virtuel existe dans Back\.venv
.\.venv\Scripts\Activate.ps1

# À exécuter au premier démarrage ou après une modification des dépendances
python -m pip install -r requirements_postgres.txt
python -m pip install -r requirements_pdf.txt
python -m pip install -r requirements_async.txt
python -m pip install -r requirements_2fa.txt

# À exécuter après une nouvelle migration ou avant le premier lancement
python manage.py migrate
python manage.py check
```

Si aucun dossier `Back\.venv` n'existe, ne pas exécuter la ligne d'activation : utiliser l'installation Python avec laquelle les dépendances du projet ont été installées.

## 4. Démarrer le backend Django

Toujours dans le dossier `Back`, lancer :

```powershell
python manage.py runserver 8000
```

Le serveur doit indiquer qu'il écoute sur `http://127.0.0.1:8000/`. Vérifier rapidement l'API :

```powershell
Invoke-WebRequest http://127.0.0.1:8000/api/ -UseBasicParsing
```

## 5. Démarrer le worker Celery

Dans un quatrième terminal :

```powershell
Set-Location "C:\Users\Benoit\Documents\BURRO\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026\Back"

# À exécuter seulement si l'environnement virtuel Back\.venv existe
.\.venv\Scripts\Activate.ps1

python -m celery -A moov_backend worker -l INFO -P solo
```

Le message attendu est semblable à :

```text
Connected to redis://...@127.0.0.1:6379/1
celery@... ready.
```

Ce terminal est indispensable pour le découpage et la publication des blocs PDF. Une fois Celery démarré, un traitement peut continuer même si l'utilisateur quitte la page de publication.

## 6. Démarrer le frontend React

Dans un cinquième terminal :

```powershell
Set-Location "C:\Users\Benoit\Documents\BURRO\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026\Front"

# À exécuter seulement au premier démarrage ou après une modification des dépendances
npm install

npm run dev
```

Ouvrir ensuite : [http://localhost:3000](http://localhost:3000)

## Ordre de démarrage quotidien

1. Vérifier/démarrer PostgreSQL.
2. Démarrer Garnet.
3. Démarrer Django.
4. Démarrer le worker Celery.
5. Démarrer React/Vite.
6. Ouvrir `http://localhost:3000`.

## Après une modification du code

- Une modification backend Django est généralement rechargée automatiquement. En cas de doute, arrêter Django avec `Ctrl+C` et relancer la commande de l'étape 4.
- Après une modification de `tasks.py`, `settings.py` ou du traitement PDF, arrêter puis relancer **Celery** avec `Ctrl+C`, puis la commande de l'étape 5.
- Vite recharge le frontend automatiquement. Si une nouvelle dépendance ou une configuration Vite a changé, arrêter puis relancer l'étape 6.
- Après une modification de modèle Django :

```powershell
Set-Location "C:\Users\Benoit\Documents\BURRO\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026\Back"
python manage.py makemigrations
python manage.py migrate
```

## Vérifications utiles

Depuis `Back` :

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
```

Depuis `Front` :

```powershell
npm run build
npm run lint
```

## Arrêter l'application

Dans les terminaux Django, Celery, Vite et Garnet, appuyer sur :

```text
Ctrl + C
```

PostgreSQL peut rester démarré : il est utilisé comme service Windows. Pour l'arrêter explicitement :

```powershell
Stop-Service -Name 'postgresql-x64-16'
```

Ne pas arrêter PostgreSQL pendant qu'un découpage PDF est en cours.
