import java.util.ArrayList;
import java.util.List;

public class Publication {
    private String periode;
    private String statut;
    /** @pdRoleInfo name=Utilisateur mult=1 */
    private Utilisateur auteur;
    /** @pdRoleInfo name=Facture coll=java.util.List impl=java.util.ArrayList mult=0..* type=aggregation */
    private final List<Facture> factures = new ArrayList<>();

    public void publier() {
        statut = "PUBLIEE";
    }
}
