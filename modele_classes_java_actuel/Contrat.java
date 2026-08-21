import java.util.ArrayList;
import java.util.List;

public class Contrat {
    private String code;
    private String raisonSociale;
    private String statut;
    /** @pdRoleInfo name=Commercial mult=0..1 */
    private Commercial commercial;
    /** @pdRoleInfo name=Payeur mult=0..1 */
    private Payeur payeur;
    /** @pdRoleInfo name=Ligne coll=java.util.List impl=java.util.ArrayList mult=0..* type=composition */
    private final List<Ligne> lignes = new ArrayList<>();
    /** @pdRoleInfo name=Facture coll=java.util.List impl=java.util.ArrayList mult=0..* */
    private final List<Facture> facturesGlobales = new ArrayList<>();

    public void ajouterLigne() {
        // Ajout d'une ligne au contrat.
    }

    public void resilier(String motif) {
        statut = "RESILIE";
    }
}
