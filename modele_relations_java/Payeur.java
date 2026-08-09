import java.util.List;

public class Payeur extends Utilisateur {
    // Payeur (1) -> (0..*) Contrat
    List<Contrat> contrats;
}
