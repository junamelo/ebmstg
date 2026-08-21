# Diagramme de séquence - Consulter les factures

```mermaid
sequenceDiagram
    actor U as Payeur ou Employé
    participant I as Interface React <<boundary>>
    participant C as API de facturation Django <<control>>
    participant B as Base PostgreSQL
    participant M as Stockage média PDF

    U->>I: Accéder à « Mes factures »
    I->>C: demanderFactures()
    C->>B: Rechercher les factures PUBLIEE\nautorisées pour l'utilisateur
    B-->>C: Liste des factures

    alt [Aucune facture disponible]
        C-->>I: Liste vide
        I-->>U: Afficher le message d'information
    else [Factures disponibles]
        C-->>I: Factures avec numéro, date, montant et statut
        I-->>U: Afficher les factures et la pagination

        U->>I: Choisir « Aperçu » ou « Télécharger »
        I->>C: demanderPDF(idFacture)
        C->>B: Vérifier les droits et le fichier associé
        B-->>C: Facture autorisée ou erreur

        alt [Accès refusé ou PDF absent]
            C-->>I: 403 ou 404 - Erreur
            I-->>U: Afficher le message d'erreur
        else [PDF disponible et accès autorisé]
            C->>M: Lire le fichier PDF
            M-->>C: Contenu du PDF
            C-->>I: PDF sécurisé encodé

            alt [Aperçu]
                I-->>U: Ouvrir le PDF dans un nouvel onglet
            else [Téléchargement]
                I-->>U: Télécharger le fichier PDF
            end
        end
    end
```

> Le payeur ne consulte que les factures publiées de son entreprise. L'employé ne consulte que les factures sommaires publiées de la ligne qui lui est attribuée. Le contrôle des droits est appliqué à la liste et à l'accès au PDF.
