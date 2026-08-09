# Cardinalités principales modélisées

- `Role (1) -> (0..*) Utilisateur`
- `Utilisateur (1) -> (0..*) Notification`
- `Utilisateur (1) -> (0..*) SessionUtilisateur`
- `Utilisateur (1) -> (0..*) PasswordReset`
- `Utilisateur (1) -> (0..*) Simulation`

- `Payeur (1) -> (0..*) Contrat`
- `Commercial (1) -> (0..*) Contrat`
- `CategorieClient (1) -> (0..*) Contrat`
- `TypeFacture (1) -> (0..*) Contrat`

- `Contrat (1) -> (0..*) Line`
- `Employe (1) -> (0..*) Line` (optionnel côté ligne)
- `Package (1) -> (0..*) Line` (optionnel côté ligne)

- `Contrat (1) -> (0..*) Invoice`
- `Line (0..1) -> (0..*) Invoice`
- `TypeFacture (1) -> (0..*) Invoice`

- `Invoice (1) -> (0..*) HistoriqueFacturation`
- `AgentFacturation (1) -> (0..*) HistoriqueFacturation`

- `Line (1) -> (0..*) LineService`
- `Service (1) -> (0..*) LineService`

- `Line (1) -> (0..*) Cycle`
- `Service (1) -> (0..*) Cycle`
