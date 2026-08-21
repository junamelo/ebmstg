import java.util.ArrayList;
import java.util.List;

public class TraitementPDF {
    private String statut;
    private Integer progression;
    /** @pdRoleInfo name=Utilisateur mult=1 */
    private Utilisateur auteur;
    /** @pdRoleInfo name=Facture coll=java.util.List impl=java.util.ArrayList mult=0..* */
    private final List<Facture> factures = new ArrayList<>();

    public void decouper() {
        statut = "EN_COURS";
    }

}
