import java.util.ArrayList;
import java.util.List;

public class Ligne {
    private String msisdn;
    private String statut;
    /** @pdRoleInfo name=Contrat mult=1 type=composition */
    private Contrat contrat;
    /** @pdRoleInfo name=Employe mult=0..1 */
    private Employe employe;
    /** @pdRoleInfo name=Forfait mult=0..1 */
    private Forfait forfait;
    /** @pdRoleInfo name=Service coll=java.util.List impl=java.util.ArrayList mult=0..* */
    private final List<Service> services = new ArrayList<>();
    /** @pdRoleInfo name=Facture coll=java.util.List impl=java.util.ArrayList mult=0..* */
    private final List<Facture> factures = new ArrayList<>();

    public void affecterEmploye() {
        // Affectation d'un employe a la ligne.
    }

    public void modifierServices() {
        // Gestion des services de la ligne.
    }
}
