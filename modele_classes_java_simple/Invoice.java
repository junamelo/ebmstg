import java.util.Date;
import java.util.List;

/**
 * Facture client
 */
public class Invoice {
    
    // Attributs
    private String id;
    private String numeroFacture;
    private Date periodeDebut;
    private Date periodeFin;
    private double montantTtc;
    private StatutFacture statut;
    private String fichierPdf;
    
    // Relations
    private Company company;
    private Line line;
    private List<NotificationFacture> notifications;
    private List<HistoriqueFacturation> historique;
    
    // Méthodes
    public void publier() {
        this.statut = StatutFacture.PUBLIEE;
    }
    
    public void annuler() {
        this.statut = StatutFacture.ANNULEE;
    }
}
