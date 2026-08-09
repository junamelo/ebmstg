import java.util.Date;

/**
 * Audit des actions sur contrats
 */
public class AuditContrat {
    
    // Attributs
    private String id;
    private TypeAction typeAction;
    private Date dateAction;
    
    // Relations
    private Company company;
    private User user;
}
