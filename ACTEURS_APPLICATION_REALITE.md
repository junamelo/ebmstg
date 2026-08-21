# Les acteurs du système Moov e-Factures

## Définition

Un acteur représente un rôle joué par une entité externe qui interagit avec le système étudié. Dans Moov e-Factures, les acteurs principaux sont les utilisateurs humains de la plateforme. Chaque acteur possède un niveau de responsabilité et un périmètre d'accès propres. Les autorisations sont contrôlées par le rôle de l'utilisateur, l'état de son compte et, pour les clients, son rattachement à un contrat ou à une ligne téléphonique.

## Les acteurs principaux

### Le Super Administrateur

Le super administrateur est responsable de l'administration globale de la plateforme. Il veille à la cohérence générale des comptes, des rôles, des statuts, des entreprises, des contrats, des lignes, des forfaits et des services. Il possède une vision complète des données et des historiques et peut intervenir sur la configuration générale du système. Il constitue le niveau d'administration le plus élevé, mais la publication courante des factures reste une responsabilité opérationnelle du chef ou de l'agent de facturation.

### Le Chef de facturation

Le chef de facturation est responsable de la supervision de l'activité de facturation. Il encadre les agents de son périmètre, contrôle les demandes provenant des commerciaux et s'assure que les contrats sont correctement validés avant leur exploitation. Il supervise également les tarifs, les services, les publications et les rapports de traitement. En cas de rejet d'une demande, il justifie sa décision par un motif qui doit pouvoir être consulté par le commercial concerné.

### L'Agent de facturation

L'agent de facturation est l'opérateur chargé de l'exécution quotidienne des opérations de facturation. Il assure la préparation et la fiabilité des données de référence, notamment les contrats, les lignes, les forfaits et les services. Il prend en charge les blocs PDF reçus, leur découpage, le rapprochement avec les comptes, les numéros de facture et les MSISDN, puis la publication des documents correctement associés. Il contrôle les rapports, identifie les erreurs et suit l'historique des traitements. Selon ses permissions, il peut également examiner et traiter les demandes de contrat.

### Le Commercial

Le commercial représente l'interlocuteur chargé de proposer et de suivre les contrats avec les clients. Il renseigne les informations nécessaires à la constitution d'une demande et reste responsable du suivi de cette demande dans la plateforme. Il ne représente pas l'autorité de validation : une demande soumise par un commercial reste en attente jusqu'à la décision d'un utilisateur habilité. Le commercial est informé de l'acceptation ou du rejet et peut prendre connaissance du motif communiqué en cas de décision défavorable.

### Le Payeur

Le payeur représente le responsable de l'entreprise cliente, généralement chargé du suivi administratif et financier du contrat. Son périmètre est limité à l'entreprise et aux lignes qui lui sont rattachées. Il dispose d'une vision globale de la facturation de sa flotte et peut accéder aux documents publiés correspondant à son contrat, notamment la facture globale et les factures sommaires associées aux lignes. Il peut également consulter ses services, effectuer des simulations et suivre son historique. Dans l'application, son identifiant est l'e-mail ou le nom d'utilisateur configuré pour son compte ; le numéro de contrat ne sert d'identifiant que s'il a été enregistré comme nom d'utilisateur.

### L'Employé

L'employé représente l'utilisateur final d'une ligne téléphonique de l'entreprise. Son périmètre est volontairement restreint à la ligne qui lui est attribuée. Il consulte les informations de cette ligne, les services qui lui sont associés et les factures sommaires publiées qui correspondent à son MSISDN. Il peut aussi réaliser une simulation individuelle et gérer les éléments autorisés de son profil. Il ne possède aucun droit de gestion sur les contrats, les autres lignes ou les données globales de l'entreprise. Son compte se connecte avec l'e-mail ou le nom d'utilisateur enregistré ; dans les données de test, ce nom d'utilisateur peut correspondre au MSISDN.

## Composants techniques hors acteurs métier

Celery, Garnet, PostgreSQL et le service SMTP sont des composants techniques de l'architecture et non des acteurs métier. Ils soutiennent respectivement l'exécution des traitements longs, le transport des tâches et le cache, la conservation des données et l'envoi éventuel d'e-mails. Ils ne représentent donc pas des rôles joués par les utilisateurs dans le diagramme des acteurs principaux.

## Synthèse des rôles

| Acteur | Rôle dans le système |
|---|---|
| Super administrateur | Administration globale et cohérence de la plateforme |
| Chef de facturation | Supervision de la facturation et contrôle des décisions |
| Agent de facturation | Exécution opérationnelle et publication des factures |
| Commercial | Relation commerciale et suivi des demandes de contrat |
| Payeur | Suivi de la facturation de son entreprise |
| Employé | Consultation de sa ligne et de sa facturation individuelle |

