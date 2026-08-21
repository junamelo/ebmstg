import java.util.ArrayList;
import java.util.List;

public class Commercial extends Utilisateur {
    private String matricule;

    /** @pdRoleInfo name=DemandeContrat coll=java.util.List impl=java.util.ArrayList mult=0..* */
    private final List<DemandeContrat> demandes = new ArrayList<>();

    /** @pdRoleInfo name=Contrat coll=java.util.List impl=java.util.ArrayList mult=0..* */
    private final List<Contrat> contrats = new ArrayList<>();

    public void soumettreDemande() {
        // Soumission d'une demande de contrat.
    }
}
