import java.util.ArrayList;
import java.util.List;

public class ChefFacturation extends Utilisateur {
    /** @pdRoleInfo name=DemandeContrat coll=java.util.List impl=java.util.ArrayList mult=0..* */
    private final List<DemandeContrat> demandesTraitees = new ArrayList<>();

    public void traiterDemande() {
        // Validation ou rejet d'une demande de contrat.
    }
}
