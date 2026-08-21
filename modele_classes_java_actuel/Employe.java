import java.util.ArrayList;
import java.util.List;

public class Employe extends Utilisateur {
    private String msisdn;
    /** @pdRoleInfo name=Ligne coll=java.util.List impl=java.util.ArrayList mult=0..* */
    private final List<Ligne> lignes = new ArrayList<>();

    public void consulterFactureSommaire() {
        // Consultation de la facture sommaire de la ligne.
    }
}
