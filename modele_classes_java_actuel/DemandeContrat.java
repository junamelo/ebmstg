public class DemandeContrat {
    private String statut;
    private String motifRejet;
    /** @pdRoleInfo name=Commercial mult=1 */
    private Commercial commercial;
    /** @pdRoleInfo name=ChefFacturation mult=0..1 */
    private ChefFacturation decideur;
    /** @pdRoleInfo name=Contrat mult=0..1 */
    private Contrat contrat;

    public void soumettre() {
        statut = "EN_ATTENTE";
    }

    public void rejeter(String motif) {
        statut = "REJETEE";
        motifRejet = motif;
    }
}
