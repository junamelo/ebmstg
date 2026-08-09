package com.moov.facturation.facturation;

import com.moov.facturation.utilisateurs.User;

/**
 * Historique des modifications de factures
 */
public class HistoriqueFacturation {
    
    // Attributs
    private String id;
    private TypeActionFacturation typeAction;
    private String ancienStatut;
    private String nouveauStatut;
    
    // Relations
    private Invoice invoice;
    private User utilisateur;
    
    // Getters et Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public TypeActionFacturation getTypeAction() { return typeAction; }
    public void setTypeAction(TypeActionFacturation typeAction) { this.typeAction = typeAction; }
    
    public String getAncienStatut() { return ancienStatut; }
    public void setAncienStatut(String ancienStatut) { this.ancienStatut = ancienStatut; }
    
    public String getNouveauStatut() { return nouveauStatut; }
    public void setNouveauStatut(String nouveauStatut) { this.nouveauStatut = nouveauStatut; }
    
    public Invoice getInvoice() { return invoice; }
    public void setInvoice(Invoice invoice) { this.invoice = invoice; }
    
    public User getUtilisateur() { return utilisateur; }
    public void setUtilisateur(User utilisateur) { this.utilisateur = utilisateur; }
}
