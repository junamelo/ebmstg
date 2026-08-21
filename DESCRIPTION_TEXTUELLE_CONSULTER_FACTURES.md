# Description textuelle du cas d'utilisation « Consulter les factures »

## Identification

| Élément | Description |
|---|---|
| **Titre** | Consulter les factures |
| **Acteurs principaux** | Payeur et Employé |
| **Acteur secondaire** | Agent de facturation, pour les contrôles et la consultation des factures selon ses droits |
| **Résumé** | Ce cas d'utilisation décrit la consultation des factures publiées dans le portail Moov e-Factures. Le payeur consulte les factures globales de ses contrats et les factures sommaires de ses lignes ; l'employé consulte uniquement la facture sommaire publiée correspondant à sa ligne. |
| **Version** | 1.0 |
| **Date de création** | 12/08/2026 |
| **Date de modification** | 12/08/2026 |

## Préconditions

- L'utilisateur est authentifié et son compte est actif.
- Le payeur est rattaché à un ou plusieurs contrats, ou l'employé est rattaché à une ligne téléphonique.
- Une facture publiée correspondant au périmètre de l'utilisateur existe.
- Le fichier PDF est disponible lorsque l'utilisateur demande son ouverture ou son téléchargement.

## Scénario nominal

1. L'utilisateur ouvre la page « Mes factures ».
2. Le système identifie son rôle et son périmètre d'accès.
3. Le système charge uniquement les factures auxquelles l'utilisateur est autorisé à accéder.
4. Le payeur voit les factures globales de ses contrats et les factures sommaires de ses lignes.
5. L'employé voit les factures sommaires publiées de sa ligne.
6. Le système affiche, pour chaque facture, son numéro réel, sa date d'émission, sa période, son type, son montant et son statut.
7. L'utilisateur peut parcourir la liste à l'aide de la pagination et utiliser les filtres disponibles.
8. L'utilisateur sélectionne une facture.
9. Le système vérifie une nouvelle fois que la facture appartient au périmètre de l'utilisateur.
10. Le système affiche le détail de la facture avec les informations enregistrées en base et issues du PDF associé.
11. L'utilisateur choisit « Aperçu » pour ouvrir le PDF dans un nouvel onglet ou « Télécharger » pour l'enregistrer.
12. Le système fournit le fichier PDF uniquement si celui-ci est attaché et que l'autorisation est valide.

## Scénarios alternatifs

### A1. Aucun résultat

Ce scénario commence au point 3 du scénario nominal, lorsque le système charge la liste des factures autorisées.

1. Aucune facture publiée ne correspond au rôle, au contrat ou à la ligne de l'utilisateur.
2. Le système affiche un message indiquant qu'aucune facture n'est disponible.
3. Le cas d'utilisation se termine sans téléchargement.

### A2. Filtrage de la liste

Ce scénario commence au point 7 du scénario nominal, lorsque l'utilisateur parcourt la liste et choisit un filtre. Après l'actualisation, le scénario reprend au point 7.

1. L'utilisateur sélectionne une période, un type de facture ou un statut.
2. Le système actualise la liste sans afficher de facture située hors de son périmètre.
3. L'utilisateur peut retirer le filtre et revenir à la liste complète autorisée.

### A3. Facture sans PDF attaché

Ce scénario commence au point 11 du scénario nominal, lorsque l'utilisateur demande l'aperçu ou le téléchargement. Le contrôle du fichier est effectué au point 12.

1. La facture est visible dans la liste, mais aucun fichier PDF n'est associé.
2. Le système affiche l'information « PDF manquant ».
3. Les actions d'aperçu et de téléchargement sont désactivées ou refusées.

### A4. PDF ouvert dans un nouvel onglet

Ce scénario commence au point 11 du scénario nominal, lorsque l'utilisateur choisit « Aperçu ». Après l'ouverture du document, le cas d'utilisation se termine ; le téléchargement reste une action distincte.

1. L'utilisateur clique sur « Aperçu ».
2. Le système vérifie l'accès puis ouvre directement le PDF dans un nouvel onglet du navigateur.
3. Le téléchargement n'est lancé que si l'utilisateur choisit explicitement « Télécharger ».

### A5. Facture globale du payeur

Ce scénario commence au point 4 du scénario nominal pour le payeur. Après le choix d'une facture globale au point 8, le déroulement reprend au point 9 pour la vérification de l'accès.

1. Le payeur sélectionne une facture globale.
2. Le système affiche le montant et les informations correspondant à l'ensemble du contrat concerné.
3. Les factures sommaires des lignes restent consultables séparément.

## Scénarios d'exceptions

### E1. Session expirée

Cette exception commence au point 3 du scénario nominal, lors de la première requête protégée de chargement des factures.

Le système refuse la requête et demande à l'utilisateur de se reconnecter. Aucune donnée de facture n'est affichée.

### E2. Accès non autorisé

Cette exception commence au point 9 du scénario nominal, lorsque le système vérifie que la facture sélectionnée appartient au périmètre de l'utilisateur.

Si l'utilisateur tente d'accéder à une facture d'un autre contrat ou d'une autre ligne, le système refuse l'accès et ne révèle pas le contenu du PDF.

### E3. Erreur de chargement

Cette exception commence au point 3 du scénario nominal lorsque le serveur ou la base de données ne répond pas. Elle peut aussi apparaître aux points 9 ou 10 lors de la vérification ou de l'affichage du détail.

Si le serveur, la base de données ou le stockage média est indisponible, le système affiche un message d'erreur et l'utilisateur peut réessayer ultérieurement.

### E4. PDF introuvable

Cette exception commence au point 12 du scénario nominal, lorsque le système doit fournir le fichier PDF.

Si le fichier a été supprimé ou déplacé, le système conserve la facture dans l'historique mais signale que le document n'est momentanément pas accessible.

## Postconditions

- L'utilisateur a consulté uniquement les factures correspondant à ses droits.
- La facture reste enregistrée dans la base avec ses informations réelles.
- Le PDF est ouvert ou téléchargé uniquement lorsqu'il est disponible et que l'autorisation est valide.
- Une éventuelle erreur est affichée sans exposer les données d'une autre entreprise ou d'une autre ligne.

## Règles d'accès

| Rôle | Factures consultables |
|---|---|
| **Payeur** | Factures globales de ses contrats et factures sommaires des lignes rattachées à ces contrats. |
| **Employé** | Factures sommaires publiées de la ligne qui lui est affectée. |
| **Agent de facturation** | Factures disponibles dans le périmètre de gestion prévu par ses permissions, notamment pour le suivi et le contrôle de la publication. |
