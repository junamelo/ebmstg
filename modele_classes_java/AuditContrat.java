package com.moov.facturation.contrats;

import com.moov.facturation.utilisateurs.User;
import java.util.Date;

/**
 * Audit des actions sur les contrats
 */
public class AuditContrat {
    
    // Attributs
    private String id;
    private TypeAction typeAction;
    private Date dateAction;
    
    // Relations
    private Company company;
    private User utilisateur;
    
    // Getters et Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public TypeAction getTypeAction() { return typeAction; }
    public void setTypeAction(TypeAction typeAction) { this.typeAction = typeAction; }
    
    public Date getDateAction() { return dateAction; }
    public void setDateAction(Date dateAction) { this.dateAction = dateAction; }
    
    public Company getCompany() { return company; }
    public void setCompany(Company company) { this.company = company; }
    
    public User getUtilisateur() { return utilisateur; }
    public void setUtilisateur(User utilisateur) { this.utilisateur = utilisateur; }
}
