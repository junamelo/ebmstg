import java.util.ArrayList;
import java.util.List;

public abstract class Utilisateur {
    protected String nom;
    protected String email;
    protected String role;

    /** @pdRoleInfo name=Simulation coll=java.util.List impl=java.util.ArrayList mult=0..* */
    protected final List<Simulation> simulations = new ArrayList<>();

    public void seConnecter() {
        // Authentification de l'utilisateur.
    }
}
