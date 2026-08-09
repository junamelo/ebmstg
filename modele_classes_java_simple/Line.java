import java.util.List;

/**
 * Ligne téléphonique
 */
public class Line {
    
    // Attributs
    private String id;
    private String msisdn;
    private String utilisateur;
    private double forfait;
    private CycleFacturation cycle;
    private String statut;
    
    // Relations
    private Company company;
    private User employe;
    private List<Invoice> invoices;
    private List<Cycle> cycles;
}
