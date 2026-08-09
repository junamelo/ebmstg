package com.moov.facturation.facturation;

import com.moov.facturation.utilisateurs.User;
import java.util.Date;

/**
 * Publication de factures par un agent
 */
public class Publication {
    
    // Attributs
    private String id;
    private String cycleFacturation;
    private Date periodeDebut;
    private Date periodeFin;
    private int nombreLignesTraitees;
    private double montantTotal;
    
    // Relations
    private User agent;
    
    // Getters et Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getCycleFacturation() { return cycleFacturation; }
    public void setCycleFacturation(String cycleFacturation) { this.cycleFacturation = cycleFacturation; }
    
    public Date getPeriodeDebut() { return periodeDebut; }
    public void setPeriodeDebut(Date periodeDebut) { this.periodeDebut = periodeDebut; }
    
    public Date getPeriodeFin() { return periodeFin; }
    public void setPeriodeFin(Date periodeFin) { this.periodeFin = periodeFin; }
    
    public int getNombreLignesTraitees() { return nombreLignesTraitees; }
    public void setNombreLignesTraitees(int nombreLignesTraitees) { this.nombreLignesTraitees = nombreLignesTraitees; }
    
    public double getMontantTotal() { return montantTotal; }
    public void setMontantTotal(double montantTotal) { this.montantTotal = montantTotal; }
    
    public User getAgent() { return agent; }
    public void setAgent(User agent) { this.agent = agent; }
}
