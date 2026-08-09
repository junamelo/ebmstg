import java.util.List;

public class AgentFacturation extends Utilisateur {
    // AgentFacturation (1) -> (0..*) HistoriqueFacturation
    List<HistoriqueFacturation> historiquesFacturation;
}
