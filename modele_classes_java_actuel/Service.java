import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

public class Service {
    private String nom;
    private String type;
    private BigDecimal prix;
    /** @pdRoleInfo name=Ligne coll=java.util.List impl=java.util.ArrayList mult=0..* */
    private final List<Ligne> lignes = new ArrayList<>();

    public void modifierTarif() {
        // Modification du tarif du service.
    }
}
