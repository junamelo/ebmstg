import java.util.List;
import java.util.Date;

/**
 * Utilisateur du système (Admin, Chef, Agent, Payeur, Employé)
 */
public class User {
    
    // Attributs
    private String id;
    private String email;
    private String firstName;
    private String lastName;
    private RoleChoices role;
    private StatusChoices status;
    private String telephone;
    
    // Relations
    private User createdBy;
    private User statusChangedBy;
    private List<StatusHistory> historique;
    private List<Company> companiesPayeur;
    private List<Line> linesEmploye;
    private List<AuditContrat> auditsEffectues;
    private List<HistoriqueFacturation> historiquesEffectues;
    private List<Publication> publicationsEffectuees;
    
    // Méthodes
    public boolean hasPermission(String permission) {
        return true;
    }
    
    public boolean canManageUser(User targetUser) {
        return true;
    }
}
