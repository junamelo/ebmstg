package com.moov.facturation.facturation;

import com.moov.facturation.contrats.Company;
import com.moov.facturation.contrats.Line;
import java.util.Date;
import java.util.List;

/**
 * Facture client (globale ou individuelle)
 */
public class Invoice {
    
    // Attributs
    private String id;
    private String numeroFacture; // unique
    private Date periodeDebut;
    private Date periodeFin;
    private double montantTtc;
    private StatutFacture statut;
    private String fichierPdf;
    
    // Relations
    private Company company;
    private Line line; // nullable pour facture globale
    private List<NotificationFacture> notifications;
    private List<HistoriqueFacturation> historique;
    
    // Méthodes
    public void publier() {
        this.statut = StatutFacture.PUBLIEE;
    }
    
    public void annuler() {
        this.statut = StatutFacture.ANNULEE;
    }
    
    // Getters et Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getNumeroFacture() { return numeroFacture; }
    public void setNumeroFacture(String numeroFacture) { this.numeroFacture = numeroFacture; }
    
    public Date getPeriodeDebut() { return periodeDebut; }
    public void setPeriodeDebut(Date periodeDebut) { this.periodeDebut = periodeDebut; }
    
    public Date getPeriodeFin() { return periodeFin; }
    public void setPeriodeFin(Date periodeFin) { this.periodeFin = periodeFin; }
    
    public double getMontantTtc() { return montantTtc; }
    public void setMontantTtc(double montantTtc) { this.montantTtc = montantTtc; }
    
    public StatutFacture getStatut() { return statut; }
    public void setStatut(StatutFacture statut) { this.statut = statut; }
    
    public String getFichierPdf() { return fichierPdf; }
    public void setFichierPdf(String fichierPdf) { this.fichierPdf = fichierPdf; }
}
