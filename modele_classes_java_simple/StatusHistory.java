import java.util.Date;

/**
 * Historique des changements de statut
 */
public class StatusHistory {
    
    // Attributs
    private String id;
    private String oldStatus;
    private String newStatus;
    private Date changedAt;
    
    // Relations
    private User user;
}
