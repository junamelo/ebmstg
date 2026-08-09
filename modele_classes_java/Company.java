package com.moov.facturation.contrats;

import com.moov.facturation.utilisateurs.User;
import com.moov.facturation.facturation.Invoice;
import java.util.List;

/**
 * Contrat entreprise client
 */
public class Company {
    
    // Attributs
    private String id;
    private String compte; // unique
    private String raisonSociale;
    private CategorieClient categorie;
    private StatutFacturation statutFactures;
    private ModeReglement modeReglement;
    private boolean estResilie;
    
    // Relations
    private Commercial commercial;
    private User payeur;
    private List<Line> lines;
    private List<Invoice> invoices;
    private List<AuditContrat> auditContrats;
    
    // Méthodes
    public void resilier() {
        this.estResilie = true;
    }
    
    // Getters et Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getCompte() { return compte; }
    public void setCompte(String compte) { this.compte = compte; }
    
    public String getRaisonSociale() { return raisonSociale; }
    public void setRaisonSociale(String raisonSociale) { this.raisonSociale = raisonSociale; }
    
    public CategorieClient getCategorie() { return categorie; }
    public void setCategorie(CategorieClient categorie) { this.categorie = categorie; }
    
    public StatutFacturation getStatutFactures() { return statutFactures; }
    public void setStatutFactures(StatutFacturation statutFactures) { this.statutFactures = statutFactures; }
    
    public ModeReglement getModeReglement() { return modeReglement; }
    public void setModeReglement(ModeReglement modeReglement) { this.modeReglement = modeReglement; }
    
    public boolean isEstResilie() { return estResilie; }
    public void setEstResilie(boolean estResilie) { this.estResilie = estResilie; }
}
