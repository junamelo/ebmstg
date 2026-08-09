/**
 * Notification envoyée pour une facture
 */
public class NotificationFacture {
    
    // Attributs
    private String id;
    private Canal canal;
    private String destinataire;
    private Statut statut;
    
    // Relations
    private Invoice invoice;
}
