/**
 * Historique des modifications de factures
 */
public class HistoriqueFacturation {
    
    // Attributs
    private String id;
    private TypeActionFacturation typeAction;
    private String ancienStatut;
    private String nouveauStatut;
    
    // Relations
    private Invoice invoice;
    private User user;
}
