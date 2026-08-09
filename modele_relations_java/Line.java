import java.util.List;

public class Line {
    // Line (N) -> (1) Contrat
    Contrat contrat;

    // Line (N) -> (0..1) Employe
    Employe employe;

    // Line (1) -> (0..*) LineService
    List<LineService> lineServices;

    // Line (1) -> (0..*) Cycle
    List<Cycle> cycles;

    // Line (0..1) -> (0..*) Invoice
    List<Invoice> factures;
}
