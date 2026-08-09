import java.util.List;

public class TypeFacture {
    // TypeFacture (1) -> (0..*) Contrat
    List<Contrat> contrats;

    // TypeFacture (1) -> (0..*) Invoice
    List<Invoice> invoices;
}
