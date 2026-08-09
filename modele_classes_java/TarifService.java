package com.moov.facturation.catalogue;

/**
 * Tarification d'un service
 */
public class TarifService {
    
    // Attributs
    private String id;
    private String nomOption;
    private double prix;
    
    // Relations
    private Service service;
    
    // Getters et Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getNomOption() { return nomOption; }
    public void setNomOption(String nomOption) { this.nomOption = nomOption; }
    
    public double getPrix() { return prix; }
    public void setPrix(double prix) { this.prix = prix; }
    
    public Service getService() { return service; }
    public void setService(Service service) { this.service = service; }
}
