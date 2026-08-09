package com.moov.facturation.facturation;

/**
 * Notification envoyée pour une facture
 */
public class NotificationFacture {
    
    // Attributs
    private String id;
    private Canal canal;
    private String destinataire;
    private Statut statut;
    
    // Relations
    private Invoice invoice;
    
    // Getters et Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public Canal getCanal() { return canal; }
    public void setCanal(Canal canal) { this.canal = canal; }
    
    public String getDestinataire() { return destinataire; }
    public void setDestinataire(String destinataire) { this.destinataire = destinataire; }
    
    public Statut getStatut() { return statut; }
    public void setStatut(Statut statut) { this.statut = statut; }
    
    public Invoice getInvoice() { return invoice; }
    public void setInvoice(Invoice invoice) { this.invoice = invoice; }
}
