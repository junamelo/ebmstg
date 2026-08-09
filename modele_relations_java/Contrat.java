import java.util.List;

public class Contrat {
    // Contrat (N) -> (1) CategorieClient
    CategorieClient categorieClient;

    // Contrat (N) -> (0..1) Payeur
    Payeur payeur;

    // Contrat (N) -> (0..1) Commercial
    Commercial commercial;

    // Contrat (N) -> (0..1) TypeFacture
    TypeFacture typeFacture;

    // Contrat (1) -> (0..*) Line
    List<Line> lignes;

    // Contrat (1) -> (0..*) Invoice
    List<Invoice> factures;
}
