import java.util.List;

/**
 * Service optionnel
 */
public class Service {
    
    // Attributs
    private String id;
    private String nom;
    private String code;
    private TypeService typeService;
    
    // Relations
    private List<TarifService> tarifs;
    private List<Cycle> cycles;
}
