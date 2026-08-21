import java.math.BigDecimal;

public class Facture {
    private String numero;
    private String type;
    private BigDecimal montantTTC;
    private String statut;
    private String fichierPDF;
    /** @pdRoleInfo name=Contrat mult=1 */
    private Contrat contrat;
    /** @pdRoleInfo name=Ligne mult=0..1 */
    private Ligne ligne;
    /** @pdRoleInfo name=Publication mult=0..1 type=aggregation */
    private Publication publication;
    /** @pdRoleInfo name=TraitementPDF mult=0..1 */
    private TraitementPDF traitementPdf;

    public void consulter() {
        // Consultation de la facture.
    }

    public void telechargerPDF() {
        // Téléchargement du fichier PDF.
    }
}
