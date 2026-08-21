# Diagramme de séquence - S'authentifier

```mermaid
sequenceDiagram
    actor U as Utilisateur
    participant I as Interface React <<boundary>>
    participant A as API d'authentification Django <<control>>
    participant B as Base PostgreSQL

    U->>I: Accéder à la page de connexion
    I-->>U: Afficher le formulaire
    U->>I: Saisir l'identifiant et le mot de passe
    U->>I: Cliquer sur « Connexion »

    alt [Un champ est vide]
        I-->>U: Afficher « Veuillez remplir tous les champs »
    else [Les champs sont renseignés]
        I->>A: seConnecter(identifiant, motDePasse)
        A->>B: Vérifier le compte, son statut\net le mot de passe haché
        B-->>A: Résultat de la vérification

        alt [Identifiant ou mot de passe incorrect]
            A-->>I: 401 — Identifiants invalides
            I-->>U: Afficher le message d'erreur
        else [Compte inactif ou désactivé]
            A-->>I: 403 — Compte non actif
            I-->>U: Afficher le message et inviter à contacter l'administrateur
        else [Authentification réussie]
            A->>A: Generer les tokens JWT
            A-->>I: 200 — Utilisateur et access token
            I->>I: Enregistrer la session
            I-->>U: Rediriger selon le rôle
        end
    end
```

> L'identifiant peut être un e-mail, un nom d'utilisateur ou un MSISDN enregistré comme nom d'utilisateur. L'interface enregistre l'access token et les informations de l'utilisateur ; le refresh token est bien retourné par l'API mais n'est pas encore exploité par le frontend.
