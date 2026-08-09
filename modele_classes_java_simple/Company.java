import java.util.List;

/**
 * Contrat entreprise client
 */
public class Company {
    
    // Attributs
    private String id;
    private String compte;
    private String raisonSociale;
    private CategorieClient categorie;
    private StatutFacturation statutFactures;
    private ModeReglement modeReglement;
    private boolean estResilie;
    
    // Relations
    private Commercial commercial;
    private User payeur;
    private List<Line> lines;
    private List<Invoice> invoices;
    private List<AuditContrat> auditContrats;
    
    // Méthodes
    public void resilier() {
        this.estResilie = true;
    }
}
