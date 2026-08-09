

import java.util.List;

/**
 * Commercial Moov Africa
 */
public class Commercial {
    
    // Attributs
    private String id;
    private String nom;
    private String prenom;
    private String matricule; // unique
    
    // Relations
    private List<Company> companies;
    
    // Getters et Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getNom() { return nom; }
    public void setNom(String nom) { this.nom = nom; }
    
    public String getPrenom() { return prenom; }
    public void setPrenom(String prenom) { this.prenom = prenom; }
    
    public String getMatricule() { return matricule; }
    public void setMatricule(String matricule) { this.matricule = matricule; }
    
    public List<Company> getCompanies() { return companies; }
    public void setCompanies(List<Company> companies) { this.companies = companies; }
}
