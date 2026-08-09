import java.util.Date;

/**
 * Publication de factures par un agent
 */
public class Publication {
    
    // Attributs
    private String id;
    private String cycleFacturation;
    private Date periodeDebut;
    private Date periodeFin;
    private int nombreLignesTraitees;
    private double montantTotal;
    
    // Relations
    private User agent;
}
