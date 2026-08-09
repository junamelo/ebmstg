import java.util.List;

public class Invoice {
    // Invoice (N) -> (1) Contrat
    Contrat contrat;

    // Invoice (N) -> (0..1) Line
    Line line;

    // Invoice (N) -> (0..1) TypeFacture
    TypeFacture typeFacture;

    // Invoice (1) -> (0..*) HistoriqueFacturation
    List<HistoriqueFacturation> historiques;
}
