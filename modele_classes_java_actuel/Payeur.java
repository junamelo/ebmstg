import java.util.ArrayList;
import java.util.List;

public class Payeur extends Utilisateur {
    /** @pdRoleInfo name=Contrat coll=java.util.List impl=java.util.ArrayList mult=0..* */
    private final List<Contrat> contrats = new ArrayList<>();

    public void consulterFactures() {
        // Consultation des factures globales.
    }
}
