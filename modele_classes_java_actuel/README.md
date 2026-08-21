# Modèle de classes Java simplifié

Ce dossier contient l'équivalent Java du diagramme de classes principal de **Moov e-Factures**. Il est destiné au reverse engineering dans PowerDesigner ; il ne constitue pas une seconde implémentation de l'application Django.

Le diagramme avec les cardinalités est disponible dans [DIAGRAMME_CLASSES_MERMAID.mmd](DIAGRAMME_CLASSES_MERMAID.mmd).

Les associations durables sont matérialisées par des références simples (`Contrat`, `Employe`, `Forfait`) ou des collections (`List<Ligne>`, `List<Facture>`, `List<Service>`). Les balises JavaDoc `@pdRoleInfo` indiquent explicitement à PowerAMC les multiplicités (`0..1`, `1`, `0..*`) et le type de relation lorsque nécessaire.

Les classes sont volontairement peu détaillées : seules les informations et opérations principales sont conservées. Aucun package n'est déclaré afin de faciliter l'import dans PowerDesigner.
