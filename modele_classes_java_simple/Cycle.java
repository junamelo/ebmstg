import java.util.Date;

/**
 * Cycle d'activation d'un service sur une ligne
 */
public class Cycle {
    
    // Attributs
    private String id;
    private Date dateDebut;
    private Date dateFin;
    
    // Relations
    private Line line;
    private Service service;
}
