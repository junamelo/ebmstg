# Modèle Java pour PowerDesigner

Ce dossier contient une conversion du diagramme de classes en Java avec relations explicites.

## Objectif
- Permettre un import/reverse engineering dans PowerDesigner.
- Faire ressortir les cardinalités via les annotations JPA.

## Convention utilisée
- `@ManyToOne` = côté N vers 1
- `@OneToMany` = côté 1 vers N
- `@OneToOne` = 1 vers 1
- `@ManyToMany` = N vers N
- `optional = false` pour marquer une relation obligatoire (cardinalité min = 1)

## Remarque
Ces classes servent d'abord de modèle UML exploitable. Elles ne sont pas branchées automatiquement sur le backend Django existant.