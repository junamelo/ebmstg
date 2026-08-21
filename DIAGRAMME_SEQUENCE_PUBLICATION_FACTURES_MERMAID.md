# Diagramme de séquence - Publier les factures

```mermaid
sequenceDiagram
    actor A as Agent de facturation
    participant I as Interface React <<boundary>>
    participant C as API de facturation Django <<control>>
    participant B as Base PostgreSQL
    participant W as Worker Celery

    A->>I: Accéder à « Factures à publier »
    I->>C: demanderFacturesValidees()
    C->>B: Rechercher les factures au statut VALIDEE
    B-->>C: Liste des factures prêtes
    C-->>I: Afficher la liste et les montants

    A->>I: Sélectionner une ou plusieurs factures
    A->>I: Confirmer « Publier la sélection »
    I->>C: publierMasse(idsFactures, canauxNotification)
    C->>B: Vérifier statuts, PDF, période et cycle
    B-->>C: Résultat des vérifications

    alt [Sélection invalide]
        C-->>I: 400 - Publication refusée
        I-->>A: Afficher les raisons du refus
    else [Sélection valide]
        loop [Pour chaque facture sélectionnée]
            C->>B: Passer VALIDEE à PUBLIEE\net enregistrer l'historique
        end
        C->>B: Créer ou mettre à jour la publication

        opt [Notification e-mail demandée]
            C-)W: Planifier l'envoi des e-mails
        end

        C-->>I: 200 - Publication réussie
        I-->>A: Afficher la confirmation et actualiser la liste
    end
```

> Seules les factures au statut `VALIDEE`, disposant d'un PDF et appartenant à la même période et au même cycle peuvent être publiées ensemble. L'envoi éventuel d'e-mails est asynchrone et son échec n'annule pas la publication.
