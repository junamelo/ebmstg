package com.moov.facturation.contrats;

import com.moov.facturation.utilisateurs.User;
import com.moov.facturation.facturation.Invoice;
import com.moov.facturation.catalogue.Cycle;
import java.util.List;

/**
 * Ligne téléphonique d'un contrat
 */
public class Line {
    
    // Attributs
    private String id;
    private String msisdn; // unique - numéro téléphone
    private String utilisateur;
    private double forfait;
    private CycleFacturation cycle;
    private String statut;
    
    // Relations
    private Company company;
    private User employe;
    private List<Invoice> invoices;
    private List<Cycle> cycles;
    
    // Getters et Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getMsisdn() { return msisdn; }
    public void setMsisdn(String msisdn) { this.msisdn = msisdn; }
    
    public String getUtilisateur() { return utilisateur; }
    public void setUtilisateur(String utilisateur) { this.utilisateur = utilisateur; }
    
    public double getForfait() { return forfait; }
    public void setForfait(double forfait) { this.forfait = forfait; }
    
    public CycleFacturation getCycle() { return cycle; }
    public void setCycle(CycleFacturation cycle) { this.cycle = cycle; }
    
    public String getStatut() { return statut; }
    public void setStatut(String statut) { this.statut = statut; }
}
