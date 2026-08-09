import java.util.List;

public abstract class Utilisateur {
    // Utilisateur (N) -> (1) Role
    Role role;

    // Utilisateur (1) -> (0..*) Notification
    List<Notification> notifications;

    // Utilisateur (1) -> (0..*) SessionUtilisateur
    List<SessionUtilisateur> sessions;

    // Utilisateur (1) -> (0..*) PasswordReset
    List<PasswordReset> passwordResets;

    // Utilisateur (1) -> (0..*) Simulation
    List<Simulation> simulations;
}
